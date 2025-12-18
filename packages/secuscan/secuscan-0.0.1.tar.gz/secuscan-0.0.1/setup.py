from setuptools import setup, find_packages

setup(
    name="secuscan",  # The name you want to reserve
    version="0.0.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Placeholder for SecuScan name reservation",
    long_description="This is a reserved package name.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
