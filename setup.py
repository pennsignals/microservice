"""Setup ventilator model."""

from setuptools import find_packages, setup

TESTS_REQUIRE = [
    'flake8-bugbear',
    'flake8-commas',
    'flake8-comprehensions',
    'flake8-docstrings',
    'flake8-logging-format',
    'flake8-mutable',
    'flake8-sorted-keys',
    'pep8-naming',
    'pylint==1.8.4',  # pytest-pylint 0.9.0 is incompatible w pylint 1.9.x
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-mock',
    'pytest-pylint',
]

setup(
    name='microservice',
    author='Penn Medicine Predictive Healthcare',
    version='0.1',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'microservice = microservice:Microservice.main',
            'input.stream.a = microservice.InputStreamA.main',
            'input.stream.b = microservice.InputStreamB.main',
            'output.stream.a = microservice.OutputStreamA.main',
            'output.stream.b = microservice.OutputStreamB.main',
        ],
    },
    extras_require={
        'tests': TESTS_REQUIRE,
    },
    include_package_data=True,
    install_requires=[
        'curio',
        'numpy',
        'pandas',
        'pymongo',
        'pyyaml',
        'pyzmq',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=TESTS_REQUIRE,
    url='https://github.com/pennsignals/microservice',
    # use_scm_version=True,
)
