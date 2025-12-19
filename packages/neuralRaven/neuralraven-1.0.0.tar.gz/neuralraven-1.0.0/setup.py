from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
import sys
import subprocess

try:
    import numpy
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy

extensions = [
    Extension(
        name="neuralRaven.core",
        sources=["neuralRaven/core.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++"
    )
]

setup(
    name="neuralRaven",
    version="1.0.0",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    packages=["neuralRaven"],
    package_data={
        "neuralRaven": ["*.pyd", "*.so"],
    },
    install_requires=["numpy", "Cython"],
)