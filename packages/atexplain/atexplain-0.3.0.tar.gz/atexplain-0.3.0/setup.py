from setuptools import setup, find_packages

setup(
    name="atexplain",
    version="0.3.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    description="Автоматически спрашивает, нужно ли объяснение работы кода",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mitriy",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
