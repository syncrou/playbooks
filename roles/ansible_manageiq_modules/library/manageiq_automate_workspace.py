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

class VM(object):
    """
        Return a VM
    """

    def __init__(self, manageiq, resource):
        self.manageiq = manageiq

        self.module = self.manageiq.module
        self.api_url = self.manageiq.api_url
        self.client = self.manageiq.client
        #self._resource = resource[resource.keys()[0]].values()[0]
        self._id = resource.split("::")[-1].split("/")[-1]

    def get(self, return_object=False):
        #id = self._resource.split("::")[-1].split("/")[-1]
        #vms = self.client.collections.__getattribute__('vms').get(id=id)
        vm = self.manageiq.find_collection_resource_by('vms', id=self._id)
        #vm = self.client.get(vms._href)
        #if return_object:
        #    return vm
        #else:
        #return dict(changed=False, msg=vm['_action'])
        return vm['_data']

    def action(self, method='start'):
        entity = self.get(True)
        start_action_url = entity['actions'][6]['href']
        return dict(changed=False, msg=start_action_url)


class Workspace(object):
    """
        Object to modify and get the Workspace
    """

    def __init__(self, workspace):
        self._object = workspace
        #self._connection = connection
        #self._manageiq = manageiq
        #self._manageiq.module.fail_json(msg=workspace)
        #self._attributes = self.lookup_attributes(attributes)

    #def lookup_attributes(self, target):
    #    vm = VM(self._manageiq, self._object['input']['workspace']['root']['vm']).get()
    #    self._object['output']['workspace']['root']['vm'] = vm

    def get(self):
        """
            Return the current Workspace object
        """
        return self._object['output']['workspace']

    def set_attribute(self, action_dict):
        """
        Set the attribute called on the object with the passed in value
        """
        object_name = action_dict.keys()[1]
        self._object['output']['workspace'][action_dict.keys()[0]] = action_dict.values()[0]
        result = self._object

        return dict(changed=False, object=result)


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
            vm = VM(self.manageiq, result['input']['workspace']['root']['vm']).get()
            result['input']['workspace']['root']['vm'] = vm
            #workspace = Workspace(result, self.manageiq, self)
        except Exception as e:
            self.module.fail_json(msg="failed to find the automate workspace %s" % (str(e)))

        return dict(changed=False, object=result)

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
                manageiq_connection=dict(required=False, type='dict',
                                         options=manageiq_argument_spec()),
                guid=dict(required=False, type='str'),
                get_workspace=dict(required=False, type='dict'),
                vmdb_object=dict(required=False, type='dict'),
                state_vars=dict(required=False, type='dict'),
                set_attribute=dict(required=False, type='dict'),
                start_vm=dict(required=False, type='dict'),
                add_attributes=dict(required=False, type='dict'),
                set_workspace=dict(required=False, type='dict')

                ),
            )

    guid = module.params['guid']
    if 'get_workspace' in module.params.keys():
        get_workspace = True

    set_attribute = module.params['set_attribute']
    vmdb_object = module.params['vmdb_object']
    start_vm = module.params['start_vm']
    add_attributes = module.params['add_attributes']
    set_workspace = module.params['set_workspace']
    try:
        workspace_actions = set_attribute.keys()
    except Exception as e:
        workspace_actions = None
    state_vars = module.params['state_vars']

    try:
        manageiq = ManageIQ(module)
        manageiq_automate_workspace = ManageIQAutomateWorkspace(manageiq, guid)
    except Exception as e:
        manageiq_automate_workspace = None

    if set_attribute and workspace_actions:
        res_args = Workspace(set_attribute['target']).set_attribute(set_attribute)
    elif vmdb_object:
        res_args = vmdb_object['target']['input']['workspace']['root']['vm']
    elif manageiq_automate_workspace:
        if start_vm:
            result = manageiq.client.post(start_vm['href'], action='start')
            res_args = result
        elif add_attributes:
            url = add_attributes['vm']['href']+"/custom_attributes"
            resources = [dict(name=add_attributes['custom_attributes'].keys()[0], value=add_attributes['custom_attributes'].values()[0])]
            result = manageiq.client.post(url, action='add', resources=resources)
            res_args = result
        elif set_workspace:
            url = '%s/automate_workspaces/%s' % ('http://localhost:3000/api', guid)
            workspace = set_workspace['output']
            res_args = manageiq.client.post(url, action='edit', resource=workspace)
        elif get_workspace:
            res_args = manageiq_automate_workspace.get_workspace()

    else:
        res_args = module.fail_json(msg="failed to return the automate workspace")

    module.exit_json(**res_args)


if __name__ == "__main__":
    main()
