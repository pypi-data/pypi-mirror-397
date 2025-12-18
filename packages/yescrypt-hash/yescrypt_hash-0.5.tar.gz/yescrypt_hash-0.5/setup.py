from setuptools import setup, Extension

yescrypt_hash_module = Extension(
    "yescrypt_hash",
    sources=[
        "yescryptmodule.c",
        "yescrypthash.c"
    ],
    include_dirs=[".", "yescrypt"],
    # Optional: Add these for optimization
    # define_macros=[("YESCRYPT_STATIC", None)],
    # extra_compile_args=["-O3", "-march=native"],
)

setup(
    ext_modules=[yescrypt_hash_module],
    zip_safe=False,  # Essential for C extensions
)