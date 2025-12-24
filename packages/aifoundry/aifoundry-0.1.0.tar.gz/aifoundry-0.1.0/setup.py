from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aifoundry",
    version="0.1.0",
    author="AI Foundry Team",
    author_email="your-email@example.com",
    description="Enterprise-grade AI implementation tools with built-in compliance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LOLA0786/Aifoundary",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=[],
)
