# License MIT
import os
from setuptools import setup, find_packages

DISTRO_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def extract_requirements(file):
    """
    Extracts requirements from requirements file

    :param file: path to requirements file
    :type file: str
    :return: list[str] -- list of requirements
    """

    with open(file, 'r') as file:
        return file.read().splitlines()


setup(
    name='supertool-distro',
    version='0.1',
    description='super-tool is a set of tools created for training purposes within the epam course.',
    long_description=open(os.path.join(DISTRO_ROOT_PATH, '..', 'README.md')).read(),
    author='Andrey Gavrilov',
    author_email='ag239@yandex.ru',
    license='MIT',
    classifiers=[
        'Topic :: Education',
        'Programming language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=extract_requirements(os.path.join(DISTRO_ROOT_PATH,
                                                       'requirements', 'base.txt')),
    tests_require=extract_requirements(os.path.join(DISTRO_ROOT_PATH,
                                                    'requirements', 'test.txt')),
    test_suite='nose.collector',
    scripts=[os.path.join('bin', 'similar_files'),
             os.path.join('bin', 'weather_forecast'),
             os.path.join('bin', 'weather_forecast_by_coords')]
)
