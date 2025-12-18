from setuptools import setup

setup(
    name = "zCtk",
    version = "0.0.0",
    description = "",
    author = "zisia13",
    github = "zisia13",
    author_email = "nothing@nothing.com",
    packages = [
        "zCtk",
        "zCtk.test"
    ],
    install_requires = [
        "tkinter",
        "customtkinter"
        ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)