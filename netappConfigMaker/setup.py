from setuptools import setup, find_packages
from sys import version

if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None


version = '1.5.5'

setup(
    name='netappConfigMaker',
    version=version,
    author='Shah Mohsin WAHED',
    author_email='shahmohsin.wahed@gmail.com',
    keywords='netapp 7mode 7M configuration generator script',
    #packages=['netappConfigMaker', 'netappConfigMaker.test'],
    scripts=['netapp.config.maker.py', 'netapp.config.maker.py3','netapp.config.maker.Config.tmpl', 'netapp.config.maker.RC.tmpl', ],
    url='http://pypi.python.org/pypi/netappConfigMaker/',
    license='LICENSE.txt',
    description='Netapp 7Mode Configuration generator based on a XML configuration file.',
    long_description=open('README.txt').read() + '\n' + open('CHANGES.txt').read(),
    classifiers=[
         'Development Status :: 5 - Production/Stable',
         'Environment :: Console',
         'Intended Audience :: System Administrators',
         'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
         'Operating System :: POSIX :: Linux',
         'Operating System :: POSIX',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3',
         'Topic :: System',
         'Topic :: System :: Hardware',
         'Topic :: System :: Installation/Setup',
         'Topic :: System :: Systems Administration',
         'Topic :: Utilities',
    ],
    install_requires=[
        "argparse >= 1.2.1",
        "lxml >= 2.3.5",
        "cheetah >= 2.4.4",
    ],
)
