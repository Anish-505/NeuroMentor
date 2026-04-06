"""
Random Forest Classifier for EEG-based mental state classification.
Wraps a pre-trained scikit-learn RandomForestClassifier with EEG band power features.

The pre-trained model expects 11 features:
  Delta, Theta, Alpha, Beta, Gamma,
  beta_alpha, alpha_theta, beta_theta, gamma_beta,
  beta_minus_alpha, alpha_plus_theta

Labels: Baseline=0, Focused=1, Stressed=2  (from LabelEncoder)
"""
import os
from dataclasses import dataclass

try:
    import joblib
    import numpy as np
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False


@dataclass
class EegBands:
    """EEG frequency band power values from a single FFT window."""
    delta: float = 0.0
    theta: float = 0.0
    alpha: float = 0.0
    beta: float = 0.0
    gamma: float = 0.0


FEATURE_NAMES = [
    'Delta', 'Theta', 'Alpha', 'Beta', 'Gamma',
    'beta_alpha', 'alpha_theta',
    'beta_theta', 'gamma_beta',
    'beta_minus_alpha', 'alpha_plus_theta',
]


class RFClassifier:
    """Random Forest classifier for EEG mental state prediction.

    Classifies EEG band power features into three states:
      Baseline (Calm), Stressed, Focused

    Uses an 11-feature vector extracted from EegBands objects,
    matching the training script's feature engineering.
    """

    def __init__(self):
        self._clf = None          # RandomForestClassifier
        self._scaler = None       # StandardScaler
        self._encoder = None      # LabelEncoder
        self._is_trained: bool = False
        self._feature_names: list = list(FEATURE_NAMES)

    # ----------------------------------------------------------
    # Feature extraction — matches training script exactly
    # ----------------------------------------------------------

    def build_feature_vector(self, bands: EegBands) -> list:
        """Extract all 11 features from an EegBands object.

        Feature engineering matches rf_model_training.py:
          5 raw bands + 4 ratios + 2 arithmetic combinations

        Returns:
            list of 11 floats
        """
        d, t, a, b, g = bands.delta, bands.theta, bands.alpha, bands.beta, bands.gamma

        beta_alpha = b / (a + 1e-6)
        alpha_theta = a / (t + 1e-6)
        beta_theta = b / (t + 1e-6)
        gamma_beta = g / (b + 1e-6)
        beta_minus_alpha = b - a
        alpha_plus_theta = a + t

        return [
            d, t, a, b, g,
            beta_alpha, alpha_theta,
            beta_theta, gamma_beta,
            beta_minus_alpha, alpha_plus_theta,
        ]

    # ----------------------------------------------------------
    # Training (for future re-training from app)
    # ----------------------------------------------------------

    def train(self, session_bands: list, session_labels: list) -> dict:
        """Train the Random Forest on labelled EEG sessions.

        Args:
            session_bands: list of EegBands objects
            session_labels: list of string labels ('Baseline', 'Stressed', 'Focused')

        Returns:
            dict with training metrics
        """
        if not _HAS_SKLEARN:
            raise RuntimeError("scikit-learn / joblib is not installed")

        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.model_selection import cross_val_score, train_test_split

        # Build feature matrix
        X = np.array([self.build_feature_vector(b) for b in session_bands])
        y = np.array(session_labels)

        # Encode labels
        self._encoder = LabelEncoder()
        y_encoded = self._encoder.fit_transform(y)

        # Fit scaler
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        # Cross-validation
        clf_cv = RandomForestClassifier(
            n_estimators=700, max_depth=None, min_samples_split=3,
            min_samples_leaf=1, random_state=42, n_jobs=-1,
        )
        cv_scores = cross_val_score(clf_cv, X_scaled, y_encoded, cv=5, scoring='accuracy')

        # Final training
        self._clf = RandomForestClassifier(
            n_estimators=700, max_depth=None, min_samples_split=3,
            min_samples_leaf=1, random_state=42, n_jobs=-1,
        )
        self._clf.fit(X_scaled, y_encoded)
        self._is_trained = True

        # Class distribution
        unique, counts = np.unique(y, return_counts=True)
        class_dist = {str(u): int(c) for u, c in zip(unique, counts)}

        return {
            'cv_accuracy': float(np.mean(cv_scores)),
            'cv_std': float(np.std(cv_scores)),
            'feature_importances': dict(zip(self._feature_names, self._clf.feature_importances_.tolist())),
            'n_samples': len(y),
            'class_distribution': class_dist,
        }

    # ----------------------------------------------------------
    # Prediction
    # ----------------------------------------------------------

    def predict(self, bands: EegBands) -> str:
        """Predict mental state label from a single EEG window.

        Returns:
            str label ('Baseline', 'Stressed', 'Focused') or 'Unknown'
        """
        if not self._is_trained or self._clf is None or self._scaler is None:
            return 'Unknown'

        fv = self.build_feature_vector(bands)
        if _HAS_SKLEARN:
            X = np.array([fv])
            X_scaled = self._scaler.transform(X)
            pred = self._clf.predict(X_scaled)[0]
            if self._encoder is not None:
                return str(self._encoder.inverse_transform([pred])[0])
            return str(pred)
        return 'Unknown'

    def predict_proba(self, bands: EegBands) -> dict:
        """Predict class probabilities from a single EEG window.

        Returns:
            dict e.g. {'Baseline': 0.7, 'Stressed': 0.1, 'Focused': 0.2}
        """
        if not self._is_trained or self._clf is None or self._scaler is None:
            return {}

        fv = self.build_feature_vector(bands)
        if _HAS_SKLEARN:
            X = np.array([fv])
            X_scaled = self._scaler.transform(X)
            proba = self._clf.predict_proba(X_scaled)[0]
            if self._encoder is not None:
                labels = self._encoder.inverse_transform(range(len(proba)))
                return {str(l): float(p) for l, p in zip(labels, proba)}
            return {str(i): float(p) for i, p in enumerate(proba)}
        return {}

    # ----------------------------------------------------------
    # Persistence — uses joblib (matches training script)
    # ----------------------------------------------------------

    def save(self, dirpath: str):
        """Save trained model, scaler, and encoder to directory via joblib."""
        if not _HAS_SKLEARN:
            raise RuntimeError("joblib is not installed")
        os.makedirs(dirpath, exist_ok=True)
        joblib.dump(self._clf, os.path.join(dirpath, 'rf_eeg_model.pkl'))
        joblib.dump(self._scaler, os.path.join(dirpath, 'rf_scaler.pkl'))
        if self._encoder is not None:
            joblib.dump(self._encoder, os.path.join(dirpath, 'rf_encoder.pkl'))

    def load(self, dirpath: str) -> bool:
        """Load model, scaler, and encoder from a directory of joblib pkl files.

        Expects:
          dirpath/rf_eeg_model.pkl
          dirpath/rf_scaler.pkl
          dirpath/rf_encoder.pkl

        Returns:
            True if loaded successfully.
        """
        if not _HAS_SKLEARN:
            print("[RFClassifier] joblib/numpy not available — cannot load model")
            return False

        model_path = os.path.join(dirpath, 'rf_eeg_model.pkl')
        scaler_path = os.path.join(dirpath, 'rf_scaler.pkl')
        encoder_path = os.path.join(dirpath, 'rf_encoder.pkl')

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            print(f"[RFClassifier] Model files not found in {dirpath}")
            return False

        try:
            self._clf = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)
            if os.path.exists(encoder_path):
                self._encoder = joblib.load(encoder_path)
            self._is_trained = True
            print(f"[RFClassifier] Model loaded successfully from {dirpath}")
            return True
        except Exception as e:
            print(f"[RFClassifier] Failed to load model: {e}")
            self._is_trained = False
            return False

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------

    @property
    def is_trained(self) -> bool:
        return self._is_trained
