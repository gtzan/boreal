#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="George Tzanetakis",
    author_email='gtzan@cs.uvic.ca',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Bokeh Reactive Audio Library",
    entry_points={
        'console_scripts': [
            'boreal=boreal.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    package_data={'': ['beatles.wav', 'audio_widgets/description.html']}, 
    keywords='boreal',
    name='boreal',
    packages=find_packages(include=['boreal', 'boreal.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/gtzan/boreal',
    version='0.6.0',
    zip_safe=False,
)
