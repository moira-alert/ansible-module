'''Mock ansible'''

import sys

class _Ansible(object):

    '''Mock ansible package'''

    def __init__(self):
        self.module_utils = _Ansible._ModuleUtils()

    class _ModuleUtils(object):

        def __init__(self):
            self.basic = _Ansible._ModuleUtils._Basic()

        class _Basic(object):

            def __init__(self, AnsibleModule='AnsibleModule'):
                self.AnsibleModule = AnsibleModule

ansible = _Ansible()
sys.modules['ansible.module_utils.basic'] = ansible.module_utils.basic
