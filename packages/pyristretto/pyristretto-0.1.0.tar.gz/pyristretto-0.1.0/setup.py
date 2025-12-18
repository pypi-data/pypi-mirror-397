from setuptools import setup, Extension

extra_compile_args = [
    '-std=c11',
    '-O3',
    '-flto',
    '-funroll-loops',
    '-fomit-frame-pointer',
]

extra_link_args = [
    "-static-libgcc",
    "-static-libstdc++",
    "-flto",
]

ext_modules = [
    Extension(
        "pyristretto.pyristretto",
        sources=["pyristretto/pyristretto.c"],
        libraries=["sodium"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "pyristretto.msm",
        sources=["pyristretto/msm.c"],
        libraries=["sodium"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    name="pyristretto",
    version="0.1.0",
    packages=["pyristretto"],
    ext_modules=ext_modules,
    description="Accelerated Ristretto255 primitives for Python, backed by libsodium.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Xylen",
    license="MIT",
)
