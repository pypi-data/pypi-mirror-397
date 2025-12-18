from setuptools import setup

# This is a pure Python package - no C extensions
setup(
    use_scm_version={"version_scheme": "guess-next-dev", "local_scheme": "dirty-tag"},
    setup_requires=["setuptools >= 61", "setuptools_scm >= 6.4"],
)
