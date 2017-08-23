from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash
import pprint

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):

        if 'debug' in task_vars:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(task_vars)


        if task_vars is None:
            task_vars = dict()
        module_vars = self._task.args.copy()
        results = super(ActionModule, self).run(tmp, task_vars)
        # remove as modules might hide due to nolog
        #del results['invocation']['module_args']
        for arg in ['miq_url', 'miq_username', 'miq_password']:
            try:
                if task_vars[arg]:
                    module_vars[arg] = task_vars[arg]
            except KeyError:
                next

        results = merge_hash(
            results,
            self._execute_module(module_args=module_vars, task_vars=task_vars),
        )
        for field in ('_ansible_notify',):
            if field in results:
                results.pop(field)
        return results
