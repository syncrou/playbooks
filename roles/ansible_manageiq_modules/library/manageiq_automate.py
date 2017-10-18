#! /usr/bin/python
#
# (c) 2017, Drew Bomhof <dbomhof@redhat.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import (absolute_import, division, print_function)
import os

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
module: manageiq_automate
'''
import dpath.util
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.manageiq import ManageIQ

class ManageIQAutomate(object):
    """
        Object to execute automate workspace management operations in manageiq.
    """

    def __init__(self, manageiq, workspace):
        self._manageiq = manageiq
        self._target = workspace

        self._module = self._manageiq.module
        self._api_url = self._manageiq.api_url
        self._client = self._manageiq.client
        self._error = None


    def url(self):
        """
            The url to connect to the workspace
        """
        url_str = self._manageiq.module.params['manageiq_connection']['automate_workspace']
        return self._api_url + '/' + url_str


    def get(self):
        """
            Get any attribute, object from the REST API
        """
        result = self._client.get(self.url())
        return dict(result=result)


    def set(self, data):
        """
            Set any attribute, object from the REST API
        """
        result = self._client.post(self.url(), action='edit', resource=data)
        return  result


    def exists(self, path):
        """
            Validate all passed objects before attempting to set or get values from them
        """

        try:
            return bool(dpath.util.get(self._target, path, '|'))
        except KeyError as error:
            return False


class Workspace(ManageIQAutomate):
    """
        Object to modify and get the Workspace
    """

    def object_exists(self, dict_options):
        search_path = "workspace|result|input|objects|" + dict_options['object']
        if self.exists(search_path):
            return dict(changed=False, value=True)
        return dict(changed=False, value=False)


    def attribute_exists(self, dict_options):
        obj = dict_options['object']
        attribute = dict_options['attribute']
        path = "workspace|result|input|objects"
        search_path = "|".join([path, obj, attribute])
        if self.exists(search_path):
            return dict(changed=False, value=True)
        return dict(changed=False, value=False)


    def state_var_exists(self, dict_options):
        attribute = dict_options['attribute']
        path = "workspace|result|input|state_vars"
        search_path = "|".join([path, attribute])
        if self.exists(search_path):
            return dict(changed=False, value=True)
        return dict(changed=False, value=False)


    def method_parameter_exists(self, dict_options):
        parameter = dict_options['parameter']
        path = "workspace|result|input|method_parameters"
        search_path = "|".join([path, parameter])
        if self.exists(search_path):
            return dict(changed=False, value=True)
        return dict(changed=False, value=False)


    def get_attribute(self, dict_options):
        """
            Get the passed in attribute from the Workspace
        """

        if self.attribute_exists(dict_options):
            return_value = self._target['workspace']['result']['input']['objects'][dict_options['object']][dict_options['attribute']]

            return dict(changed=False, value=return_value)
        else:
            self._module.fail_json(msg='Object %s Attribute %s does not exist' % (dict_options['object'], dict_options['attribute']))


    def get_state_var(self, dict_options):
        """
            Get the passed in state_var from the Workspace
        """
        return_value = None

        if self.state_var_exists(dict_options):
            return_value = self._target['workspace']['result']['input']['state_vars'][dict_options['attribute']]

            return dict(changed=False, value=return_value)
        else:
            self._module.fail_json(msg='State Var %s does not exist' % dict_options['attribute'])


    def get_method_parameter(self, dict_options):
        """
            Get the passed in state_var from the Workspace
        """
        return_value = None

        if self.method_parameter_exists(dict_options):
            return_value = self._target['workspace']['result']['input']['method_parameters'][dict_options['parameter']]

            return dict(changed=False, value=return_value)
        else:
            self._module.fail_json(msg='Method Parameter %s does not exist' % dict_options['parameter'])

    def get_object_names(self):
        return_value = self._target['workspace']['result']['input']['objects'].keys()
        return dict(changed=False, value=return_value)


    def get_object_attribute_names(self, dict_options):
        if self.object_exists(dict_options):
            return_value = self._target['workspace']['result']['input']['objects'][dict_options['object']].keys()
            return dict(changed=False, value=return_value)
        else:
            self._module.fail_json(msg='Object %s does not exist' % dict_options['object'])


    def set_state_var(self, dict_options):
        """
            Set the state_vars called with the passed in value
        """

        new_attribute = dict_options['attribute']
        new_value = dict_options['value']
        self._target['workspace']['result']['input']['state_vars'][new_attribute] = new_value
        self._target['workspace']['result']['output']['state_vars'][new_attribute] = new_value
        return dict(changed=True, workspace=self._target['workspace'])


    def set_attribute(self, dict_options):
        """
            Set the attribute called on the object with the passed in value
        """

        new_attribute = dict_options['attribute']
        new_value = dict_options['value']
        obj = dict_options['object']
        if self.object_exists(dict_options):
            self._target['workspace']['result']['input']['objects'][obj][new_attribute] = new_value
            new_dict = {obj:{new_attribute: new_value}}
            self._target['workspace']['result']['output']['objects'] = new_dict
            return dict(changed=True, workspace=self._target['workspace'])
        else:
            msg = 'Failed to set the attribute %s with value %s for %s' % (new_attribute, new_value, obj)
            self._module.fail_json(msg=msg, changed=False)


    def commit_workspace(self):
        """
            Commit the workspace
        """
        workspace = self.set(self._target['workspace']['result']['output'])
        return dict(changed=True, workspace=workspace)


    def commit_attribute(self, dict_options):
        """
            Commit the attribute called on the object with the passed in value
        """
        workspace = self.set_attribute(dict_options)
        self.commit_workspace()
        return workspace


    def commit_state_var(self, dict_options):
        """
            Commit the attribute called on the object with the passed in value
        """
        workspace = self.set_state_var(dict_options)
        self.commit_workspace()
        return workspace


    def get_workspace(self):
        """
            Get the entire Workspace
        """

        workspace = self.get()
        workspace['result']['output'] = dict()
        workspace['result']['output']['objects'] = dict()
        workspace['result']['output']['state_vars'] = dict()

        return dict(changed=False, workspace=workspace)


def manageiq_argument_spec():
    return dict(
        url=dict(default=os.environ.get('MIQ_URL', None)),
        username=dict(default=os.environ.get('MIQ_USERNAME', None)),
        password=dict(default=os.environ.get('MIQ_PASSWORD', None), no_log=True),
        token=dict(default=os.environ.get('MIQ_TOKEN', None), no_log=True),
        automate_workspace=dict(default=None, type='str', no_log=True),
        group=dict(default=None, type='str'),
        X_MIQ_Group=dict(default=None, type='str'),
        verify_ssl=dict(default=True, type='bool'),
        ca_bundle_path=dict(required=False, default=None),
    )


def main():
    """
        The entry point to the ManageIQ Automate module
    """
    module = AnsibleModule(
            argument_spec=dict(
                manageiq_connection=dict(required=True, type='dict',
                                         options=manageiq_argument_spec()),
                get_workspace=dict(type='bool', default=False),
                commit_workspace=dict(type='bool', default=False),
                set_attribute=dict(required=False, type='dict'),
                object_exists=dict(required=False, type='str'),
                attribute_exists=dict(required=False, type='dict'),
                state_var_exists=dict(required=False, type='dict'),
                method_parameter_exists=dict(required=False, type='dict'),
                commit_attribute=dict(required=False, type='dict'),
                commit_state_var=dict(required=False, type='dict'),
                get_attribute=dict(required=False, type='dict'),
                get_state_var=dict(required=False, type='dict'),
                get_method_parameter=dict(required=False, type='dict'),
                set_state_var=dict(required=False, type='dict'),
                get_object_names=dict(required=False, type='bool'),
                get_state_var_names=dict(required=False, type='bool'),
                get_method_parameter_names=dict(required=False, type='bool'),
                get_object_attribute_names=dict(required=False, type='dict'),
                workspace=dict(required=False, type='dict')
                ),
            )

    argument_opts = {
        'get_attribute':module.params['get_attribute'],
        'get_method_parameter':module.params['get_method_parameter'],
        'get_state_var':module.params['get_state_var'],
        'get_object_attribute_names':module.params['get_object_attribute_names'],
        'object_exists':module.params['object_exists'],
        'method_parameter_exists':module.params['method_parameter_exists'],
        'attribute_exists':module.params['attribute_exists'],
        'state_var_exists':module.params['state_var_exists'],
        'set_attribute':module.params['set_attribute'],
        'set_state_var':module.params['set_state_var'],
        'commit_attribute':module.params['commit_attribute'],
        'commit_state_var':module.params['commit_state_var'],
        }

    boolean_opts = {
        'get_object_names':module.params['get_object_names'],
        'commit_workspace':module.params['commit_workspace'],
        'get_workspace':module.params['get_workspace'],
        }

    manageiq = ManageIQ(module)
    workspace = Workspace(manageiq, module.params['workspace'])

    for key, value in boolean_opts.iteritems():
        if value:
            result = getattr(workspace, key)()
            module.exit_json(**result)
    for key, value in argument_opts.iteritems():
        if value:
            result = getattr(workspace, key)(value)
            module.exit_json(**result)


    module.fail_json(msg="No workspace found")


if __name__ == "__main__":
    main()
