from unittest import TestCase

import python_esxi

class TestNetwork(TestCase):
    def test_list_vswitch_info_returns_a_count_of_vswitches(self):
        my_cluster = python_esxi.vm_util.connect()

        s = python_esxi.list_vswitch_info(my_cluster)
        self.assertTrue(isinstance(s, int))
        self.assertEqual(s, 2)  # My server just has the two right now

        python_esxi.vm_util.disconnect(my_cluster)
