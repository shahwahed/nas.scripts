from setuptools import setup

setup(
    name='netappConfigMaker',
    version='1.5.1',
    author='Shah Mohsin WAHED',
    author_email='shahmohsin.wahed@gmail.com',
    #packages=['netappConfigMaker', 'netappConfigMaker.test'],
    scripts=['netapp.config.maker.py', 'netapp.config.maker.Config.tmpl', 'netapp.config.maker.RC.tmpl',],
    url='http://pypi.python.org/pypi/netappConfigMaker/',
    license='LICENSE.txt',
    description='Netapp 7Mode Configuration generator based on a XML configuration file.',
    long_description=open('README.txt').read(),
    install_requires=[
        "argparse >= 1.2.1",
        "lxml >= 2.3.5",
        "cheetah >= 2.4.4",
    ],
)
