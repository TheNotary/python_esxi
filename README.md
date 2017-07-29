# Python ESXi
This package is able to build VMs against an ESXi (6.0) server with /mobs enabled.


## Setup

Install the dependencies:
```
$ pip install --upgrade pyvmomi
```

Install this package (as symlinks):
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

```
$ python main
```


## References
- [Python Package Structure](http://python-packaging.readthedocs.io/en/latest/minimal.html)
- [Getting started with pyvmomi](https://www.jacobtomlinson.co.uk/vmware/2016/06/22/using-vmware-esxi-vsphere-python-api/)

