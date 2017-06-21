#! /usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule
from manageiq_client.api import ManageIQClient as MiqApi

DOCUMENTATION = '''
---
module: manageiq_api
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
    miq_verify_ssl - whether SSL certificates should be verified for HTTPS requests
    ca_bundle_path - the path to a CA_BUNDLE file or directory with certificates
    endpoint       - the endpoint path to lookup via the ManageIQ REST API
    """

    WAIT_TIME = 5
    ITERATIONS = 10

    def __init__(self, module, url, user, password, state, miq_verify_ssl, ca_bundle_path, endpoint):
        self.module = module
        self.api_url = url + '/api'
        self.user = user
        self.password = password
        self.client = MiqApi(self.api_url, (self.user, self.password), verify_ssl=miq_verify_ssl, ca_bundle_path=ca_bundle_path)
        self.changed = False
        self.state = state
        self.endpoint = endpoint

    def miq_results(self):
        result = self.client.get(self.api_url + '/' + self.endpoint + '/')
        response = {}
        for item in result['resources']:
            thing = self.client.get(item['href'])
            response[self.endpoint + "_" + str(thing['id'])] = thing
        return response



def main():
    module = AnsibleModule(
        argument_spec=dict(
           miq_url=dict(default=os.environ.get('MIQ_URL', None)),
           miq_username=dict(default=os.environ.get('MIQ_USERNAME', None)),
           miq_password=dict(default=os.environ.get('MIQ_PASSWORD', None), no_log=True),
           miq_verify_ssl=dict(required=False, type='bool', default=True),
           ca_bundle_path=dict(required=False, type='str', default=None),
           state=dict(required=False, type='str', default='get'),
           endpoint=dict(type='str', default='vms')
        )
    )

    for arg in ['miq_url', 'miq_username', 'miq_password']:
        if module.params[arg] in (None, ''):
            module.fail_json(msg="missing required argument: {}".format(arg))

    miq_url = module.params['miq_url']
    miq_username = module.params['miq_username']
    miq_password = module.params['miq_password']
    miq_verify_ssl = module.params['miq_verify_ssl']
    ca_bundle_path = module.params['ca_bundle_path']
    state = module.params['state']
    endpoint = module.params['endpoint']

    manageiq = ManageIQ(module, miq_url, miq_username, miq_password, state, miq_verify_ssl, ca_bundle_path, endpoint)

    res_args = manageiq.miq_results()
    module.exit_json(changed=False, meta=res_args)
    #module.fail_json(msg="Big Problem")


# Import module bits
if __name__ == "__main__":
    main()
