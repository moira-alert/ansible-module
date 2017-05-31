#!/usr/bin/python
#SKB KONTUR

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: moira_trigger
short_description: Working with large number of triggers in Moira
description:
    - Create new triggers
    - Edit existing triggers parameters
    - Delete triggers
version_added:
    - 2.3.0.0
author:
    - SKB Kontur
requirements:
    - 'python >= 2.6'
    - 'moira-client >= 0.4'
options:
  moira:
    description:
      - Url of Moira API.
    type: 'str'
    required: True
  state:
    description:
      - Desired state of a trigger.
      - Use state 'present' to create and edit existsing triggers and state 'absent' to delete triggers.
    type: 'str'
    required: True
    choices: ['present', 'absent']
  name:
    description:
      - Trigger name.
    type: 'str'
    required: True
  desc:
    description:
      - Trigger description.
    type: 'str'
    required: False
  ttl:
    description:
      - Time To Live.
    type: 'str'
    required: False
    default: '600'
  ttl_state:
    description:
      - Trigger state at the expiration of TTL.
    type: 'str'
    required: False
    default: 'NODATA'
    choices: ['NODATA', 'ERROR', 'WARN', 'OK']
  expression:
    description:
      - Python expression.
    type: 'str'
    required: False
  disabled_days:
    description:
      - Days for trigger to be in silent mode.
    type: 'dict'
    required: False
  targets:
    description:
      - List of trigger targets.
    type: 'list'
    required: True
  tags:
    description:
      - List of trigger tags.
    type: 'list'
    required: False
  warn_value:
    description:
      - Value to set WARN status.
    type: 'int'
    required: False
  error_value:
    description:
      - Value to set ERROR status.
    type: 'int'
    required: False
'''

EXAMPLES = '''
- name: MoiraAnsible
  moira_trigger:
     moira: http://localhost/api/
     state: present
     name: '{{ item.name }}'
     desc: trigger test description
     warn_value: 300
     error_value: 600
     ttl_state: ERROR
     tags:
       - first_tag
       - second_tag
     targets: '{{ item.targets }}'
     disabled_days:
       ? Mon
       ? Wed
     with_items:
       - name: test1
         targets:
           - test1.rps
           - test2.rps
       - name: test2
         targets:
           - test3.rps
           - test4.rps
'''

RETURN = '''
results:
  description: Current state of trigger
  returned: success
  type: dictionary
  sample: {
  'test2': {
            'trigger changed': {
                'desc': 'trigger test description',
                'disabled_days': {
                    'Mon': null,
                    'Tue': null
                },
                'error_value': 500,
                'expression': null,
                'name': 'test2',
                'tags': [
                    'first_tag',
                    'second_tag'
                ],
                'targets': [
                    'test30.rps',
                    'test40.rps'
                ],
                'ttl': '600',
                'ttl_state': 'ERROR',
                'warn_value': 300
            }
        }
    }
'''

from moira_client import Moira
from ansible.module_utils.basic import AnsibleModule

class MoiraAnsible():

    def __init__(self, results = {}, failed = {}):

        self.results = results

        self.failed = failed

    def api_check(self):

        components = {'pattern', 'tag', 'trigger'}

        api_fails = {}

        for component in components:
            try:
                moira.trigger.trigger_client.get('/'+component)
            except:
                api_fails.update({component: 'request failed'})

        if api_fails:
            self.failed['Unable to connect to Moira API'] = api_fails

        return bool(not(api_fails))

    def tag_cleanup(self):

        for tag in moira.tag.stats():
            if not tag.triggers:
                moira.tag.delete(tag.name)

    def get_trigger_id(self, trigger):

        trigger_id = None

        all_triggers = moira.trigger.fetch_all()

        for moira_trigger in all_triggers:
            if moira_trigger.name == trigger['name']:
                trigger_id = moira_trigger.id

        return trigger_id

    def parameters_change(self, moira_trigger, trigger):

        parameters_to_change = {}

        for parameter in trigger:
            if not(moira_trigger.__dict__[parameter] == trigger[parameter]):
                moira_trigger.__dict__[parameter] = trigger[parameter]

        moira_trigger.update()

    def triggers(self, trigger, state):

        current_id = self.get_trigger_id(trigger)

        if state == 'absent':
            if current_id:
                moira.trigger.delete(current_id)
                self.results[trigger['name']] = {'trigger removed': current_id}
            else:
                self.results.update({trigger['name']: 'no id found for trigger'})

        elif state == 'present':
            if current_id:
                moira_trigger = moira.trigger.fetch_by_id(current_id)
                self.parameters_change(moira_trigger, trigger)
                self.results[trigger['name']] = {'trigger changed': trigger}
            else:
                new_trigger = moira.trigger.create(**trigger)
                new_trigger.save()
                self.parameters_change(new_trigger, trigger)
                self.results[trigger['name']] = {'new trigger created': trigger}

def main():

    fields = {
        'moira': {
            'type': 'str',
            'required': True
            },
        'state': {
            'type': 'str',
            'required': True,
            'choices': ['present', 'absent']
            },
        'name': {
            'type': 'str',
            'required': True
            },
        'desc': {
            'type': 'str',
            'required': False
            },
        'ttl': {
            'type': 'str',
            'required': False,
            'default': '600'
            },
        'ttl_state': {
            'type': 'str',
            'required': False,
            'default': 'NODATA',
            'choices': ['NODATA', 'ERROR', 'WARN', 'OK']
            },
        'expression': {
            'type': 'str',
            'required': False
            },
        'disabled_days': {
            'type': 'dict',
            'required': False
            },
        'targets': {
            'type': 'list',
            'required': True
            },
        'tags': {
            'type': 'list',
            'required': False
            },
        'warn_value': {
            'type': 'int',
            'required': False
            },
        'error_value': {
            'type': 'int',
            'required': False
            }
        }

    module = AnsibleModule(argument_spec=fields)
    global moira
    moira = Moira(module.params['moira'])
    moira_ansible = MoiraAnsible()

    if not moira_ansible.api_check():
        module.fail_json(msg=moira_ansible.failed)

    trigger = {}
    trigger_parameters = {'name', 'desc', 'ttl', 'ttl_state', 'expression', 'targets', 'tags', 'disabled_days', 'warn_value', 'error_value'}

    for parameter in module.params:
        if parameter in trigger_parameters:
            trigger.update({parameter: module.params[parameter]})

    moira_ansible.triggers(trigger, module.params['state'])
    moira_ansible.tag_cleanup()
    module.exit_json(msg=moira_ansible.results)

if __name__ == '__main__':
    main()
