'''Test moira_trigger'''

import unittest
import warnings
from _mocking import ansible_pkg, moira_api
from moira_trigger import MoiraAnsible, HAS_MOIRA_CLIENT

test_trigger = {
    'name': 'test',
    'targets': ['target1', 'target2'],
    'desc': 'test desc',
    'tags': ['tag1', 'tag2']}

test_trigger_name = test_trigger['name']

moira_ansible = MoiraAnsible(moira_api)


class TestMoiraAnsible(unittest.TestCase):

    '''Test MoiraAnsible from moira_trigger'''

    @staticmethod
    def _clear_data():

        '''Clear data for next iterations'''

        moira_api.trigger_body.id = None
        moira_api.methods_calls.trace = ''

    def test_moira_client(self):

        '''Test if moira_client has all required methods'''

        result = set()
        trigger_save_attributes = 'save', 'update'
        trigger_edit_attributes = 'fetch_all', 'fetch_by_id', \
                                  'create', 'delete'

        if HAS_MOIRA_CLIENT:

            import moira_client
            moira = moira_client.Moira('http://test/')

            for save_attribute in trigger_save_attributes:
                result.add(
                    hasattr(moira_client.models.trigger.Trigger,
                            save_attribute))

            for edit_attribute in trigger_edit_attributes:
                result.add(
                    hasattr(moira.trigger,
                            edit_attribute))

            del moira_client

        else:

            warnings.warn('module not found: moira_client')

        self.assertNotIn(bool(0), result)

    def test_trigger_create(self):

        '''Create new trigger'''

        moira_ansible.trigger_customize(test_trigger, 'present')

        self.assertIn(
            'new trigger created',
            moira_ansible.success[test_trigger_name])
        self.assertFalse(moira_ansible.failed)

        if not moira_ansible.dry_run:
            self.assertEqual(moira_api.methods_calls.trace,
                             '.fetch_all.create.save.update')

        else:
            self.assertEqual(moira_api.methods_calls.trace,
                             '.fetch_all.create')

        self._clear_data()

    def test_trigger_update(self):

        '''Update existing trigger'''

        moira_ansible.trigger_customize(test_trigger, 'present')
        del moira_ansible.success[test_trigger_name]
        test_trigger.update({'other_param': 'other_value'})

        moira_ansible.trigger_customize(test_trigger, 'present')

        self.assertIn(
            'other_param',
            moira_api.trigger_body.__dict__)
        self.assertFalse(moira_ansible.failed)

        if not moira_ansible.dry_run:
            self.assertIn(
                'trigger changed',
                moira_ansible.success[test_trigger_name])
            self.assertEqual(moira_api.methods_calls.trace,
                             '.fetch_all.create.save.update.fetch_all.fetch_by_id.update')

        else:
            self.assertEqual(moira_api.methods_calls.trace,
                             '.fetch_all.create.fetch_all.create')
        self._clear_data()

    def test_trigger_delete(self):

        '''Remove existing trigger'''

        moira_ansible.trigger_customize(test_trigger, 'present')
        moira_ansible.trigger_customize(test_trigger, 'absent')

        self.assertFalse(moira_ansible.failed)

        if not moira_ansible.dry_run:
            self.assertIn(
                'trigger removed',
                moira_ansible.success[test_trigger_name])
            self.assertEqual(moira_api.methods_calls.trace,
                             '.fetch_all.create.save.update.fetch_all.delete')

        else:
            self.assertEqual(moira_api.methods_calls.trace,
                             '.fetch_all.create.fetch_all')

        self._clear_data()

    def test_no_id_found(self):

        '''No trigger found to remove'''

        moira_ansible.trigger_customize(test_trigger, 'absent')

        self.assertIn(
            'no id found for trigger',
            moira_ansible.success[test_trigger_name])
        self.assertFalse(moira_ansible.failed)
        self.assertEqual(moira_api.methods_calls.trace,
                         '.fetch_all')

        self._clear_data()

    def test_dry_run(self):

        '''Check mode'''

        moira_ansible.dry_run = True

        self.test_no_id_found()
        self.test_trigger_delete()
        self.test_trigger_update()
        self.test_trigger_create()


if __name__ == '__main__':
    unittest.main()
