from setuptools import setup, find_packages

setup(
    name="aegis-recon",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "httpx",
        "sqlalchemy",
        "aiosqlite",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "aegis=aegis.cli:app",
        ],
    },
)
