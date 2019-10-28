from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'pdxModTool=pdxModTool.main:main',  # command=package.module:function
        ],
    },
    name='pdxModTool',
    version='0.94',
    packages=['pdxModTool'],
    url='',
    license='',
    author='Arash',
    author_email='',
    description='paradox mod tool'
)
