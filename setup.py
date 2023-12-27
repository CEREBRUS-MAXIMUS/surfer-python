from setuptools import find_packages, setup

setup(
    name='spookyai',
    packages=find_packages(include=['spookyai']),
    version='0.1.1',
    description='The official Python library for the Spooky HumanAPI',
    author='Jack Blair',
    install_requires=['asyncio', 'requests', 'langchain'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)