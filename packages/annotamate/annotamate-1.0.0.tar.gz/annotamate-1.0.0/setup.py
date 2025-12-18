from setuptools import setup, find_packages

setup(
    name="annotamate",
    version="1.0.0",
    description="A Python package for image annotation",
    author="Rugved Jalit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rugvedjalit/Annotamate",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "customtkinter",
        "pillow",
        "tkfontawesome"
    ],
    entry_points={
        "console_scripts": [
            "annotamate=annotamate.main:main",
        ],
    },
)
