from setuptools import setup

setup(
    name='netappConfigMaker',
    version='1.1.0',
    author='Shah Mohsin WAHED',
    author_email='shahmohsin.wahed@gmail.com',
    #packages=['netappConfigMaker', 'netappConfigMaker.test'],
    scripts=['netapp.config.maker.py', ],
    url='http://pypi.python.org/pypi/netappConfigMaker/',
    license='LICENSE.txt',
    description='Netapp 7Mode Configuration generator based on a XML configuration file.',
    long_description=open('README.txt').read(),
    install_requires=[
        "argparse >= 1.2.1",
        "lxml >= 2.3.5",
    ],
)
