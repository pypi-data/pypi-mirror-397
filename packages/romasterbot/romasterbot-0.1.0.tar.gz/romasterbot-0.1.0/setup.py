from setuptools import setup, find_packages

setup(
    name="romasterbot",          # имя твоей библиотеки
    version="0.1.0",
    author="Mitay",
    description="Web messenger bot API library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
)
