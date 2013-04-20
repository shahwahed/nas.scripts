Netapp 7M configuration generator
=================================

Tags: Netapp, Configuration, XML

Version history: 1.0

License: GPLv3

License URL: http://www.gnu.org/licenses/gpl-3.0.html

Licence
=======

    Copyright (C) 2012, 2013  Shah Mohsin WAHED

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
	

Description
===========

 
This script will create configuration file (".config" and ".rc") for Netapp NAS filer using Data Ontap in 7M (seven mode) based on a XML configuration file.
Making it simpler to create standard and quick configs.

Project link : http://shah.nas.scripting.cloudcorner.net


Requirements / Pre-requisites
=============================

This script require:

    1. Python 2.X run on a Linux server, haven't test on windows
    2. few python libs (lxml, argparse)
    3. of course a Netapp appliance running DataOntap in 7M (work also with Netapp simulator or Netapp Edge) to test or apply your configuration.

usage
=====
from a linux server  just run:

        #shell> netapp.config.maker.py -c configfile.xml

This will generate two file <hostname>.config <hostname>.rc with hostname extract from the xml file

Quick help
----------

        usage: netapp.config.maker.py [-h] -c configfile [-v]

        optional arguments:
            -h, --help show this help message and exit

            -c configfile, --configfile configfile XML config file

            -v, --vfiler vfiler config generator only



XML Configuration file
----------------------

see the ConfigExample file in ./docs for more information.


.config layout
--------------

The .config file have the following layout:

Ifgroup Configuration
Vlan Configuration
General Options
Ipspaces Configuration
Interfaces Configuration
Global Routes
vFilers Configuration
        
.rc layout
----------

The .rc file have the following layout:

Basic Configuration
Ifgroup Configuration
Vlan Configuration
Interfaces Configuration
Global Routes
vFilers Configuration


Authors and Contributors
========================

Author: `Shah Mohsin WAHED <mailto:shahmohsin.wahed@gmail.com>`_ | `Linkedin Profile <http://www.linkedin.com/pub/shah-mohsin-wahed/1a/750/18a>`_

Thanks to David Rousseau and Timo Sugliani for encouraging me to publish my work on github and pypi :)

Support
=======

Having trouble with this scripts, think about an evolution ? Contact me!
