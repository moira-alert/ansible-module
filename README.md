# ansible-module
Ansible module to create, update and delete Moira triggers based on [python-moira-client](https://github.com/moira-alert/python-moira-client)

# Create new triggers
Simply use 'branch' inside your playbook task to pass parameters you'd like every trigger to obtain:
```
     branch:
       desc: all triggers test description
       warn_value: 300
       error_value: 600
       tags: first_tag; second_tag
       ttl_state: ERROR
```
and 'leaves' to create different triggers based on 'branch':
```
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
```
Since Ansible supports jinja2 expressions, you can also customize every parameter as you want to.

# Change trigger parameteres
Use 'gardening' to change trigger's tags:
```
     gardening:
       change:
         third_tag: second_tag
```
and purge unusual tags left after removed triggers:
```
     gardening:
       cleanup: True
```

# Delete triggers
To remove instance from monitoring it's enough to specify its targets inside the 'fall':
```
     fall:
       target_0: target_30.rps
       target_1: target_31.rps
```
After procedure of targets removal, function finds and removes triggers with no targets left.

Feel free to use only 'branch/leaves' or only 'fall' or only 'gardening' inside one task.
