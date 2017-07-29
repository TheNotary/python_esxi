import pdb
import os
import sys
import traceback

from pyVim import connect
from pyVmomi import vim

from config_helper import lookup_env_variables
import vm_util
import esxi_printer
from network import *

def main():
    esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()

    my_cluster = connect.ConnectNoSSL(esxi_vsphere_server, 443, esxi_user, esxi_pass)

    #list_vms(my_cluster)
    list_vswitch_info(my_cluster)

    connect.Disconnect(my_cluster)


def list_vms(my_cluster):
    content = my_cluster.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            for vm in vmList:
                esxi_printer.PrintVmInfo(vm)
    return 0


def list_vswitch_info(my_cluster):
    content = my_cluster.RetrieveContent()

    hosts = vm_util.GetVMHosts(content)
    hostSwitchesDict = vm_util.GetHostsSwitches(hosts)

    for host, vswithes in hostSwitchesDict.items():
        for v in vswithes:
            print_switch_info(v)
            # import pdb; pdb.set_trace()


main()
