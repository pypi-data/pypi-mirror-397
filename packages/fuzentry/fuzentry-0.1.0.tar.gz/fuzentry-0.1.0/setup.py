from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fuzentry",
    version="0.1.0",
    author="Fuzentry",
    author_email="support@fuzentry.com",
    description="Official Python SDK for Fuzentry AI AgentOS PaaS Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuzentry/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/fuzentry/python-sdk/issues",
        "Documentation": "https://docs.fuzentry.com",
        "Source Code": "https://github.com/fuzentry/python-sdk",
        "AWS Marketplace": "https://aws.amazon.com/marketplace/pp/prodview-fuzentry",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "mypy>=1.5.0",
            "flake8>=6.1.0",
        ],
    },
    keywords="ai agents llm orchestration aws-marketplace saas sdk fuzentry",
    license="Proprietary",
    license_files=["LICENSE"],
)
