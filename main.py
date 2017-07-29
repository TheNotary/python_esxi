import pdb
import os
import traceback
import sys

import pyVim
from pyVim import connect
from pyVmomi import vim

def main():
    esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()

    my_cluster = connect.ConnectNoSSL(esxi_vsphere_server, 443, esxi_user, esxi_pass)

    list_vms(my_cluster)

    connect.Disconnect(my_cluster)


def lookup_env_variables():
    try:
        esxi_vsphere_server = os.environ["TF_VAR_vsphere_server"]
        esxi_user = os.environ["TF_VAR_vsphere_user"]
        esxi_pass = os.environ["TF_VAR_vsphere_password"]
    except Exception as error:
        exc_info = sys.exc_info()
        print("Error:  Missing env variable '{}'".format(exc_info[1].message))
        sys.exit()
        #import pdb; pdb.set_trace()
        #traceback.print_exception(*exc_info)
    return [esxi_vsphere_server, esxi_user, esxi_pass]


def list_vms(my_cluster):
    content = my_cluster.RetrieveContent()
    for child in content.rootFolder.childEntity:
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            for vm in vmList:
                PrintVmInfo(vm)
    return 0


def PrintVmInfo(vm, depth=1):
    """
    Print information for a particular virtual machine or recurse into a folder
    or vApp with depth protection
    """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity
        for c in vmList:
            PrintVmInfo(c, depth+1)
        return

    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm, vim.VirtualApp):
        vmList = vm.vm
        for c in vmList:
            PrintVmInfo(c, depth + 1)
        return

    summary = vm.summary
    print("Name: {}".format(summary.config.name))
    print("  Path: {}".format(summary.config.vmPathName))
    print("  Guest: {}".format(summary.config.guestFullName))
    annotation = summary.config.annotation
    if annotation != None and annotation != "":
        print("Annotation : {}".format(annotation))
    print("  State: {}".format(summary.runtime.powerState))
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip != None and ip != "":
            print("  IP: {}".format(ip))
    if summary.runtime.question != None:
        print("Question  : ", summary.runtime.question.text)
        print("")
    print("")


main()
