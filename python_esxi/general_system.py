#!/usr/bin/env python

import pyVim
from pyVmomi import vim


def set_advanced_configs(service_instance):
    """
    Sets advanced configs like hostname, etc.
    """

    content = service_instance.RetrieveContent()

    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)

    host = host_view.view[0]
    option_manager = host.configManager.advancedOption

    # pdb.set_trace()
    option = vim.option.OptionValue(key = "Net.GuestIPHack", value=long(1))
    option_manager.UpdateOptions(changedValue=[option])


def list_license_info(my_cluster):
    lm = my_cluster.RetrieveContent().licenseManager

    license_name = lm.licenses[0].name
    if license_name == 'Evaluation Mode':
        print("WARNING:\nWARNING:  Your server is still in evaluation mode and needs you to manually login and fill in the free esxi key.\nWARNING:")
        return False
    else:
        print( u'\u2714' + " License detected '{}' ".format(license_name) )
        return True


def print_uptime(my_cluster):
    content = my_cluster.RetrieveContent()
    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)

    # host_view.view[0]
    for host in host_view.view:
        seconds = host.RetrieveHardwareUptime()
        print("Uptime: {} hours".format(seconds/60.0/60.0) )


import socket
def check_for_ssh(esxi_vsphere_server):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((esxi_vsphere_server, 22))
        print( u'\u2714' + " SSH is enabled" )
        s.close()
        return True
    except socket.error as e:
        print( "Connection on port 22 to {} failed {}".format(esxi_vsphere_server, e) )
        print("WARNING:\nWARNING:  You'll need to login to the ESXi server, right click the Host -> Services -> Enable Secure Shell\nWARNING:")
        s.close()
        return False
