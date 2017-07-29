#!/usr/bin/env python
# Common VM Util
#
# This file homes things that make interacting with ESXi easier such as getting
# references to abstractions such as switches, hosts, nics and such.
#

from pyVmomi import vim


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
