from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bugpilot-cli",
    version="1.0.7",
    author="LAKSHMIKANTHAN K",
    author_email="letchupkt@example.com",
    description="AI-powered penetration testing and bug hunting CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/letchupkt/bugpilot-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.7.0",
        "click>=8.1.7",
        "google-generativeai>=0.3.0",
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "groq>=0.4.0",
        "requests>=2.31.0",
        "prompt-toolkit>=3.0.43",
        "pyfiglet>=1.0.2",
        "colorama>=0.4.6",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.5.0",
        "pydantic>=2.5.0",
        "PyYAML>=6.0.1",
        "asyncio>=3.4.3",
    ],
    entry_points={
        "console_scripts": [
            "bugpilot=bugpilot.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bugpilot": ["templates/*", "payloads/*"],
    },
)
