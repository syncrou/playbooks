#! /usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule
from manageiq_client.api import ManageIQClient as MiqApi

DOCUMENTATION = '''
---
module: ansible_manageiq_api
short_description: Interface to ManageIq Rest API
'''

EXAMPLES = '''
---
'''

class ManageIQ(object):
    """ ManageIQ object to execute various operations in manageiq
    url            - manageiq environment url
    user           - the username in manageiq
    password       - the user password in manageiq
    token          - the miq_token if it exists
    miq_verify_ssl - whether SSL certificates should be verified for HTTPS requests
    ca_bundle_path - the path to a CA_BUNDLE file or directory with certificates
    endpoint       - the endpoint path to lookup via the ManageIQ REST API
    """

    WAIT_TIME = 5
    ITERATIONS = 10

    def __init__(self, module, url, user, password, state, miq_verify_ssl, ca_bundle_path, endpoint, token):
        self.module = module
        self.api_url = url + '/api'
        self.user = user
        self.password = password
        self.token = token
        self.client =  self._build_client(miq_verify_ssl, ca_bundle_path)
        self.changed = False
        self.state = state
        self.endpoint = endpoint

    def results(self):
        result = self.client.get(self.api_url + '/' + self.endpoint + '/')
        response = {}
        for item in result['resources']:
            thing = self.client.get(item['href'])
            response[self.endpoint + "_" + str(thing['id'])] = thing
        return response

    def _build_client(self, miq_verify_ssl, ca_bundle_path):
        auth = None
        if self.token:
            auth = dict(token=self.token)
        else:
            auth = dict(user=self.user, password=self.password)

        return MiqApi(self.api_url, auth, verify_ssl=miq_verify_ssl, ca_bundle_path=ca_bundle_path)


def validate_inputs(module):
    if module.params['miq_token'] and module.params['miq_url']:
        return
    else:
        for arg in ['miq_url', 'miq_username', 'miq_password']:
            if module.params[arg] in (None, ''):
                module.fail_json(msg="missing required argument: {}".format(arg))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            miq_url=dict(default=os.environ.get('MIQ_URL', None)),
            miq_username=dict(default=os.environ.get('MIQ_USERNAME', None)),
            miq_password=dict(default=os.environ.get('MIQ_PASSWORD', None), no_log=True),
            miq_token=dict(default=os.environ.get('MIQ_TOKEN', None), no_log=True),
            miq_verify_ssl=dict(required=False, type='bool', default=True),
            ca_bundle_path=dict(required=False, type='str', default=None),
            state=dict(required=False, type='str', default='get'),
            endpoint=dict(type='str', default='vms'),
        )
    )
    validate_inputs(module)

    miq_url = module.params['miq_url']
    miq_username = module.params['miq_username']
    miq_password = module.params['miq_password']
    miq_token = module.params['miq_token']
    miq_verify_ssl = module.params['miq_verify_ssl']
    ca_bundle_path = module.params['ca_bundle_path']
    state = module.params['state']
    endpoint = module.params['endpoint']

    manageiq = ManageIQ(module, miq_url, miq_username, miq_password, state, miq_verify_ssl, ca_bundle_path, endpoint, miq_token)

    res_args = manageiq.results()
    module.exit_json(changed=False, meta=res_args)


# Import module bits
if __name__ == "__main__":
    main()
