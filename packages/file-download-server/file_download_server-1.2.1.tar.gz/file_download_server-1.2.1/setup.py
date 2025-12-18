from setuptools import setup, find_packages
import platform
from pathlib import Path

# 读取 README.md 作为长描述
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

python_version = int("".join(platform.python_version().split(".")[:2]))

setup(
    name="file_download_server",
    version="1.2.1",
    packages=find_packages(),
    author="Ricardo",
    author_email="GeekRicardozzZ@gmail.com",
    url="https://github.com/GeekRicardo/file-download-server",
    description="A simple file server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "fastapi",
        "python-multipart",
        "uvicorn~=" + ("0.16.0" if python_version == 36 else "0.17.0"),
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
