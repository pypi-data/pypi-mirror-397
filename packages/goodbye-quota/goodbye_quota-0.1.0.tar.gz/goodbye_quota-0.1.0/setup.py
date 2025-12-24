from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="goodbye_quota",
    version="0.1.0",
    description="A wrapper for Gemini API to handle multiple API keys and rotate them on quota exhaustion.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@cmpdchtr",
    author_email="cmpdchtr@example.com",
    url="https://github.com/cmpdchtr/GoodbyeQuota",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)