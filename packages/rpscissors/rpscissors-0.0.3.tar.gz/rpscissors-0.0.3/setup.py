from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rpscissors",
    version="0.0.3",
    description="A Rock Paper Scissors game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Iven Boxem",
    author_email="boxemivenruben@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="rock paper scissors game",
    packages=find_packages(),
    python_requires=">=3.8",
)
