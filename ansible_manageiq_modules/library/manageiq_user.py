#!/usr/bin/python
#
# (c) 2017, Daniel Korn <korndaniel1@gmail.com>
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
#


DOCUMENTATION = '''
---
module: manageiq_user
description: The manageiq_user module supports adding, updating and deleting users in ManageIQ.
short_description: management of users in ManageIQ
requirements: [ ManageIQ/manageiq-api-client-python ]
author: Daniel Korn (@dkorn)
options:
  miq_url:
    description:
      - the manageiq environment url
    default: MIQ_URL env var if set. otherwise, it is required to pass it
  miq_username:
    description:
      - manageiq username
    default: MIQ_USERNAME env var if set. otherwise, it is required to pass it
  miq_password:
    description:
      - manageiq password
    default: MIQ_PASSWORD env var if set. otherwise, it is required to pass it
  name:
    description:
      - the unique userid in manageiq, often mentioned as username
    required: true
    default: null
  fullname:
    description:
      - the users' full name
    required: false
    default: null
  password:
    description:
      - the users' password
    required: false
    default: null
  group:
    description:
      - the name of the group to which the user belongs
    required: false
    default: null
  email:
    description:
      - the users' E-mail address
    required: false
    default: null
  state:
    description:
      - the state of the user
      - On present, it will create the user if it does not exist or update the
        user if the associated data is different
      - On absent, it will delete the user if it exists
    required: False
    choices: ['present', 'absent']
    default: 'present'
  miq_verify_ssl:
    description:
      - whether SSL certificates should be verified for HTTPS requests
    required: false
    default: True
    choices: ['True', 'False']
  ca_bundle_path:
    description:
      - the path to a CA_BUNDLE file or directory with certificates
    required: false
    default: null
'''

EXAMPLES = '''
# Create a new user in ManageIQ
  manageiq_user:
    name: 'dkorn'
    fullname: 'Daniel Korn'
    password: '******'
    group: 'EvmGroup-user'
    email: 'dkorn@redhat.com'
    state: 'present'
    miq_url: 'http://localhost:3000'
    miq_username: 'admin'
    miq_password: '******'
    miq_verify_ssl: False
'''

import manageiq_utils


class ManageIQUser(object):
    """
        object to execute user management operations in manageiq
    """

    def __init__(self):
        self.changed = False

    def delete_user(self, manageiq, userid):
        """Deletes the user from manageiq.

        Returns:
            a short message describing the operation executed.
        """
        user = manageiq.find_collection_resource_by('users', userid=userid)
        if not user:  # user doesn't exist
            return dict(
                changed=self.changed,
                msg="User {userid} does not exist in manageiq".format(userid=userid))
        try:
            url = '{api_url}/users/{user_id}'.format(api_url=manageiq.api_url, user_id=user['id'])
            result = manageiq.client.post(url, action='delete')
            self.changed = True
            return dict(changed=self.changed, msg=result['message'])
        except Exception as e:
            manageiq.module.fail_json(msg="Failed to delete user {userid}: {error}".format(userid=userid, error=e))

    def user_update_required(self, user, username, group_id, email):
        """ Returns True if the username, group id or email passed for the user
            differ from the user's existing ones, False otherwise.
        """
        if username is not None and user['name'] != username:
            return True
        if group_id is not None and user['current_group_id'] != group_id:
            return True
        if email is not None and user.get('email') != email:
            return True
        return False

    def update_user_if_required(self, manageiq, user, userid, username, group_id, password, email):
        """Updates the user in manageiq.

        Returns:
            the created user id, name, created_on timestamp,
            updated_on timestamp, userid and current_group_id
        """
        if not self.user_update_required(user, username, group_id, email):
            return dict(
                changed=self.changed,
                msg="User {userid} already exist, no need for updates".format(userid=userid))
        url = '{api_url}/users/{user_id}'.format(api_url=self.api_url, user_id=user.id)
        resource = {'userid': userid, 'name': username, 'password': password,
                    'group': {'id': group_id}, 'email': email}
        try:
            result = manageiq.client.post(url, action='edit', resource=resource)
        except Exception as e:
            manageiq.module.fail_json(msg="Failed to update user {userid}: {error}".format(userid=userid, error=e))
        self.changed = True
        return dict(
            changed=self.changed,
            msg="Successfully updated the user {userid}: {user_details}".format(userid=userid, user_details=result))

    def create_user(self, manageiq, userid, username, group_id, password, email):
        """Creates the user in manageiq.

        Returns:
            the created user id, name, created_on timestamp,
            updated_on timestamp, userid and current_group_id
        """
        url = '{api_url}/users'.format(api_url=manageiq.api_url)
        resource = {'userid': userid, 'name': username, 'password': password,
                    'group': {'id': group_id}, 'email': email}
        try:
            result = manageiq.client.post(url, action='create', resource=resource)
        except Exception as e:
            manageiq.module.fail_json(msg="Failed to create user {userid}: {error}".format(userid=userid, error=e))
        self.changed = True
        return dict(
            changed=self.changed,
            msg="Successfully created the user {userid}: {user_details}".format(userid=userid, user_details=result['results']))

    def create_or_update_user(self, manageiq, userid, username, password, group, email):
        """ Create or update a user in manageiq.

        Returns:
            Whether or not a change took place and a message describing the
            operation executed.
        """
        group = manageiq.find_collection_resource_by('groups', description=group)
        if not group:  # group doesn't exist
            manageiq.module.fail_json(
                msg="Failed to create user {userid}: group {group_name} does not exist in manageiq".format(userid=userid, group_name=group))

        user = manageiq.find_collection_resource_by('users', userid=userid)
        if user:  # user already exist
            return self.update_user_if_required(manageiq, user, userid, username, group['id'], password, email)
        else:
            return self.create_user(manageiq, userid, username, group['id'], password, email)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            manageiq_utils.manageiq_argument_spec(),
            name=dict(required=True, type='str'),
            fullname=dict(required=False, type='str'),
            password=dict(required=False, type='str', no_log=True),
            group=dict(required=False, type='str'),
            email=dict(required=False, type='str'),
            state=dict(required=False, type='str',
                       choices=['present', 'absent'], defualt='present'),
        ),
        required_if=[
            ('state', 'present', ['fullname', 'group', 'password'])
        ],
    )

    name     = module.params['name']
    fullname = module.params['fullname']
    password = module.params['password']
    group    = module.params['group']
    email    = module.params['email']
    state    = module.params['state']

    manageiq = manageiq_utils.ManageIQ(module)
    manageiq_user = ManageIQUser()
    if state == "present":
        res_args = manageiq_user.create_or_update_user(manageiq, name, fullname,
                                                       password, group, email)
    if state == "absent":
        res_args = manageiq_user.delete_user(manageiq, name)

    module.exit_json(**res_args)


# Import module bits
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()