from setuptools import setup, find_packages

setup(
    name="autexplain",
    version="0.1.0",
    packages=find_packages(),
    description="Автоматически спрашивает объяснение кода при завершении программы",
    python_requires=">=3.7",
)