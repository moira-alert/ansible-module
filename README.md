# ansible-module

Ansible module to create, update and delete Moira triggers based on [python-moira-client](https://github.com/moira-alert/python-moira-client)

## User Guide

[Installation](#installation)
- [Python Moira client](#python-moira-client)
- [Moira Trigger module](#moira-trigger-module)

[Module parameters](#module-parameters)
- [Required parameters](#required-parameters)
- [Static parameters](#static-parameters)
- [Dynamic parameters](#dynamic-parameters)
 
[Playbook tasks](#playbook-tasks)
- [Creating new triggers](#creating-new-triggers)
- [Changing existing triggers](#changing-existing-triggers)
- [Deleting triggers](#deleting-triggers)
 
[Playbook example](#playbook-example)

## <a name="installation"></a> Installation

### <a name="python-moira-client"></a> Python Moira client

Make sure you have [python-moira-client](https://github.com/moira-alert/python-moira-client) installed:

```
pip install moira-client
```

### <a name="moira-trigger-module"></a> Moira Trigger module
Clone ansible-module project inside your Ansible library directory specified in [ansible.cfg](http://docs.ansible.com/ansible/intro_configuration.html#library) file:

```
cd /path/to/library
git clone https://github.com/moira-alert/ansible-module moira_trigger
```
 
## <a name="module-parameters"></a> Module parameters

### <a name="required-parameters"></a> Required parameters

The parameters listed below are required to be specified for every task:

| Parameter | Description | Type | Required | Choices |
| ------ | ------ | ------ | ------ | ------ |
| api_url | Url of Moira API | String | True |
| state | Desired state of a trigger | String | True | present <br> absent |  | present |
| name | Trigger name | String | True |
| targets | List of trigger targets | List | True |

Any others can be used with their default values.

> **Note:** Both static and dynamic parameters can be specified for every trigger. 
See the difference between these two groups [here](#changing_existing_triggers).

### <a name="static-parameters"></a> Static parameters

| Parameter | Description | Type | Required | Choices | Default | Example |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| api_url | Url of Moira API | String | True | | | http://localhost/api/ |
| login | Auth Login (for 'X-Webauth-User' header) | String | False | | None | admin |
| auth_user | Auth User  (Basic Auth) | String | False | | None | admin |
| auth_pass | Auth Password  (Basic Auth) | String | False | | None | pass|
| state | Desired state of a trigger | String | True | present <br> absent |  | present |
| name | Trigger name | String | True | | | test1 |
| ttl | Time to Live (in seconds) | String | False | | '600' | '600' |
| ttl_state | Trigger state at the expiration of 'ttl' | String | False | NODATA <br> ERROR <br> WARN <br> OK | NODATA | WARN |
| targets | List of trigger targets | List | True | | | - test1.rps <br> - test2.rps |
| warn_value | Value to set WARN status | Int | False | | None | 300 |
| error_value | Value to set ERROR status | Int | False | | None | 600 |

### <a name="dynamic-parameters"></a> Dynamic parameters

| Parameter | Description | Type | Required |  Default | Example |
| ------ | ------ | ------ | ------ | ------ | ------ |
| desc | Trigger description | String | False | Empty String | trigger test description |
| expression | Python expression | String | False | Empty String | ERROR if t1 > 10 else WARN if t1 > 1 else OK |
| disabled_days | Days for trigger to be in silent mode | Set | False | {} | ? Mon <br> ? Wed |
| tags | List of trigger tags | List | False | [] | - first_tag <br> - second_tag |

## <a name="playbook-tasks"></a> Playbook tasks

### <a name="creating-new-triggers"></a> Creating new triggers
Use state 'present' to create and edit existing triggers:

```
 - name: MoiraAnsible
   moira_trigger:
      ...
      state: present
      ...  
```

> **Note:** See [required parameters](#required_parameters) section and [playbook example](#playbook_example) for more information.

### <a name="changing-existing-triggers"></a> Changing existing triggers

To remove any of the dynamic parameters from the existing trigger you can simply remove the related key from your playbook.

The table below shows which value be assigned to a parameter if the related key isn't specified within a playbook. 

| Parameter | Value to be assigned |
| ------ | ------ |
| Static | Last used value |
| Dynamic | Default value |

> **Note:** Since its name required to find existing trigger do not use state 'present' to change triggers names.
It's important to avoid multiple trigger creation with same parameters but different names. Triggers can be renamed by re-creation.

### <a name="deleting-triggers"></a> Deleting triggers

To delete existing triggers use state 'absent':

```
 - name: MoiraAnsible
   moira_trigger:
      ...
      state: absent
      ...  
```

## <a name="playbook-example"></a> Playbook example

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
