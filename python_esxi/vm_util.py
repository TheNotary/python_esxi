#!/usr/bin/env python
# Common VM Util
#
# This file homes things that make interacting with ESXi easier such as getting
# references to abstractions such as switches, hosts, nics and such.
#

import pyVim
from pyVmomi import vim

from config_helper import lookup_env_variables
esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()


def connect():
    return pyVim.connect.ConnectNoSSL(esxi_vsphere_server, 443, esxi_user, esxi_pass)


def disconnect(my_cluster):
    pyVim.connect.Disconnect(my_cluster)


def GetHostsSwitches(hosts):
    hostSwitchesDict = {}
    for host in hosts:
        switches = host.config.network.vswitch
        hostSwitchesDict[host] = switches
    return hostSwitchesDict


def GetVMHosts(content):
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj
