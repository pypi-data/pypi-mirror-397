
from setuptools import setup, find_packages
from setuptools.command.install import install

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="py-ankiconnect",
    version="1.1.4",
    description="Minimal wrapper to simplify the usage of the awesome ankiconnect anki addon.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiswillbeyourgithub/py_ankiconnect",
    packages=find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords=["anki", "flashcards", "ankiconnect", "learning", "cli", "tool", "spaced", "repetition", "ebbinghaus", "addon"],
    python_requires=">=3.9",

    entry_points={
        'console_scripts': [
            'py_ankiconnect=py_ankiconnect.__init__:cli_launcher',
        ],
    },

    install_requires=[
        "fire >= 0.6.0",
        "aiohttp",
    ],

    extras_require={
        'rich': ['rich'],
    },
)
