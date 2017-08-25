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

    def get_workspace(self):
        """ Returns the current workspace as looked up via the guid.

        Returns:
            the json representation of the current automate workspace.
        """

        try:
            url = self.api_url+'/automate_workspaces/'+self._guid
            result = self.client.get(url)
        except Exception as e:
            self.module.fail_json(msg="failed to find the automate workspace %s" % (str(e)))

        return dict(changed=False, msg=result)

def main():
    module = AnsibleModule(
            argument_spec=dict(
                manageiq_connection=dict(required=True, type='dict',
                                         options=manageiq_argument_spec()),
                guid=dict(required=True, type='str')
                ),
            )

    guid = module.params['guid']

    manageiq = ManageIQ(module)
    manageiq_automate_workspace = ManageIQAutomateWorkspace(manageiq, guid)

    if manageiq_automate_workspace:
        res_args = manageiq_automate_workspace.get_workspace()
    else:
        res_args = module.fail_json(msg="failed to return the automate workspace")

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()
