from setuptools import setup, find_packages

setup(
    name="pnw_subscriptions",
    version="0.2.4",
    packages=find_packages(),
    include_package_data=True,
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
