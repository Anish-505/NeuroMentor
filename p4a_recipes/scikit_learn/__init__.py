"""
python-for-android recipe for scikit-learn on Android ARM.

scikit-learn has C/Cython extensions that cannot be installed via
standard pip on Android.  This recipe builds from source using
the cross-compilation toolchain provided by python-for-android.

Place this file at:
  p4a_recipes/scikit_learn/__init__.py
"""
from pythonforandroid.recipe import PythonRecipe


class ScikitLearnRecipe(PythonRecipe):
    """Build scikit-learn from source for Android ARM targets."""

    name = 'scikit_learn'
    version = '1.2.2'
    url = 'https://pypi.io/packages/source/s/scikit-learn/scikit-learn-{version}.tar.gz'

    depends = ['numpy', 'scipy', 'cython', 'setuptools', 'joblib']

    # Build via pip from source
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # Disable OpenMP (not available on Android NDK by default)
        env['SKLEARN_NO_OPENMP'] = '1'
        # Ensure numpy headers are found
        numpy_recipe = self.get_recipe('numpy', self.ctx)
        numpy_include = numpy_recipe.get_include_dir(arch)
        if numpy_include:
            env['CFLAGS'] = env.get('CFLAGS', '') + f' -I{numpy_include}'
            env['CXXFLAGS'] = env.get('CXXFLAGS', '') + f' -I{numpy_include}'
        return env

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        """Install using pip with --no-build-isolation to use already-built
        numpy and scipy from python-for-android."""
        env = env or self.get_recipe_env(arch)
        self.install_hostpython_prerequisites()
        self.run_pymodules_install(
            arch,
            ['scikit-learn=={}'.format(self.version)],
            env=env,
            extra_args=['--no-build-isolation'],
        )


recipe = ScikitLearnRecipe()
