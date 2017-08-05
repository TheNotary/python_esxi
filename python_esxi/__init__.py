#!/usr/bin/env python
"""
API DOCS: https://github.com/vmware/pyvmomi/tree/master/docs
SAMPLES: https://github.com/vmware/pyvmomi-community-samples/tree/master/samples
"""

import pdb
import os
import sys
import traceback

import paramiko
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

    # list_datastores(my_cluster)

    general_system.count_datastores(my_cluster)

    # FINISHED:
    # create_users(my_cluster)
    # bootstrap_esxi_network_configs(my_cluster)
    # general_system.set_advanced_configs(my_cluster)
    # general_system.check_for_ssh(esxi_vsphere_server)
    # general_system.list_license_info(my_cluster)
    # general_system.print_uptime(my_cluster)

    # Unwanted Ones:
    # list_users(my_cluster)
    # list_vswitch_info(my_cluster)
    # list_vms(my_cluster)

    vm_util.disconnect(my_cluster)





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
