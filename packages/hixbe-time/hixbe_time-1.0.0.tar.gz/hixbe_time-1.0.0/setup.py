"""Setup script for hixbe-time package"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hixbe-time",
    version="1.0.0",
    author="Hixbe",
    author_email="info@hixbe.com",
    description="High-precision NTP time synchronization package with CLI tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hixbehq/python-time",
    project_urls={
        "Bug Tracker": "https://github.com/hixbehq/python-time/issues",
        "Repository": "https://github.com/hixbehq/python-time",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Time Synchronization",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "hixbe-time=hixbe_time.cli:main",
        ],
    },
    keywords=[
        "ntp",
        "network-time-protocol",
        "time",
        "synchronization",
        "time-server",
        "hixbe",
    ],
)
