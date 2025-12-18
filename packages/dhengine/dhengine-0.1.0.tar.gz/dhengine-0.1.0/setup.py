from setuptools import setup, find_packages

setup(
    name="dhengine",
    version="0.1.0",
    author="Ayaan Dhalait",
    description="DhEngine: Lightweight Python game engine built on pygame",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pygame>=2.6.1"
    ],
classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Games/Entertainment",
    "Topic :: Software Development :: Libraries",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

)
