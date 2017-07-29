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

# Debug:
"""
from python_esxi import *
list_vms()
list_vswitch_info()
"""

esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()


def main():
    list_vms()
    # list_vswitch_info()


def list_vms():
    my_cluster = vm_util.connect()
    # import pdb; pdb.set_trace()

    content = my_cluster.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            for vm in vmList:
                esxi_printer.PrintVmInfo(vm)

    vm_util.disconnect(my_cluster)
    print("Total VMs: {}".format(len(vmList)))


def list_vswitch_info():
    my_cluster = vm_util.connect()

    content = my_cluster.RetrieveContent()

    hosts = vm_util.GetVMHosts(content)
    hostSwitchesDict = vm_util.GetHostsSwitches(hosts)

    for host, vswithes in hostSwitchesDict.items():
        for v in vswithes:
            print_switch_info(v)

    vm_util.disconnect(my_cluster)


if __name__ == "__main__":
    main()
