from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="s3-toolkit",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A robust Python package for AWS S3 data integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sivaramanlatchapathi/s3-toolkit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "boto3>=1.26.0",
        "pandas>=1.5.0",
        "pyarrow>=10.0.0",
        "python-dotenv>=0.19.0",
        "tqdm>=4.64.0",
        "pydantic>=1.10.0",
        "smart-open>=6.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.5b2",
            "isort>=5.8.0",
            "mypy>=0.910",
            "types-python-dateutil>=2.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "s3toolkit=s3_toolkit.cli:main",
        ],
    },
)
