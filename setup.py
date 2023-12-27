from setuptools import find_packages, setup

setup(
    name='spookyai',
    packages=find_packages(include=['spookyai']),
    version='0.1.0',
    description='My first Python library',
    author='Jack Blair',
    install_requires=['asyncio', 'requests', 'langchain'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)