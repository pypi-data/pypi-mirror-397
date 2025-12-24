import setuptools
from pathlib import Path

long_desc = Path("README.md").read_text(encoding="utf-8")
setuptools.setup(
    name="kson2toml",
    version="1.0.5",
    author="Matias Barrios",
    author_email="matias@barrioslira.com",
    description="KSON to TOML converter",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    packages=["kson2toml"],
    py_modules=["app"],
    install_requires=[
        "kson-lang",
        "toml"
    ],
    entry_points={
        "console_scripts": [
            "kson2toml=app:main",
        ],
    }
)