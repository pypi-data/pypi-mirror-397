import setuptools
from pathlib import Path

setuptools.setup(
    name="quangpdf",
    version="0.1.0",
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["data", "tests"]),
    author="Quang Huynh Minh",
    author_email="huynhq772@gmail.com",
)
