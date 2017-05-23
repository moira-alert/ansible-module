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
    - Delete targets from triggers and triggers with no targets
version_added:
    - 2.3.0.0
author:
    - SKB Kontur
requirements:
    - 'python >= 2.6'
    - 'moira-client >= 0.4'
options:
  moira-server:
    description:
      - Url of Moira API
    required: True
  branch:
    description:
      - Dictionary with parameters to use as common trigger template. Keys can be any. Subkeysto be used are:name, targets, desc, warn_value, error_value, tags, ttl_state.
      - Use ';' to separate objects in tags and targets values.
      - Do not use same keys in both branch and leaves sections. Use leaves section to differentiate triggers.
    required: False
  leaves:
    description:
      - Dictionary with parameters to complement common trigger template.
      - For n leaves, in Moira there will be created n triggers. With jinja filters, n different groups of triggers can be created.
    required: False
  fall:
    description:
      - Dictionary with metric targets as values. Keys can be any.
      - Function searches for trigger, related to specified target and removes target from trigger. Trigger will be also deleted if no targets found after first operation.
    required: False
  gardening:
    description:
      - change:Dictionary with existing tagname as key and tagname you want to change as key value.
      - cleanup:Boolean(Key presence). Removes every tagname if its not assigned to at least one trigger.
    required: False
'''

EXAMPLES = '''
- name: Moira
  moira_trigger:

     moira-server: http://localhost/api/

     branch:
       desc: all triggers test description
       warn_value: 300
       error_value: 600
       tags: first_tag; second_tag
       ttl_state: ERROR

     leaves:
       leaf_0:
         name: trigger_00
         targets: target_00.rps
       leaf_1:
         name: trigger_01
         targets: target_10.rps; target_11.rps
       leaf_2:
         name: trigger_02
         targets: target_20.rps; target_21.rps; target_22.rps

     fall:
       target_0: target_30.rps
       target_1: target_31.rps

     gardening:
       change:
         third_tag: second_tag
       cleanup: True
'''

RETURN = '''
results:
  description: Results of module execution inside ansible playbook
  returned: always
  type: complex
  sample: {'msg': {'already_exist': {'1': [{'ttl_state': 'ERROR', 'warn_value': 300, 'targets': ['target_20.rps', 'target_21.rps', 'target_22.rps'],
  'name': 'trigger_02', 'tags': ['first_tag', 'second_tag'], 'error_value': 600, 'desc': 'all triggers test description'}]}, 'tags_changed': {'third_tag': 'second_tag'},
  'triggers_removed': {'2': ['trigger_00', 'trigger_00']}, 'tags_removed': {'1': ['fourth_tag']}, 'triggers_saved': '100% of triggers has been saved successfully',
  'targets_removed': {'2': ['target_00.rps', 'target_10.rps']}}}
  contains:
    triggers_saved:
      description: Dictionary with successfuly saved triggers
      returned: always
      type: dict
      sample: {'triggers_saved': '100% of triggers has been saved successfully'}
    already_exist:
      description: Dictionary with triggers that already exists
      returned: always
      type: dict
      sample: {'already_exist': {'1': [{'desc': 'all triggers test description', 'error_value':600, 'name': 'trigger_02', 'tags': ['first_tag', 'second_tag'],
      'targets': ['target_20.rps', 'target_21.rps', 'target_22.rps'], 'ttl_state': 'ERROR', 'warn_value': 300}]}}
    targets_removed:
      description: Dictionary with removed targets
      returned: always
      type: dict
      sample: {'targets_removed': {'2': ['target_00.rps', 'target_10.rps']}}
    triggers_removed:
      description: Dictionary with removed triggers
      returned: always
      type: dict
      sample: {'triggers_removed': {'2': ['trigger_00', 'trigger_00']}}
    tags_removed:
      description: Dictionary with removed tags
      returned: always
      type: dict
      sample: {'tags_removed': {'1': ['fourth_tag']}}
    tags_changed:
      description: Dictionary with changed tags
      returned: always
      type: dict
      sample: {'tags_changed': {'third_tag': 'second_tag'}}
'''

from moira_client import Moira
from ansible.module_utils.basic import AnsibleModule

class PropertiesHandler():

    def __init__(self, result = {}):

        self.result = result

    def tag_cleanup(self):

        tags_removed = []

        for tag in moira.tag.stats():
            if not tag.triggers:
                moira.tag.delete(tag.name)
                tags_removed.append(str(tag.name))

        self.result['tags_removed'] = {len(tags_removed): tags_removed}

    def tag_change(self, previous_tag, new_tag):

        for tag in moira.tag.stats():
            if tag.name == previous_tag:
                for every_trigger in tag.triggers:
                    trigger = moira.trigger.fetch_by_id(every_trigger.id)
                    trigger.tags.append(new_tag)
                    trigger.tags.remove(previous_tag)
                    trigger.update()

        self.result['tags_changed'] = {previous_tag: new_tag}

class TriggerHandler():

    def __init__(self, bodies = {}, failed = {}, result = {}):

        self.bodies = bodies
        self.failed = failed
        self.result = result

    def triggers_construct(self, trigger_template, trigger_body):

        to_modify = ['targets', 'tags']
        trigger_body_keys = list(trigger_body.keys())
        for i in range(len(trigger_body_keys)):
            instance = trigger_body_keys[i]
            self.bodies[instance] = {}
            self.bodies[instance].update(trigger_template)
            self.bodies[instance].update(trigger_body[instance])
            for j in to_modify:
                if j in self.bodies[instance].keys():
                    self.bodies[instance][j] = self.bodies[instance][j].replace(' ','').split(';')

    def triggers_save(self):

        exists = []

        for instance in self.bodies.keys():
            trigger_body = self.bodies[instance]
            trigger = moira.trigger.create(**trigger_body)
            if moira.trigger.is_exist(trigger):
                exists.append(trigger_body)
            else:
                try:
                    trigger.save()
                except Exception as error_body:
                    self.failed[trigger_body['name']] = {}
                    self.failed[trigger_body['name']].update(trigger_body)
                    self.failed[trigger_body['name']].update({'why_failed': error_body})

        if not(self.failed):
            self.result['triggers_saved'] = '100% of triggers has been saved successfully'
        else:
            self.result['triggers_saved'] = (str(round(100*(len(self.failed)/len(self.bodies)))) + '% of triggers has been failed to save: \n' + str(self.failed))

        self.result['already_exist'] = {len(exists): exists}

    def targets_remove(self, trigger_targets):

        targets_removed = []
        triggers_removed = []

        all_triggers = moira.trigger.fetch_all()

        for target in trigger_targets.values():
            for trigger in all_triggers:
                if target in trigger.targets:
                    trigger.targets.remove(target)
                    targets_removed.append(str(target))
                if not(trigger.targets):
                    moira.trigger.delete(trigger.id)
                    triggers_removed.append(str(trigger.name))
                else:
                    trigger.update()

        self.result['targets_removed'] = {len(targets_removed): targets_removed}
        self.result['triggers_removed'] = {len(triggers_removed): triggers_removed}

def main():

    fields = {
        'moira-server': {'type': 'str', 'required': True},
        'branch': {'type': 'dict', 'required': False},
        'leaves': {'type': 'dict', 'required': False},
        'fall': {'type': 'dict', 'required': False},
        'gardening': {'type': 'dict', 'required': False}
        }

    module = AnsibleModule(argument_spec=fields)
    global moira
    moira = Moira(module.params['moira-server'])
    trigger_handler = TriggerHandler()
    properties_handler = PropertiesHandler()

    if module.params['branch']:
        if module.params['leaves']:
            trigger_handler.triggers_construct(module.params['branch'], module.params['leaves'])
            trigger_handler.triggers_save()
        else:
            module.fail_json(msg='At least one leaf must be specified')

    if module.params['fall']:
        trigger_handler.targets_remove(module.params['fall'])

    if module.params['gardening']:
        if 'change' in module.params['gardening']:
            for previous_tag in module.params['gardening']['change'].keys():
                properties_handler.tag_change(previous_tag, module.params['gardening']['change'][previous_tag])
        if 'cleanup' in module.params['gardening']:
            properties_handler.tag_cleanup()

    results = trigger_handler.result.copy()
    results.update(properties_handler.result)
    module.exit_json(msg=results)

if __name__ == '__main__':
    main()
