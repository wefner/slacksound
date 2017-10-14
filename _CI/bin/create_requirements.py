#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
from pipenv.project import Project
from collections import namedtuple

Package = namedtuple('Package', ['name', 'version'])


def get_top_level_dependencies(package_type):
    validate_package_type(package_type)
    _type = 'packages' if package_type == 'default' else 'dev-packages'
    return Project().parsed_pipfile.get(_type, {}).keys()


def get_packages(package_type):
    validate_package_type(package_type)
    packages = json.loads(open('Pipfile.lock', 'r').read())
    return [Package(package_name, data.get('version'))
            for package_name, data in packages.get(package_type).items()]


def validate_package_type(package_type):
    if package_type not in ['default', 'develop']:
        raise ValueError('Invalid type received {}'.format(package_type))


if __name__ == '__main__':
    _type = sys.argv[1].lower()
    top_level_dependencies = get_top_level_dependencies(_type)
    packages = get_packages(_type)
    packages = [package for package in packages
                if package.name in top_level_dependencies]
    ofile = 'requirements.txt' if _type == 'default' else 'dev-requirements.txt'
    with open(ofile, 'w') as f:
        f.write('\n'.join(['{}{}'.format(package.name, package.version)
                           for package in packages]))

