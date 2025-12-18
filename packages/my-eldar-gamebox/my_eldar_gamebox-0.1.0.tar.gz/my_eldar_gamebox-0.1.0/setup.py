from setuptools import setup, find_packages

setup(
    name="my_eldar_gamebox",
    version="0.1.0",
    author="Eldar",
    author_email="eldaraliyev675@gmail.com",
    description="Collection of fun terminal games for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
