"""Setup microservice."""

from datetime import date
from os.path import (
    exists,
    join,
)
from setuptools import (
    find_packages,
    setup,
)

TESTS_REQUIRE = (
    'flake8-bugbear',
    'flake8-commas',
    'flake8-comprehensions',
    'flake8-docstrings',
    'flake8-logging-format',
    'flake8-mutable',
    'flake8-sorted-keys',
    'pep8-naming',
    'pylint',
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-mock',
    'pytest-pylint',
)


def get_long_description(file_name='readme.md'):
    """Get long description."""
    with open(join(file_name), encoding='utf-8') as f:
        return f.read()


setup(
    name='microservice',
    author='Penn Medicine Predictive Healthcare',
    version='1.0',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ),
    entry_points={
        'console_scripts': (
            'microservice = microservice:Microservice.main',
            'microservice.job = microservice:Microservice.job',
        ),
    },
    extras_require={
        'tests': TESTS_REQUIRE,
    },
    include_package_data=True,
    install_requires=(
        'numpy',
        'pandas',
        'pymongo',
        'pymssql',
        'pyyaml',
        'schedule',
    ),
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'tests.*')),
    python_requires='>=3.7',
    setup_requires=('pytest-runner', 'setuptools_scm'),
    tests_require=TESTS_REQUIRE,
    url='https://github.com/pennsignals/microservice',
    # use_scm_version=True
)
