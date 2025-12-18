from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="py-osrm-backend",
    version="0.1.0",
    description="A Python implementation of OSRM backend core functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GalTechDev",
    url="https://github.com/GalTechDev/py-osrm-backend",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "flask",  # For the API server
        "osmium",  # For PBF parsing
    ],
    extras_require={
        "dev": [
            "pytest",
            "build",
            "twine",
        ],
    },
    keywords=["osrm", "routing", "osm", "openstreetmap", "dijkstra", "navigation"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
