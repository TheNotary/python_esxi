#!/usr/bin/env python

import pdb
import paramiko
import vm_util
from pyVmomi import vim

from config_helper import lookup_env_variables
esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()


verification_signature_for_local_sh_packer_vnc = "# Installer for packer-vnc firewall rule"


def bootstrap_esxi_network_configs(my_cluster):
    content = my_cluster.RetrieveContent()
    install_firewall_rule()
    create_vswitch(content)


def get_unassigned_pnic(content):
    hosts = vm_util.GetVMHosts(content)
    for host in hosts:
        ns = host.configManager.networkSystem

        # check if the physical_nic is bound to a vswitch
        for physical_nic in ns.networkConfig.pnic:
            for switch in host.config.network.vswitch:
                if is_pnic_free(host, physical_nic):
                    return physical_nic.device
    return None


def is_pnic_free(host, target_physical_nic):
    for vswitch in host.config.network.vswitch:
        pnics_used_by_vswitch = vswitch.spec.policy.nicTeaming.nicOrder.activeNic
        for pnic in pnics_used_by_vswitch:
            if pnic == target_physical_nic.device:
                return False

    return True


def create_vswitch(content):
    """
    This function will create a second Virtual Switch which allows me to have
    an isolated network for VMs that I don't want exposed to the internet.
    """
    hosts = vm_util.GetVMHosts(content)

    for host in hosts:
        switches = host.config.network.vswitch
        found_switch = does_switch1_already_exist(switches)

        if found_switch:
            print( u'\u2714' + " vSwitch1 already exists." )
            return found_switch
        else:
            pnic = get_unassigned_pnic(content)
            if pnic:
                print( "Creating vSwitch1 for host {}... Using pnic {}".format(host, pnic) )
                add_vswitch_to_host(host, "vSwitch1", pnic)
                add_portgroup_to_vswitch(host, "vSwitch1", "VM Network 2 Dark", 0)
            else:
                print( "WARN: Tried to find a free Physical NIC that wasn't already associated with a vSwitch and couldn't!")


def add_portgroup_to_vswitch(host, vswitchName, portgroupName, vlanId):
    portgroup_spec = vim.host.PortGroup.Specification(
        vswitchName = vswitchName,
        name = portgroupName,
        vlanId = int(vlanId),
        policy = vim.host.NetworkPolicy(
            security = vim.host.NetworkPolicy.SecurityPolicy(
                allowPromiscuous = False,
                macChanges = False,
                forgedTransmits = False
            )
        )
    )
    host.configManager.networkSystem.AddPortGroup(portgroup_spec)


def add_vswitch_to_host(host, vswitchName, nic_name):
    vswitch_spec = vim.host.VirtualSwitch.Specification(
        numPorts = 1024,
        mtu = 1450,
        bridge = vim.host.VirtualSwitch.BondBridge(
            nicDevice = [nic_name]
        )
    )
    host.configManager.networkSystem.AddVirtualSwitch(vswitchName, vswitch_spec)


def does_switch1_already_exist(switches):
    """
    Checks to see if vSwitch1 has already been created.  Only vSwitch0 is created
    at the start.
    """
    named_switch_already_created = False
    for switch in switches:
        if switch.name == "vSwitch1":
            named_switch_already_created = switch
    return named_switch_already_created


def install_firewall_rule():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(esxi_vsphere_server, username='root', password=esxi_pass, allow_agent=False)
    except paramiko.ssh_exception.NoValidConnectionsError, e:
        print("FAIL:  Could not establish SSH connection. Can't install VNC firewall rules.")
        print(e)
        return False

    # hack the local.sh file if it hasn't been hacked yet
    local_sh_file = get_local_sh_from_server(ssh)
    if local_sh_file_is_missing_hacks(local_sh_file):
        print("Updating /etc/rc.local.d/local.sh to include a command to install a VNC firewall rule...")
        patched_sh_file = patch_local_sh_with_vnc_firewall_dropper_and_exec(ssh, local_sh_file)
        upload_local_sh_to_server(patched_sh_file)
        reload_firewall_configs(ssh)
    else:
        print(u'\u2714' + " local.sh already patched to load VNC rules on reboot.")

    ssh.close()


def reload_firewall_configs(ssh):
    cmd_to_execute = """
    esxcli network firewall refresh
    """
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)


def upload_local_sh_to_server(patched_sh_file):
    t = paramiko.Transport((esxi_vsphere_server, 22))
    t.connect(username='root',password=esxi_pass)
    sftp = paramiko.SFTPClient.from_transport(t)

    tmp_file_path = "/tmp/temp_python_esxi_local_sh_file"
    with open(tmp_file_path, "w") as f:
        f.write(patched_sh_file)

    sftp.put(tmp_file_path, "/etc/rc.local.d/local.sh")


def local_sh_file_is_missing_hacks(local_sh_file):
    # Check to see if dropper rule already exists
    if local_sh_file.find(verification_signature_for_local_sh_packer_vnc) == -1:
        return True
    else:
        return False


def patch_local_sh_with_vnc_firewall_dropper_and_exec(ssh, local_sh_file):
    packer_vnc_dropper_code = """
%s
firewall_rule="
<ConfigRoot>
    <service id='1000'>
      <id>packer-vnc</id>
      <rule id='0000'>
        <direction>inbound</direction>
        <protocol>tcp</protocol>
        <porttype>dst</porttype>
        <port>
          <begin>5900</begin>
          <end>6000</end>
        </port>
      </rule>
      <enabled>true</enabled>
      <required>true</required>
    </service>
</ConfigRoot>
"
echo "${firewall_rule}" > /etc/vmware/firewall/packer-vnc.xml
esxcli network firewall refresh

exit 0""" % (verification_signature_for_local_sh_packer_vnc)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(packer_vnc_dropper_code)

    local_sh_file = local_sh_file.replace("exit 0", packer_vnc_dropper_code)
    return local_sh_file


def local_sh_cmd_missing(local_sh_file):
    if local_sh_file.find("packer_vnc") == -1:
        return True
    else:
        return False


def get_local_sh_from_server(ssh):
    """
    The /etc/rc.local.d/local.sh file represents one of the few files to which
    persistent changes can be made.  It also represents a startup script that
    runs everytime your system boots up.  Because firewall rule changes are
    wiped out upon reboot, they must be reapplied through this script.
    """

    cmd_to_execute = """
        cat /etc/rc.local.d/local.sh
    """

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    local_sh_file = ssh_stdout.read()
    return local_sh_file
