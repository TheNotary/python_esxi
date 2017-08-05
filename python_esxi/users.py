#!/usr/bin/env python

import pdb
import vm_util
from pyVmomi import vim

def create_users(my_cluster):
    if api_user_exists(my_cluster):
        print(u'\u2714' + " API user already exists.")
        return

    ud = my_cluster.RetrieveContent().userDirectory
    users = ud.RetrieveUserGroups(searchStr = "", exactMatch = False, findUsers = True, findGroups = False)

    am = my_cluster.RetrieveContent().accountManager

    api_user = vim.host.LocalAccountManager.PosixAccountSpecification(
        id = "api",
        password = "p_assw0rd1",
        description = "User for working with the API of ESXi")
    am.CreateUser(api_user)


def list_users(my_cluster):
    ud = my_cluster.RetrieveContent().userDirectory
    users = ud.RetrieveUserGroups(searchStr = "", exactMatch = False, findUsers = True, findGroups = False)

    print( "Users ({}): ".format(len(users)) )
    for u in users:
        print("  " + u.principal)
    print("")


def api_user_exists(my_cluster):
    ud = my_cluster.RetrieveContent().userDirectory
    users = ud.RetrieveUserGroups(searchStr = "api", exactMatch = True, findUsers = True, findGroups = False)
    if len(users) == 1:
        return True
    else:
        return False
