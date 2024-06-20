from setuptools import find_packages, setup

setup(
    name='surferai',
    packages=find_packages(),
    version='1.1',
    description='A Python client for the Surfer AI API',
    author='Me',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)