# Python ESXi
This package is able to configure a freshly installed ESXi (6.5) server.  It assumes you want two vswitches... customize this stuff to meet your own needs via the `python_esxi/network.py` script.  It will basically setup ESXi such that it is ready for someone to manually step in and add datastores, but otherwise is ready to be dropped into production and generate VMs via packer according to the process described in Nick Charlton's fanstastic [blog post](https://nickcharlton.net/posts/using-packer-esxi-6.html).


## Install

Install this package (`-e` for symlink install so you can edit the script):
```
$ pip install -e .
```

Configure secrets and source them:
```
export TF_VAR_vsphere_user='root'
export TF_VAR_vsphere_password=''
export TF_VAR_vsphere_server='192.168.1.2'
```


## Usage

To attempt to a provision an esxi host

```
$ python_esxi
✔ API user already exists.
✔ Firewall rule for VNC already installed.
✔ vSwitch1 already exists.
✔ Net.GuestIPHack already set to 1
✔ SSH is enabled
✔ License detected 'VMware vSphere 6 Hypervisor'
✔ Detected 1 datastore(s): ['datastore1']

Uptime: 75.5366666667 hours
```


## Running Tests

To run the test suite, enter the below command into your turtle:
```
python setup.py test
```


## License

MIT


## References
- [Python Package Structure](http://python-packaging.readthedocs.io/en/latest/minimal.html)
- [Getting started with pyvmomi](https://www.jacobtomlinson.co.uk/vmware/2016/06/22/using-vmware-esxi-vsphere-python-api/)

