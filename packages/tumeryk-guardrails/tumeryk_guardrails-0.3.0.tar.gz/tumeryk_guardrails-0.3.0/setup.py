from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tumeryk_guardrails",
    version="0.3.0",
    author="Tumeryk",
    author_email="support@tumeryk.com",
    description="API Client for Tumeryk Guardrails",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tumeryk.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "python-dotenv>=0.19.0",
        ],
    },
    keywords=["tumeryk", "guardrails", "openai", "llm", "ai-safety", "api-client"],
)
