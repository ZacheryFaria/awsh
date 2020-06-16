from setuptools import find_packages, setup

setup(
    name='awsh',
    packages=find_packages(),
    version='1.0.1',
    include_package_data=True,
    install_requires=[
        'wheel',
        'boto3',
        'click'
    ],
    extras_require={'tools': [
        'nose',
        'pylint',
    ]},
    entry_points={
        'console_scripts': ['awsh=awsh.awshell:main']
    },
)