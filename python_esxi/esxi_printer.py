#!/usr/bin/env python

from pyVmomi import vim

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
    state = "online" if summary.runtime.powerState == "poweredOn" else "off"
    print("\033[92m{}\033[0m - {}".format(summary.config.name, state))
    # print("  Path: {}".format(summary.config.vmPathName))
    # print("  Guest: {}".format(summary.config.guestFullName))
    annotation = summary.config.annotation
    if annotation != None and annotation != "":
        print("Annotation : {}".format(annotation))
    # print("  State: {}".format(summary.runtime.powerState))
    print("  Creation: {}".format(summary.runtime.bootTime.strftime("%Y-%m-%d")) )
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip != None and ip != "":
            print("  IP: {}".format(ip))
    if summary.runtime.question != None:
        print("Question  : ", summary.runtime.question.text)
        print("")
    print("")

def print_switch_info(switch):
    """
    Pass in a switch and all of it's Port Groups and Uplinks will be printed.
    """
    print(switch.name)
    print("  Port Groups:")
    for grp in tuple(switch.portgroup):
        print("    " + grp)

    print("  Uplinks")
    for pnic in tuple(switch.pnic):
        print("    " + pnic)
    print("")
