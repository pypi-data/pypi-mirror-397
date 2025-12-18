import pathlib
from setuptools import setup
import re

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

PACKAGE_NAME = "opentele-py313"
VERSION = "1.15.2"
SOURCE_DIRECTORY = "src"

requirements = [
    "pyqt5",
    "telethon",
    "tgcrypto",
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    license="MIT",
    description="A Python 3.13+ compatible fork of opentele - Telegram API Library for converting between tdata and telethon sessions.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/opentele-py313",
    author="Aleksey (fork maintainer)",
    author_email="your.email@example.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 5 - Production/Stable",
    ],
    keywords=[
        "tdata",
        "tdesktop",
        "telegram",
        "telethon",
        "opentele",
        "python313",
    ],
    include_package_data=True,
    packages=["opentele", "opentele.td", "opentele.tl"],
    package_dir={"opentele": SOURCE_DIRECTORY},
    install_requires=requirements,
)
