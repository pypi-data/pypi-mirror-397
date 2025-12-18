from setuptools import setup, find_packages

setup(
    name="pnw_subscriptions",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
    ],
    python_requires=">=3.8",
    description="Subscription utilities for PNW",
    author="Sumnor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
