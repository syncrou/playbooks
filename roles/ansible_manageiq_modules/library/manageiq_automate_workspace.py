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

    def __init__(self, workspace):
        self._object = workspace

    def get(self):
        """
        Return the current Workspace
        """
        return self._object['output']['workspace']

class StateVars(object):
    """
        Object to modify and get the StateVars
    """

    def __init__(self, state_vars):
        self._object = state_vars

    def get(self):
        """
        Return the current State Vars
        """
        return self._object['output']['state_vars']

class ManageIQAutomateWorkspace(object):
    """
        Object to execute automate workspace management operations in manageiq.
    """

    def __init__(self, manageiq, guid, workspace_params, state_vars_params):
        self.manageiq = manageiq

        self.module = self.manageiq.module
        self.api_url = self.manageiq.api_url
        self.client = self.manageiq.client
        self._guid = guid
        self._workspace = workspace_params
        self._state_vars = state_vars_params

    def get_state_vars(self):
        """ Returns the current state_vars as looked up via the guid.

        Returns:
            the json representation of the current automate state_vars.
        """

        try:
            url = '%s/automate_workspaces/%s' % (self.api_url, self._guid)
            result = self.client.get(url)
            state_vars = StateVars(result).get()
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
            workspace = Workspace(result).get()
        except Exception as e:
            self.module.fail_json(msg="failed to find the automate workspace %s" % (str(e)))

        return dict(changed=False, msg=workspace)




def main():
    module = AnsibleModule(
            argument_spec=dict(
                manageiq_connection=dict(required=True, type='dict',
                                         options=manageiq_argument_spec()),
                guid=dict(required=True, type='str'),
                workspace=dict(required=False, type='str'),
                state_vars = dict(required=False, type='dict')
                ),
            )

    guid = module.params['guid']
    workspace = module.params['workspace']
    state_vars = module.params['state_vars']

    manageiq = ManageIQ(module)
    manageiq_automate_workspace = ManageIQAutomateWorkspace(manageiq, guid, workspace, state_vars)

    if manageiq_automate_workspace:
        res_args = manageiq_automate_workspace.get_workspace()
    else:
        res_args = module.fail_json(msg="failed to return the automate workspace")

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()
