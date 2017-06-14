# ansible-module
Ansible module to create, update and delete Moira triggers based on [python-moira-client](https://github.com/moira-alert/python-moira-client)

# Create new and edit existing triggers
To create or edit existing trigger in Moira use state 'present' inside playbook task.
Parameters values required to be specified:

 - api_url: Url of Moira API
 - state: Desired state of a trigger
 - name: Trigger name
 - targets: List of trigger targets
 
Any others will be used with their default values.
```
   - name: MoiraAnsible
     moira_trigger:
        api_url: http://localhost/api/
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
        with_items:
          - name: test1
            targets:
              - test1.rps
              - test2.rps
          - name: test2
            targets:
              - test3.rps
              - test4.rps

```
Note: Since its name required to find existing trigger do not use this state to change triggers names. 
It's important to avoid multiple trigger creation with same parameters but different names. Triggers can be renamed by re-creation. 

# Delete triggers
To delete existing triggers use state 'absent':
```
 - name: MoiraAnsible
   moira_trigger:
      ...
      state: absent
      ...  
```
# Advanced parameters
As in web application, you're also free to use advanced parameters like:

 - Python expressions:
```
 - name: MoiraAnsible
   moira_trigger:
      ...
      expression: ERROR if t1 > 10 else WARN if t1 > 1 else OK
      ...
```

 -  and days for trigger to be in silent mode:
```
 - name: MoiraAnsible
   moira_trigger:
      ...
      disabled_days:
        ? Mon
        ? Wed
      ...
```
specified as elements of a set in common yaml syntax.

# Dynamic parameters
Following paramaters are easily removeable:

 - desc: Trigger description
 - disabled_days: Days for trigger to be in silent mode
 - tags: List of trigger tags
 - expression: Python expression
 
 To remove any of the described parameters from existing trigger you can simply remove related key from your playbook.
