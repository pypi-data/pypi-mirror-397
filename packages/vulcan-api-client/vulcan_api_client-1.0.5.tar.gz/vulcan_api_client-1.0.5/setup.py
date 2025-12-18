from setuptools import setup, find_packages

setup(
    name="vulcan-api-client",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        "requests",
        "selenium",
    ],
    author="Jake",
    author_email="jakub201307@gmail.com",
    description="Full-featured Vulcan API"
)
