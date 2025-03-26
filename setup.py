from setuptools import setup, find_packages

setup(
    name="webscraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",
    ],
    entry_points={
        "console_scripts": [
            "webscraper=src.scraper:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive web scraper for extracting various types of information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/webscraper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 