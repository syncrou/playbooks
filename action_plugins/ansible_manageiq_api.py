from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
import pprint

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):

        if 'debug' in self._task.args:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(self._task.args)
            pp.pprint(task_vars)
            self._task.args.pop('debug', None)


        if task_vars is None:
            task_vars = dict()
        module_vars = self._task.args.copy()
        results = super(ActionModule, self).run(tmp, task_vars)
        # remove as modules might hide due to nolog
        #del results['invocation']['module_args']
        for arg in ['miq_url', 'miq_username', 'miq_password', 'miq_token']:
            if arg in task_vars:
                module_vars[arg] = task_vars[arg]


        results = merge_hash(
            results,
            self._execute_module(module_args=module_vars, task_vars=task_vars),
        )


        for field in ('_ansible_notify',):
            if field in results:
                results.pop(field)
        return results
