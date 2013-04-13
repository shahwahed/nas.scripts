#!/usr/bin/python
#-*-coding: utf8 -*


"""Python configmaker_nas.py 
Script generate custom netapp filer .config and .rc based on XML config file
"""
__author__ = "Shah Mohsin WAHED <s.wahed@laposte.net>"
__copyright__ = "Copyright (c) 2013 S.WAHED"
__license__ = "GPL"
__version__ = "1.1"
__cvsversion__ = "$Revision: $"
__date__ = "$Date: $"


import argparse
from lxml import etree
import subprocess
import sys
import string
import getpass, os

# this part contain all netapp command use python 2.x % vars to fill command
# command format :
# netapp command line with $(variable) for each variable you want to fill in
#
ifGroupConfigCSS = "ifgrp create %(lagType)s %(ifgroupename)s -b port %(port)s \n"
vlanConfigCSS = "vlan create %(ifgroupename)s %(vlanlist)s \n"
ipspacesConfigCSS =  "ipspace create %(ipspaceName)s %(ipspaceInterfaces)s \n"
interfacesConfigCSS = "ifconfig %(interfaceName)s %(interfaceHostname)s netmask %(interfaceNetmask)s mtusize %(interfaceMtu)s partner %(interfaceName)s \n"
globalRouteCSS = "route add %(routeType)s %(routeToAdd)s %(routeMetric)s \n"
vFilerVolCreateCSS = "vol create %(vFilerShortName)s_vol_root -s volume RP_NL2_01_etc 300M \n"
vFilerCreateCSS = "vfiler create %(vFilerFullName)s -n -s %(ipspaceName)s %(vFilerIpList)s /vol/%(vFilerShortName)s_vol_root \n"
vFilerDisallowProtoCSS = "vfiler disallow %(vFilerFullName)s proto=ssh proto=rsh proto=iscsi proto=ftp \n"
vFilerRouteAddCSS = "vfiler run %(vFilerFullName)s route add %(vFilerRouteType)s %(vFilerInterfaceRoute)s  %(vFilerRouteMetric)s\n"

# function to return filer hostname from xml config
def HostNameConfig():
    HostnameFiler = rootTreeFiler.xpath('//hostname/text()')[0].strip()
    return HostnameFiler

# we setup basic configuration here 
def BasicConfig():
    ConfigFileHostname = "hostname " + HostnameFiler +"\n"
    return ConfigFileHostname

# general options we set up in our configuration
def optionsGeneral():
    partnerAddress = rootTreeFiler.xpath('//partnerAddress/text()')[0].strip()
    optionsGeneralTxt = ""
    optionsGeneralTxt +="options licensed_feature.multistore.enable on \n"
    optionsGeneralTxt +="options cf.giveback.auto.cancel.on_network_failure on \n"
    optionsGeneralTxt +="options cf.takeover.on_reboot on \n"
    optionsGeneralTxt +="options cf.hw_assist.partner.address " + partnerAddress + "\n"
    optionsGeneralTxt +="options cf.hw_assist.enable on  \n"
    return optionsGeneralTxt


# generate ifgroup configuration
def ifGroupConfig():
    ifGroupConfigTxt = ""
    # we cycle in ifgroups xml part and get interface name and bind it to physical port
    # then make config command using the ifGroupConfigCSS
    for ifgroups in rootTreeFiler.xpath('//ifgroups'):
        for ifgroup in ifgroups:
            ifgroupename =  ifgroup.get('name') + "-" + ifgroup.find('port').text.replace(' ', '')
            port = ifgroup.find('port').text
            lagType = ifgroup.find('type').text
            ifGroupConfigTxt += ifGroupConfigCSS % vars()
    return ifGroupConfigTxt

# generate vlan config
def vlanConfig():
    vlanConfigTxt = ""
    # cylcle on xml part with the ifgroupname short name (vm1 for exemple) we could find the correct port
    for ifgroups in rootTreeFiler.xpath('//ifgroups'):
        for ifgroup in ifgroups:
            ifgroupename =  ifgroup.get('name') + "-" + ifgroup.find('port').text.replace(' ', '')
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
            interfaceHostname = interface.get('hostnamename')
            interfaceName = interface.find('int').text.strip()
            interfaceNetmask = interface.find('netmask').text.strip()
            interfaceMtu = interface.find('mtu').text.strip()
            xpathsearchtext = '//ifgroups//ifgroup[@name="' + interfaceName + '"]'
            for ifgroup in rootTreeFiler.xpath(xpathsearchtext):
                interfaceName = ifgroup.get('name')  + "-" + ifgroup.find('port').text.replace(' ', '') + "-" + interface.find('vlan').text.strip()
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
                        interfaceName = ifgroup.get('name')  + "-" + ifgroup.find('port').text.replace(' ', '') + "-" + interface.find('vlan').text.strip()
                    interfaceVlan = interface.find('vlan').text.strip()
                    interfaceIp = interface.find('ip').text.strip()
                    interfaceNetmask = interface.find('netmask').text.strip()
                    interfaceMtu = interface.find('mtu').text.strip()
                    
                    vFilerIpList += "-i " + interfaceIp + " "
                    vFilerInterfacesConfig += interfacesConfigCSS % vars()

                    for routes in  interface:
                        for route in routes:
                            vFilerInterfaceRoute = route.text.strip()
                            vFilerRouteType = route.get('type')
                            vFilerRouteMetric =  route.get('metric')
                            vFilerRoutesConfig += vFilerRouteAddCSS % vars()

                vFilersConfigTxt += vFilerVolCreateCSS % vars()
                vFilersConfigTxt += vFilerCreateCSS % vars()
                vFilersConfigTxt += vFilerDisallowProtoCSS % vars()
                vFilersConfigTxt += vFilerRoutesConfig
                vFilersConfigTxt +=  vFilerInterfacesConfig
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
                        interfaceName = ifgroup.get('name')  + "-" + ifgroup.find('port').text.replace(' ', '') + "-" + interface.find('vlan').text.strip()
                    interfaceVlan = interface.find('vlan').text.strip()
                    interfaceIp = interface.find('ip').text.strip()
                    interfaceNetmask = interface.find('netmask').text.strip()
                    interfaceMtu = interface.find('mtu').text.strip()

                    vFilerIpList += "-i " + interfaceIp + " "
                    vFilerInterfacesConfig += interfacesConfigCSS % vars()

                    for routes in  interface:
                        for route in routes:
                            vFilerInterfaceRoute = route.text.strip()
                            vFilerRouteType = route.get('type')
                            vFilerRouteMetric =  route.get('metric')
                            vFilerRoutesConfig += vFilerRouteAddCSS % vars()

                vFilersConfigTxt +=  vFilerInterfacesConfig
                vFilersConfigTxt += vFilerRoutesConfig
    return vFilersConfigTxt


# configure global route
def globalRoutes():
    routeConfigTxt = ""
    for filerRoutes in rootTreeFiler.xpath('//global/routes'):
        for route in filerRoutes:
            routeType = route.get('type')
            routeMetric =  route.get('metric')
            routeToAdd = route.text.strip()
            routeConfigTxt += globalRouteCSS % vars()
    return routeConfigTxt


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
            print "Error openning file: "+args.configFile[0]
            print str(e)
            os._exit(1)

    

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
            print "Error openning file: "+configFile
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
            print "Error openning file: "+configFile
            print str(e)
            os._exit(1)

        try:
            myRcFile = open(rcFile, "w")
        except Exception, e:
            print "Error openning file: "+rcFile
            print str(e)
            os._exit(1)

        # simple part we just write each config command to the correct filer
        # myConfigFile for .config
        # myRcFile for .rc
        myConfigFile.write("echo ifgrp and vlan creation \n")
        myConfigFile.write(ifGroupConfig())
        myConfigFile.write(vlanConfig())
        myConfigFile.write("echo General options\n")
        myConfigFile.write(optionsGeneral())
        myConfigFile.write("echo ipspaces creation\n")
        myConfigFile.write(ipspacesConfig())
        myConfigFile.write("echo vfiler0 interface address\n")
        myConfigFile.write(interfacesConfig())
        myConfigFile.write("echo global route\n")
        myConfigFile.write(globalRoutes())
        myConfigFile.write("echo vfilers configuration\n")
        myConfigFile.write(vFilersConfig())

        myRcFile.write(BasicConfig())
        myRcFile.write(ifGroupConfig())
        myRcFile.write(vlanConfig())
        myRcFile.write(interfacesConfig())
        myRcFile.write(vFilersInterfacesAndRoutes())
        myRcFile.write(globalRoutes())

        # close file we done all
        myConfigFile.close
        myRcFile.close
    

    #end of main
