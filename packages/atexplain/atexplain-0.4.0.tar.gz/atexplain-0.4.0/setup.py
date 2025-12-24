from setuptools import setup, find_packages

setup(
    name="atexplain",
    version="0.4.0",
    packages=find_packages(),
    install_requires=[],
    description="Библиотека для автоматического объяснения кода Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Митрий",
    license="MIT",
    url="https://github.com/yourusername/atexplain",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

