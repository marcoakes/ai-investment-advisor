"""
Setup script for AI Investment Research Assistant
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-investment-advisor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A sophisticated AI investment research assistant with CLI interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcoakes/ai-investment-advisor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "investment-advisor=investment_advisor.cli:main",
        ],
    },
    keywords="investment, finance, ai, analysis, stocks, trading, backtesting",
    project_urls={
        "Bug Reports": "https://github.com/marcoakes/ai-investment-advisor/issues",
        "Source": "https://github.com/marcoakes/ai-investment-advisor",
        "Documentation": "https://github.com/marcoakes/ai-investment-advisor#readme",
    },
)