from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
import pprint

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None, module_vars=dict(), **kwargs):
        pp = pprint.PrettyPrinter(indent=4)
        miq_url = task_vars['miq_url']
        miq_password = task_vars['miq_password']
        miq_username = task_vars['miq_username']
        pp.pprint("TASK VARS: "+miq_url+" "+miq_username+" "+miq_password)
        if task_vars is None:
            task_vars = dict()
        results = super(ActionModule, self).run(tmp, task_vars)
        # remove as modules might hide due to nolog
        #del results['invocation']['module_args']
        module_vars['miq_username'] = miq_username
        module_vars['miq_password'] = miq_password
        module_vars['miq_url'] = miq_url
        results = merge_hash(
            results,
            self._execute_module(module_args=module_vars, task_vars=task_vars),
        )
        for field in ('_ansible_notify',):
            if field in results:
                results.pop(field)
        return results
