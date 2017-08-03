#!/usr/bin/env python

import pdb
import os
import sys
import traceback

from pyVim import connect
from pyVmomi import vim

from config_helper import lookup_env_variables
import vm_util
import esxi_printer
import general_system
from network import bootstrap_esxi_network_configs
from users import create_users, list_users

# Debug:
"""
from python_esxi import *
list_vms()
list_vswitch_info()
"""

esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()


def main():
    my_cluster = vm_util.connect()
    # pdb.set_trace()

    # create_users(my_cluster)
    # list_users(my_cluster)

    # set_advanced_configs()
    general_system.list_license_info(my_cluster)
    general_system.print_uptime(my_cluster)

    # bootstrap_esxi_network_configs()
    # list_vswitch_info(my_cluster)
    # list_vms(my_cluster)

    vm_util.disconnect(my_cluster)


def set_advanced_configs(my_cluster):
    """
    Sets advanced configs like hostname, etc.
    """


def list_vms(my_cluster):

    content = my_cluster.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            for vm in vmList:
                esxi_printer.PrintVmInfo(vm)

    print("Total VMs: {}".format(len(vmList)))
    # return len(vmList)


def list_vswitch_info(my_cluster):
    content = my_cluster.RetrieveContent()

    hosts = vm_util.GetVMHosts(content)
    hostSwitchesDict = vm_util.GetHostsSwitches(hosts)

    vswitch_count = 0
    for host, vswitches in hostSwitchesDict.items():
        for vswitch in vswitches:
            vswitch_count += 1
            esxi_printer.print_switch_info(vswitch)

    print( "Total number of switches:  {}".format(vswitch_count) )
    return vswitch_count


if __name__ == "__main__":
    main()
