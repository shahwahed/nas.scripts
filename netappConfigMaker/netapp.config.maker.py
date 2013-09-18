#!/usr/bin/python
#-*-coding: utf8 -*


"""Python netapp.config.maker.py
Script generate custom netapp filer .config and .rc based on XML config file
"""
__author__ = "Shah Mohsin WAHED <s.wahed@laposte.net>"
__copyright__ = "Copyright (c) 2013 S.WAHED"
__license__ = "GPL"
__version__ = "1.5.4"
__cvsversion__ = "$Revision: $"
__date__ = "$Date: $"


"""
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
"""

import argparse
from lxml import etree
import os
from Cheetah.Template import Template
import re
import datetime


# Configuration variable
#

# path to template
tmplPath = "/usr/local/bin/"

# aggregate for vfiler root volume
aggrVfilerRoot = "RP_NL2_01_etc"

# this part contain all netapp command use python 2.x % vars to fill command
# command format :
# netapp command line with $(variable) for each variable you want to fill in
#
ifGroupConfigCSS = "ifgrp create %(lagType)s %(ifgroupename)s -b %(lbmode)s %(port)s \n"
ifGroupConfigSingleCSS = "ifgrp create %(lagType)s %(ifgroupename)s %(port)s \n"
vlanConfigCSS = "vlan create %(ifgroupename)s %(vlanlist)s \n"
ipspacesConfigCSS = "ipspace create %(ipspaceName)s %(ipspaceInterfaces)s \n"
interfacesConfigCSS = "ifconfig %(interfaceName)s %(interfaceHostname)s netmask %(interfaceNetmask)s mtusize %(interfaceMtu)s partner %(interfaceName)s \n"
globalRouteCSS = "route add %(routeType)s %(routeToAdd)s %(routeMetric)s \n"
vFilerVolCreateCSS = "vol create %(vFilerShortName)s_vol_root -s volume " + aggrVfilerRoot + " 300M \n"
vFilerCreateCSS = "vfiler create %(vFilerFullName)s -n -s %(ipspaceName)s %(vFilerIpList)s /vol/%(vFilerShortName)s_vol_root \n"
vFilerDisallowProtoCSS = "vfiler disallow %(vFilerFullName)s proto=ssh proto=rsh proto=iscsi proto=ftp \n"
vFilerRouteAddCSS = "vfiler run %(vFilerFullName)s route add %(vFilerRouteType)s %(vFilerInterfaceRoute)s  %(vFilerRouteMetric)s\n"


# function to return filer hostname from xml config
def HostNameConfig():
    HostnameFiler = rootTreeFiler.xpath('//hostname/text()')[0].strip()
    return HostnameFiler


# we setup basic configuration here
def BasicConfig():
    ConfigFileHostname = "hostname " + HostnameFiler + "\n"
    return ConfigFileHostname


# general options we set up in our configuration
def optionsGeneral():
    partnerAddress = rootTreeFiler.xpath('//partnerAddress/text()')[0].strip()
    optionsGeneralTxt = ""
    optionsGeneralTxt += "options licensed_feature.multistore.enable on \n"
    optionsGeneralTxt += "options cf.giveback.auto.cancel.on_network_failure on \n"
    optionsGeneralTxt += "options cf.takeover.on_reboot on \n"
    optionsGeneralTxt += "options cf.hw_assist.partner.address " + partnerAddress + "\n"
    optionsGeneralTxt += "options cf.hw_assist.enable on  \n"
    return optionsGeneralTxt


# generate ifgroup configuration
def ifGroupConfig():
    ifGroupConfigTxt = ""
    # we cycle in ifgroups xml part and get interface name and bind it to physical port
    # then make config command using the ifGroupConfigCSS
    for ifgroups in rootTreeFiler.xpath('//ifgroups'):
        for ifgroup in ifgroups:
            ifgroupename = ifgroup.get('name') + "-" + "e" + re.sub('e', '', ifgroup.find('port').text.replace(' ', ''))
            port = ifgroup.find('port').text
            lagType = ifgroup.find('type').text
            lbmode = ifgroup.find('lb').text
            if lagType == "single":
                ifGroupConfigTxt += ifGroupConfigSingleCSS % vars()
            else:
                ifGroupConfigTxt += ifGroupConfigCSS % vars()
    return ifGroupConfigTxt


# generate vlan config
def vlanConfig():
    vlanConfigTxt = ""
    # cylcle on xml part with the ifgroupname short name (vm1 for exemple) we could find the correct port
    for ifgroups in rootTreeFiler.xpath('//ifgroups'):
        for ifgroup in ifgroups:
            ifgroupename = ifgroup.get('name') + "-" + "e" + re.sub('e', '', ifgroup.find('port').text.replace(' ', ''))
            vlanlist = ifgroup.find('vlans').text.strip()
            vlanConfigTxt += vlanConfigCSS % vars()
    return vlanConfigTxt


# generate ipspace definition
def ipspacesConfig():
    ipspacesConfigTxt = ""
    for ipspaces in rootTreeFiler.xpath('ipspaces'):
        for ipspace in ipspaces:
            ipspaceName = ipspace.get('name')
            ipspaceInterfaces = ipspace.find('interfaces').text.strip()
            ipspacesConfigTxt += ipspacesConfigCSS % vars()
    return ipspacesConfigTxt


# generate interface configuration use for vfiler0 configuration
def interfacesConfig():
    interfacesConfigTxt = ""
    for interfaces in rootTreeFiler.xpath('//interfaces'):
        for interface in interfaces:
            interfaceHostname = interface.get('hostname')
            interfaceName = interface.find('int').text.strip()
            interfaceNetmask = interface.find('netmask').text.strip()
            interfaceMtu = interface.find('mtu').text.strip()
            xpathsearchtext = '//ifgroups//ifgroup[@name="' + interfaceName + '"]'
            for ifgroup in rootTreeFiler.xpath(xpathsearchtext):
                interfaceName = ifgroup.get('name') + "-" + "e" + re.sub('e', '', ifgroup.find('port').text.replace(' ', '')) + "-" + interface.find('vlan').text.strip()
            interfacesConfigTxt += interfacesConfigCSS % vars()
    return interfacesConfigTxt


# generate vfiler configuration
# configure also vfiler interfaces all in once route also
def vFilersConfig():
    vFilersConfigTxt = ""
    for vFilers in rootTreeFiler.xpath('//vfilers'):
        for vFiler in vFilers:
            vFilerIpList = ""
            vFilerInterfacesConfig = ""
            vFilerRoutesConfig = ""

            vFilerFullName = vFiler.get('name')
            vFilerShortName = vFilerFullName.rsplit('-', 1)[0]
            ipspaceName = vFiler.get('ipspace')

            xpathsearchtext = '//vfilers//vfiler[@name="' + vFilerFullName + '"]/interfaces'
            for interfaces in rootTreeFiler.xpath(xpathsearchtext):
                for interface in interfaces:
                    interfaceHostname = interface.get('hostname')
                    interfaceName = interface.find('int').text.strip()
                    xpathsearchtext = '//ifgroups//ifgroup[@name="' + interfaceName + '"]'
                    for ifgroup in rootTreeFiler.xpath(xpathsearchtext):
                        interfaceName = ifgroup.get('name') + "-" + "e" + re.sub('e', '', ifgroup.find('port').text.replace(' ', '')) + "-" + interface.find('vlan').text.strip()
                    interfaceVlan = interface.find('vlan').text.strip()
                    interfaceIp = interface.find('ip').text.strip()
                    interfaceNetmask = interface.find('netmask').text.strip()
                    interfaceMtu = interface.find('mtu').text.strip()

                    vFilerIpList += "-i " + interfaceIp + " "
                    vFilerInterfacesConfig += interfacesConfigCSS % vars()

                    for routes in interface:
                        for route in routes:
                            vFilerInterfaceRoute = route.text.strip()
                            vFilerRouteType = route.get('type')
                            vFilerRouteMetric = route.get('metric')
                            vFilerRoutesConfig += vFilerRouteAddCSS % vars()

                vFilersConfigTxt += vFilerVolCreateCSS % vars()
                vFilersConfigTxt += vFilerCreateCSS % vars()
                vFilersConfigTxt += vFilerDisallowProtoCSS % vars()
                vFilersConfigTxt += vFilerRoutesConfig
                vFilersConfigTxt += vFilerInterfacesConfig
    return vFilersConfigTxt


# generate vfiler interface + route for .rc
def vFilersInterfacesAndRoutes():
    vFilersConfigTxt = ""
    for vFilers in rootTreeFiler.xpath('//vfilers'):
        for vFiler in vFilers:
            vFilerIpList = ""
            vFilerInterfacesConfig = ""
            vFilerRoutesConfig = ""

            vFilerFullName = vFiler.get('name')
            vFilerShortName = vFilerFullName.rsplit('-', 1)[0]

            xpathsearchtext = '//vfilers//vfiler[@name="' + vFilerFullName + '"]/interfaces'
            for interfaces in rootTreeFiler.xpath(xpathsearchtext):
                for interface in interfaces:
                    interfaceHostname = interface.get('hostname')
                    interfaceName = interface.find('int').text.strip()
                    xpathsearchtext = '//ifgroups//ifgroup[@name="' + interfaceName + '"]'
                    for ifgroup in rootTreeFiler.xpath(xpathsearchtext):
                        interfaceName = ifgroup.get('name') + "-" + "e" + re.sub('e', '', ifgroup.find('port').text.replace(' ', '')) + "-" + interface.find('vlan').text.strip()
                    interfaceVlan = interface.find('vlan').text.strip()
                    interfaceIp = interface.find('ip').text.strip()
                    interfaceNetmask = interface.find('netmask').text.strip()
                    interfaceMtu = interface.find('mtu').text.strip()

                    vFilerIpList += "-i " + interfaceIp + " "
                    vFilerInterfacesConfig += interfacesConfigCSS % vars()

                    for routes in interface:
                        for route in routes:
                            vFilerInterfaceRoute = route.text.strip()
                            vFilerRouteType = route.get('type')
                            vFilerRouteMetric = route.get('metric')
                            vFilerRoutesConfig += vFilerRouteAddCSS % vars()

                vFilersConfigTxt += vFilerInterfacesConfig
                vFilersConfigTxt += vFilerRoutesConfig
    return vFilersConfigTxt


# configure global route
def globalRoutes():
    routeConfigTxt = ""
    for filerRoutes in rootTreeFiler.xpath('//global/routes'):
        for route in filerRoutes:
            routeType = route.get('type')
            routeMetric = route.get('metric')
            routeToAdd = route.text.strip()
            routeConfigTxt += globalRouteCSS % vars()
    return routeConfigTxt


# configure global Options
def globalOptions():
    globalOptionsDict = {}
    dnsServerList = []
    ntpServerList = ""

    dnsDomainName = rootTreeFiler.xpath('//globalOptions/dnsdomainname/text()')[0].strip()
    for dnsserver in rootTreeFiler.xpath('//globalOptions/dnsservers/dnsserver'):
        dnsServerList.append(dnsserver.text)

    for ntpserver in rootTreeFiler.xpath('//globalOptions/ntpservers/ntpserver'):
        ntpServerList = ntpServerList + " " + ntpserver.text + ","
    ntpServerList = ntpServerList[:-1]

    mailFrom = rootTreeFiler.xpath('//globalOptions/autosupport/mailfrom/text()')[0].strip()
    mailHost = rootTreeFiler.xpath('//globalOptions/autosupport/mailhost/text()')[0].strip()
    partnerMail = rootTreeFiler.xpath('//globalOptions/autosupport/partnermail/text()')[0].strip()
    mailTo = rootTreeFiler.xpath('//globalOptions/autosupport/mailto/text()')[0].strip()

    snmpContact = rootTreeFiler.xpath('//globalOptions/snmp/snmpcontact/text()')[0].strip()
    snmpLocation = rootTreeFiler.xpath('//globalOptions/snmp/snmplocation/text()')[0].strip()
    snmpTrapHost = rootTreeFiler.xpath('//globalOptions/snmp/snmptraphost/text()')[0].strip()

    globalOptionsDict = {
        'dnsDomainName': dnsDomainName,
        'dnsServerList': dnsServerList,
        'ntpServerList': ntpServerList,
        'mailFrom': mailFrom,
        'mailHost': mailHost,
        'partnerMail': partnerMail,
        'mailTo': mailTo,
        'snmpContact': snmpContact,
        'snmpLocation': snmpLocation,
        'snmpTrapHost': snmpTrapHost,
    }

    return globalOptionsDict

# main part start here

if __name__ == '__main__':

    # argment handling
    parser = argparse.ArgumentParser(description='.config and .rc file generator based on XML config file for Netapp filer', epilog='in case of script trouble contact me')

    parser.add_argument("-c", "--configfile", action="store", dest="configFile", help="XML config file", metavar='configfile', nargs=1, required=True)
    parser.add_argument("-v", "--vfiler", action="store_true", help="vfiler config generator only", default=False)

    args = parser.parse_args()

    if args.configFile:

        try:
            myXmlConfigFile = open(args.configFile[0], "r")
        except Exception, e:
            print "Error openning file: " + args.configFile[0]
            print str(e)
            os._exit(1)

    # date creation of file
    runningDate = datetime.datetime.now()

    # we setup xml parsing env
    treeFiler = etree.parse(myXmlConfigFile)
    rootTreeFiler = treeFiler.getroot()

    # retrive hostname from xml config
    HostnameFiler = HostNameConfig()

    # rc and config file will be name <hostname>.rc and .config
    # for vfiler config hostname.vfiler
    configFile = HostnameFiler + '.config'
    rcFile = HostnameFiler + '.rc'
    configVFiler = HostnameFiler + '.vfiler'

    if args.vfiler:

        try:
            myConfigFileVFiler = open(configVFiler, "w")
        except Exception, e:
            print "Error openning file: " + configFile
            print str(e)
            os._exit(1)

        # we write to vfiler config file only vfiler part
        myConfigFileVFiler.write(vFilersConfig())
        myConfigFileVFiler.close
    else:
        # we do full configuration so try open both file
        try:
            myConfigFile = open(configFile, "w")
        except Exception, e:
            print "Error openning file: " + configFile
            print str(e)
            os._exit(1)

        try:
            myRcFile = open(rcFile, "w")
        except Exception, e:
            print "Error openning file: " + rcFile
            print str(e)
            os._exit(1)

        # simple part we just create a dict with all our variable
        # then put them in form with cheetah template
        # in this version cheetah is just use to order and add comment to the rc and .config file
        # myConfigFile for .config
        # myRcFile for .rc
        dictTemplate = {
            'runningDate': runningDate,
            'BasicConfig': BasicConfig(),
            'ifGroupConfig': ifGroupConfig(),
            'vlanConfig': vlanConfig(),
            'interfacesConfig': interfacesConfig(),
            'globalRoutes': globalRoutes(),
            'vFilersInterfacesAndRoutes': vFilersInterfacesAndRoutes(),
            'optionsGeneral': optionsGeneral(),
            'ipspacesConfig': ipspacesConfig(),
            'vFilersConfig': vFilersConfig(),
        }

        # add to template dictionary globalOptions which is a dictionary
        dictTemplate.update(globalOptions())

        # fill template with dictionary
        configPrint = Template(file=tmplPath + "netapp.config.maker.Config.tmpl", searchList=[dictTemplate])
        rcPrint = Template(file=tmplPath + "netapp.config.maker.RC.tmpl", searchList=[dictTemplate])

        # create config file
        myConfigFile.write(str(configPrint))
        myRcFile.write(str(rcPrint))

        # close file we done all
        myConfigFile.close
        myRcFile.close


    #end of main
