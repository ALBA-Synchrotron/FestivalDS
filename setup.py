#!/usr/bin/env python

from setuptools import setup

# The version is updated automatically with bumpversion
# Do not update manually
__version = '1.0.0'


def main():

    setup(
        name='tangods-festival',
        version=__version,
        package_dir={'tangods-festival': 'src'},
        packages=['tangods-festival'],
        include_package_data=True,  # include files in MANIFEST
        author='ALBA Synchrotron computing group',
        author_email='computing@cells.es',
        description='Text to speech tango device server using festival',
        license='GPLv3+',
        platforms=['src', 'noarch'],
        url='https://github.com/ALBA-Synchrotron/FestivalDS',
        requires=['tango (>=7.2.6)'],
        entry_points={
            'console_scripts': [
                'FestivalDS = src.FestivalDS:main',
            ],
        },
    )


if __name__ == "__main__":
    main()
