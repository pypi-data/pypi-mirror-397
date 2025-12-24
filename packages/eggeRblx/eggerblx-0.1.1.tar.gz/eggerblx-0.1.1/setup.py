from setuptools import setup, find_packages

setup(
    name="eggeRblx",
    version="0.1.1",
    author="egge",
    author_email="tspmoegge@gmail.com",
    description="Roblox Users API wrapper",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.8",
    license="MIT",
)