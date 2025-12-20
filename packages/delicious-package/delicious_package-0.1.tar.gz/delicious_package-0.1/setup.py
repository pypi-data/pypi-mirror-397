from setuptools import setup, find_packages
setup(
    name="delicious_package",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author="Kenmo",
    author_email="your.email@example.com",
    description="A simple delicious package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/kento0614/delicious_package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',)