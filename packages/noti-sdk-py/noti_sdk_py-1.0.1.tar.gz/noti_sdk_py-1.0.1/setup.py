from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="noti-sdk-py",
    version="1.0.1",
    author="Diego Quiroz Ramirez - CEO NotiBuzz Cloud",
    author_email="",
    description="Lightweight Python SDK for WhatsApp messaging and bulk messaging via the Notibuzz Cloud REST API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/notibuzzcloud/noti-sdk-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    include_package_data=True,
)

