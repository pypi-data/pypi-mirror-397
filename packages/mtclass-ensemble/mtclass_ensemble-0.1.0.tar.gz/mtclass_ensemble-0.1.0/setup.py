from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mtclass_ensemble',
    version='0.1.0',
    url='https://github.com/ronnieli0114/MTClass',
    author='Ronnie Li',
    author_email='ronnieli0114@gmail.com',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    description='MTClass ensemble algorithm for identifying multi-phenotype cis-eQTLs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=["scikit-learn>=1.5.2",
                      "pandas>=2.2.1",
                      "numpy>=1.26.4",
                      "pyarrow>=17.0.0"],
    extras_require={"dev": ["twine>=6.0.1"]},
    python_requires='>=3.12',
)