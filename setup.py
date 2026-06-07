"""
setup.py - SoilGuard Portal Package Configuration

Enables installation via 'pip install .' or 'pip install -e .'
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="soilguard-portal",
    version="0.1.0",
    author="Coastal Alpine Tech Limited",
    author_email="info@coastalalpine.co.nz",
    description="Autonomous on-premise soil quality monitoring and agricultural control system with edge AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fivepanelhat/SoilGuard-Portal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "soilguard-portal=main:main",
        ],
    },
    keywords="soil-quality agriculture IoT edge-ai crops compliance",
    include_package_data=True,
)
