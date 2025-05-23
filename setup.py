from setuptools import setup, find_packages

setup(
    name="scenic",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "websockets",
        "numpy",
        "scipy",
        "pytest",
        "pytest-asyncio",
        "pyzmq"
    ],
    python_requires=">=3.7",
) 