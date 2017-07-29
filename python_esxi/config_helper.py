import os
import sys
import traceback

def lookup_env_variables():
    try:
        esxi_vsphere_server = os.environ["TF_VAR_vsphere_server"]
        esxi_user = os.environ["TF_VAR_vsphere_user"]
        esxi_pass = os.environ["TF_VAR_vsphere_password"]
    except Exception as error:
        exc_info = sys.exc_info()
        print("Error:  Missing env variable '{}'".format(exc_info[1].message))
        sys.exit()
        # Debugging
        #import pdb; pdb.set_trace()
        # type 'list' to see
        # dir() and dict() are helpful
        #traceback.print_exception(*exc_info)
    return [esxi_vsphere_server, esxi_user, esxi_pass]
