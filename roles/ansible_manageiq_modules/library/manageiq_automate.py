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
        self._guid = self._parse_for_guid()
        self._target = workspace

        self._module = self._manageiq.module
        self._api_url = self._manageiq.api_url
        self._client = self._manageiq.client
        self._error = None

    def _parse_for_guid(self):
        """
            Grab the guid from the automate_workspace parameter
        """
        #url_str = self._manageiq.module.params['automate_workspace']
        url_str = self._manageiq.module.params['manageiq_connection']['automate_workspace']
        return url_str.split("/")[1]

    def url(self):
        """
            The url to connect to the workspace
        """
        return '%s/automate_workspaces/%s' % ('http://localhost:3000/api', self._guid)


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


    def validate(self, obj, path, attribute=None):
        """
            Validate all passed objects before attempting to set or get values from them
        """

        if attribute is None:
            search_path = '|'.join([path, obj])
        else:
            search_path = '|'.join([path, obj, attribute])
        try:
            return bool(dpath.util.get(self._target, search_path, '|'))
        except KeyError as error:
            self._error = str(error)
            return False



class Workspace(ManageIQAutomate):
    """
        Object to modify and get the Workspace
    """

    def set_attribute(self, items):
        """
            Set the attribute called on the object with the passed in value
        """

        new_attribute = items['attribute']
        new_value = items['value']
        obj = items['object']
        search_path = "workspace|result|input|objects"
        if self.validate(obj, search_path):
            self._target['workspace']['result']['output']['objects'][obj][new_attribute] = new_value
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

    def get_workspace(self):
        """
            Get the entire Workspace
        """

        workspace = self.get()
        return dict(changed=False, workspace=workspace)


    def get_attribute(self, attribute):
        """
            Get the passed in attribute from the Workspace
        """

        findable_attribute = attribute['attribute']
        obj = attribute['object']
        search_path = "workspace|result|input|objects"
        return_value = None

        if self.validate(findable_attribute, obj, search_path):
            return_value = self._target['workspace']['result']['input']['objects'][obj][findable_attribute]

            return dict(changed=False, value=return_value)
        else:
            self._module.fail_json(msg='Validation failed on: %s' % self._error)


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
        The entry point to the module
    """
    module = AnsibleModule(
            argument_spec=dict(
                manageiq_connection=dict(required=True, type='dict',
                                         options=manageiq_argument_spec()),
                get_workspace=dict(type='bool', default=False),
                commit_workspace=dict(type='bool', default=False),
                set_attribute=dict(required=False, type='dict'),
                get_attribute=dict(required=False, type='dict'),
                workspace=dict(required=False, type='dict')
                ),
            )

    get_attribute = module.params['get_attribute']
    get_workspace = module.params.get('get_workspace')
    commit_workspace = module.params.get('commit_workspace')
    set_attribute = module.params['set_attribute']
    workspace_arg = module.params['workspace']

    manageiq = ManageIQ(module)
    workspace = Workspace(manageiq, workspace_arg)

    result = None
    if get_workspace:
        result = workspace.get_workspace()
        module.exit_json(**result)
    elif commit_workspace:
        result = workspace.commit_workspace()
        module.exit_json(**result)
    for key, value in dict(get_attribute=get_attribute, set_attribute=set_attribute).iteritems():
        if value:
            result = getattr(workspace, key)(value)
            module.exit_json(**result)


    module.fail_json(msg="No workspace found")


if __name__ == "__main__":
    main()
