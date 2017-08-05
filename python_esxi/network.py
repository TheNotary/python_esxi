#!/usr/bin/env python

import pdb
import paramiko
import vm_util
from pyVmomi import vim

from config_helper import lookup_env_variables
esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()


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
    ssh.connect(esxi_vsphere_server, username='root', password=esxi_pass, allow_agent=False)

    service_xml_file = get_firewall_xml_from_server(ssh)

    if vnc_firewall_rule_missing(service_xml_file):
        print("Installing firewall for VNC connections...")
        service_xml_file = patch_firewall_xml_with_vnc_rule(service_xml_file)
        upload_firewall_xml_to_server(service_xml_file)
        swap_in_new_firewall_file(ssh)
    else:
        print(u'\u2714' + " Firewall rule for VNC already installed.")

    ssh.close()


def vnc_firewall_rule_missing(service_xml_file):
    if service_xml_file.find("packer-vnc") == -1:
        return True
    else:
        return False


def upload_firewall_xml_to_server(service_xml_file):
    t = paramiko.Transport((esxi_vsphere_server, 22))
    t.connect(username='root',password=esxi_pass)
    sftp = paramiko.SFTPClient.from_transport(t)

    tmp_file_path = "/tmp/temp_python_esxi_firewall_file"
    with open(tmp_file_path, "w") as f:
        f.write(service_xml_file)

    sftp.put(tmp_file_path, "/etc/vmware/firewall/service.xml.new")


def swap_in_new_firewall_file(ssh):
    cmd_to_execute = """
    chmod 644 /etc/vmware/firewall/service.xml && \
        chmod +t /etc/vmware/firewall/service.xml && \
        mv /etc/vmware/firewall/service.xml /etc/vmware/firewall/service.xml.bk && \
        mv /etc/vmware/firewall/service.xml.new /etc/vmware/firewall/service.xml && \
        chmod 444 /etc/vmware/firewall/service.xml && \
        esxcli network firewall refresh
    """
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)


def get_firewall_xml_from_server(ssh):
    cmd_to_execute = """
        cat /etc/vmware/firewall/service.xml
    """
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    service_xml_file = ssh_stdout.read()
    return service_xml_file


def patch_firewall_xml_with_vnc_rule(service_xml_file):
    new_firewall_rule = """
        <service id="1000">
          <id>packer-vnc</id>
          <rule id="0000">
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
    """
    return service_xml_file.replace('</ConfigRoot>', new_firewall_rule)
