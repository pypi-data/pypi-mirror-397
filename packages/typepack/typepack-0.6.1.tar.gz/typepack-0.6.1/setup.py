"""
Setup script for fastpack C extension.

The C extension is optional - if the build fails (no compiler, etc.),
the package will still work using the pure Python implementation.
"""

import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class BuildExtOptional(build_ext):
    """Build C extensions, but don't fail if compilation is not possible."""

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            print(f"\n*** WARNING: Failed to build C extension: {e}")
            print("*** typepack will use pure Python implementation instead.\n")


# Define the C extension
_typepack_ext = Extension(
    "typepack._typepack",
    sources=["src/_typepack.c"],
    extra_compile_args=["-O3"] if sys.platform != "win32" else ["/O2"],
)


setup(
    ext_modules=[_typepack_ext],
    cmdclass={"build_ext": BuildExtOptional},
)
