def PrintVmInfo(vm, depth=1):
    """
    Print information for a particular virtual machine or recurse into a folder
    or vApp with depth protection
    """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity
        for c in vmList:
            PrintVmInfo(c, depth+1)
        return

    # if this is a vApp, it likely contains child VMs
    # (vApps can nest vApps, but it is hardly a common usecase, so ignore that)
    if isinstance(vm, vim.VirtualApp):
        vmList = vm.vm
        for c in vmList:
            PrintVmInfo(c, depth + 1)
        return

    summary = vm.summary
    print("Name: {}".format(summary.config.name))
    print("  Path: {}".format(summary.config.vmPathName))
    print("  Guest: {}".format(summary.config.guestFullName))
    annotation = summary.config.annotation
    if annotation != None and annotation != "":
        print("Annotation : {}".format(annotation))
    print("  State: {}".format(summary.runtime.powerState))
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip != None and ip != "":
            print("  IP: {}".format(ip))
    if summary.runtime.question != None:
        print("Question  : ", summary.runtime.question.text)
        print("")
    print("")
