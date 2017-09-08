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
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
module: manageiq_automate_workspace
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.manageiq import ManageIQ, manageiq_argument_spec

class Workspace(object):
    """
        Object to modify and get the Workspace
    """

    def __init__(self, workspace, connection):
        self._object = workspace
        self._connection = connection

    def get(self):
        """
        Return the current Workspace object
        """
        return self._object['output']['workspace']

    def set_attribute(self, action_dict):
        """
        Set the attribute called on the object with the passed in value
        """
        object_name = action_dict.keys()[0]
        object, all = self._connection.get_object(object_name)
        all['workspace']['root'][action_dict.keys()[0]] = action_dict.values()[0]

        result = self._connection.set_object(all)

        return dict(changed=False, msg=result)


class StateVars(object):
    """
        Object to modify and get the StateVars
    """

    def __init__(self, state_vars, connection):
        self._object = state_vars
        self._connection = connection

    def get(self):
        """
        Return the current State Vars
        """
        return self._object['output']['state_vars']

class ManageIQAutomateWorkspace(object):
    """
        Object to execute automate workspace management operations in manageiq.
    """

    def __init__(self, manageiq, guid):
        self.manageiq = manageiq

        self.module = self.manageiq.module
        self.api_url = self.manageiq.api_url
        self.client = self.manageiq.client
        self._guid = guid

    def get_state_vars(self):
        """ Returns the current state_vars as looked up via the guid.

        Returns:
            the json representation of the current automate state_vars.
        """

        try:
            url = '%s/automate_workspaces/%s' % (self.api_url, self._guid)
            result = self.client.get(url)
            state_vars = StateVars(result, self).get()
        except Exception as e:
            self.module.fail_json(msg="failed to find the automate state_vars %s" % (str(e)))

        return dict(changed=False, msg=state_vars)

    def get_workspace(self):
        """ Returns the current workspace as looked up via the guid.

        Returns:
            the json representation of the current automate workspace.
        """

        try:
            url = '%s/automate_workspaces/%s' % (self.api_url, self._guid)
            result = self.client.get(url)
            workspace = Workspace(result, self)
        except Exception as e:
            self.module.fail_json(msg="failed to find the automate workspace %s" % (str(e)))

        return workspace

    def get_object(self, name):
        url = '%s/automate_workspaces/%s' % (self.api_url, self._guid)
        result = self.client.get(url)
        return result['output']['workspace'][name], result['output']

    def set_object(self, obj):
        url = '%s/automate_workspaces/%s' % (self.api_url, self._guid)
        result = self.client.post(url, action='edit', resource=obj)
        return result





def main():
    module = AnsibleModule(
            argument_spec=dict(
                manageiq_connection=dict(required=True, type='dict',
                                         options=manageiq_argument_spec()),
                guid=dict(required=True, type='str'),
                workspace=dict(required=False, type='dict'),
                state_vars = dict(required=False, type='dict')
                ),
            )

    guid = module.params['guid']
    workspace = module.params['workspace']
    workspace_actions = workspace.keys()
    state_vars = module.params['state_vars']

    manageiq = ManageIQ(module)
    manageiq_automate_workspace = ManageIQAutomateWorkspace(manageiq, guid)

    if manageiq_automate_workspace:
        if workspace and workspace_actions:
            for action in workspace_actions:
                workspace_sandbox = manageiq_automate_workspace.get_workspace()
                res_args = getattr(workspace_sandbox, action)(workspace[action])
    else:
        res_args = module.fail_json(msg="failed to return the automate workspace")

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()
