from setuptools import setup, find_packages

setup(
    name='lstm-deep-learning-project',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A deep learning project using LSTM for time series forecasting.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'pandas',
        'tensorflow',
        'scikit-learn',
        'matplotlib',
        'pyyaml',
        'jupyter'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)