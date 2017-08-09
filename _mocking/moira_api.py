'''Mock moira_api'''

class _MethodsCalls():

    '''Methods calls'''

    def __init__(self,
                 trace=''):

        self.trace = trace


class _TriggerBody(object):

    '''Mock trigger'''

    def __init__(self,
                 name=None,
                 desc=None,
                 tags=None,
                 targets=None,
                 id=None,
                 other_param=None):

        self.name = name
        self.desc = desc
        self.tags = tags
        self.targets = targets
        self.id = id
        self.other_param = other_param

    def save(self):

        '''Mock moira_client.models.trigger.Trigger.save'''

        self.id = 'gh0st'
        methods_calls.trace += '.save'

    @staticmethod
    def update():

        '''Mock moira_client.models.trigger.Trigger.update'''

        methods_calls.trace += '.update'


class _Trigger(object):

    '''Mock api methods'''

    @staticmethod
    def fetch_all():

        '''Mock moira.trigger.fetch_all'''

        all_triggers = []
        if trigger_body.id is not None:
            all_triggers.append(trigger_body)
        methods_calls.trace += '.fetch_all'
        return all_triggers

    @staticmethod
    def delete(trigger_id):

        '''Mock moira.trigger.delete'''

        trigger_body.id = None
        methods_calls.trace += '.delete'

    @staticmethod
    def fetch_by_id(trigger_id):

        '''Mock moira.trigger.fetch_by_id'''

        methods_calls.trace += '.fetch_by_id'
        return trigger_body

    @staticmethod
    def create(**kwargs):

        '''Mock moira.trigger.create'''

        methods_calls.trace += '.create'
        return trigger_body

methods_calls = _MethodsCalls()
trigger_body = _TriggerBody()
trigger = _Trigger()