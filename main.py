import pdb
import os
import traceback
import sys

import pyVim
from pyVim import connect

def main():
    esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()

    my_cluster = connect.ConnectNoSSL(esxi_vsphere_server, 443, esxi_user, esxi_pass)
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


main()
