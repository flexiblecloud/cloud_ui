#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def process_requirement(requirement):
    if requirement.startswith("git+"):
        dep_name = requirement.rpartition("@")[0].partition("/")[2]
        return f"{dep_name}@{requirement}"
    return requirement


requirements = [process_requirement(requirement) for requirement in requirements]


setup(
    name='cloudui',
    version='0.0.1',
    description='Python trio and remi based library for making web-apps ...',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/flexiblecloud/cloud_ui',
    download_url='https://github.com/flexiblecloud/cloud_ui/archive/master.zip',
    keywords=['gui-library', 'remi', 'trio', 'service', 'application', 'platform-independent', 'ui', 'gui'],
    author='Andriy Vasyltsiv',
    author_email='andriyvasyltsiv@gmail.com',
    license='BSD',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=requirements
)
