"""Setup project."""

from os.path import join
from setuptools import (
    find_packages,
    setup,
)


INSTALL_REQUIRES = (
    # 'curio @ git+https://github.com/dabeaz/curio.git@master#egg=curio-0.10',
    'pymongo',
    'pytz',
    'pyyaml',
    'pyzmq',
)

SETUP_REQUIRES = (
    'pytest-runner',
    'setuptools-scm',
    'setuptools-scm-git-archive',
)

TESTS_REQUIRE = (
    'autocoverage',
    'flake8',
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


def extras_require(
        install_requires=INSTALL_REQUIRES,
        tests_require=TESTS_REQUIRE):
    """Extras require."""
    result = {
        'adt': (),
        'flowsheet': (),
        'labs': (),
        'med': (),
        'order': (),
    }

    result['all'] = install_requires + tuple(
        value
        for values in result.values()
        for value in values)

    result['test'] = tests_require
    return result


def long_description(file_name='readme.md'):
    """Long description."""
    with open(join(file_name), encoding='utf-8') as desc:
        return desc.read()


setup(
    name='project',
    author='Penn Medicine Predictive Healthcare',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ),
    entry_points={
        'console_scripts': (
            (
                'project = '
                'project:Microservice.run_on_schedule'),
            (
                'project.run_once_now = '
                'project:Microservice.run_once_now'),
        ),
    },
    extras_require=extras_require(),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    long_description=long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRE,
    url='https://github.com/pennsignals/microservice',
    use_scm_version={'write_to': 'src/project/version.py'},
)
