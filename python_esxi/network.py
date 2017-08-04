#!/usr/bin/env python

import pdb
import paramiko
import vm_util
from pyVmomi import vim

from config_helper import lookup_env_variables
esxi_vsphere_server, esxi_user, esxi_pass = lookup_env_variables()


def bootstrap_esxi_network_configs(my_cluster):
    content = my_cluster.RetrieveContent()

    hosts = vm_util.GetVMHosts(content)
    hostSwitchesDict = vm_util.GetHostsSwitches(hosts)

    install_firewall_rule()

    vswitch = create_vswitch()
    add_portgroups(vswitch)


def create_vswitch():
    print("I'm a stub")


def add_portgroups(vswitch):
    print("I'm a stub")


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
