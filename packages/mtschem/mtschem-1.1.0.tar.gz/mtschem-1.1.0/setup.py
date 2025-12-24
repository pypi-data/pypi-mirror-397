import sys

from setuptools import setup, find_packages

pip_arg = 'install'
if pip_arg in sys.argv:
    from mtschem.get_from_github import _get_mttools_from_github

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except Exception:
    long_description = "Python library to handle Minetest schematics"

setup(
    name="mtschem",
    version="1.1.0",
    author="roya willing",
    author_email="royawillingroyawillingroyawilling@gmail.com",
    description="Python library to handle Minetest schematics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
    ],
    keywords="minetest, schematic, 3d",
)
