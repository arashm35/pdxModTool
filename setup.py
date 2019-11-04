from setuptools import setup

from pdxModTool import version

setup(
    entry_points={
        'console_scripts': [
            'pdxModTool=pdxModTool.__main__:main',  # command=package.module:function
        ],
    },
    name='pdxModTool',
    version=version,
    packages=['pdxModTool'],
    url='',
    license='',
    author='Arash',
    author_email='',
    description='paradox mod tool', install_requires=['tqdm']
)
