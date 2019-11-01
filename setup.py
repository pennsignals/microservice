"""Setup project.

Writing version.py allows the service to know its own version from git
    without updating the code.

However, git also knows that the code has been modified
    (version.py has been written), so it always adds
    dev+build hashes to the reported version.

Clearly there is some way to have git ignore the file for scm.
"""

from os.path import join

from setuptools import find_packages, setup

CLASSIFIERS = (
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
)

INSTALL_REQUIRES = (
    "numpy",
    "pandas",
    "pymongo",
    "pymssql",
    "pyyaml",
    "schedule",
)

SETUP_REQUIRES = ("pytest-runner", "setuptools_scm")

TESTS_REQUIRE = (
    "black",
    "flake8",
    "flake8-bugbear",
    "flake8-commas",
    "flake8-comprehensions",
    "flake8-docstrings",
    "flake8-logging-format",
    "flake8-mutable",
    "flake8-sorted-keys",
    "pep8-naming",
    "pylint",
    "pytest",
    "pytest-cov",
    "pytest-flake8",
    "pytest-mock",
    "pytest-pylint",
)


def long_description(file_name="readme.md"):
    """Return long description."""
    with open(join(file_name), encoding="utf-8") as readme:
        return readme.read()


setup(
    name="project",
    author="Penn Medicine Predictive Healthcare",
    classifiers=list(CLASSIFIERS),
    entry_points={
        "console_scripts": (
            "project = project:Service.main",
            "project.ping = project:Service.main_ping",
        )
    },
    extras_require={"tests": TESTS_REQUIRE},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRE,
    url="https://github.com/pennsignals/microservice",
    use_scm_version={"write_to": "src/project/version.py"},
)
