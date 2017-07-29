def print_switch_info(switch):
    print(switch.name)
    for grp in tuple(switch.portgroup):
        print("  " + grp)
