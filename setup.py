from setuptools import find_packages, setup

setup(
    name='awsh',
    packages=find_packages(),
    version='1.0.0',
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
        'console_scripts': ['awshpy=awsh.awshell:main']
    },
    scripts=['scripts/awsh', 'scripts/awsh.ps1']
)