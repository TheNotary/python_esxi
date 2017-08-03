#!/usr/bin/env python

import pyVim
from pyVmomi import vim

def list_license_info(my_cluster):
    lm = my_cluster.RetrieveContent().licenseManager

    license_name = lm.licenses[0].name
    if license_name == 'Evaluation Mode':
        print("WARNING:\nWARNING:  Your server is still in evaluation mode and needs you to manually login and fill in the free esxi key.\nWARNING:")
        return False
    else:
        print( "Detected License '{}' ".format(license_name) )
        return True


def print_uptime(my_cluster):
    content = my_cluster.RetrieveContent()
    host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)

    for host in host_view.view:
        seconds = host.RetrieveHardwareUptime()
        print("Uptime: {} hours".format(seconds/60.0/60.0) )
