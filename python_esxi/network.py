#!/usr/bin/env python

import vm_util
from pyVmomi import vim


def bootstrap_esxi_network_configs():
    vswitch = create_vswitch()
    add_portgroups(vswitch)

def create_vswitch():
    print("I'm a stub")

def add_portgroups(vswitch):
    print("I'm a stub")
