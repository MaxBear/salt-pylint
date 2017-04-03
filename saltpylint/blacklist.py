# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2017 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    saltpylint.blacklist
    ~~~~~~~~~~~~~~~~~~~~

    Checks blacklisted imports and code usage on salt
'''

# Import python libs
from __future__ import absolute_import
import os
import fnmatch

# Import pylint libs
import astroid
from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker
from pylint.checkers.utils import check_messages

BLACKLISTED_IMPORTS_MSGS = {
    'W8402': ('Uses of a blacklisted module %r: %s',
              'blacklisted-module',
              'Used a module marked as blacklisted is imported.'),
    'W8403': ('Uses of a blacklisted external module %r: %s',
              'blacklisted-external-module',
              'Used a module marked as blacklisted is imported.'),
    'W8404': ('Uses of a blacklisted import %r: %s',
              'blacklisted-import',
              'Used an import marked as blacklisted.'),
    'W8405': ('Uses of an external blacklisted import %r: %s',
              'blacklisted-external-import',
              'Used an external import marked as blacklisted.'),
    'W8406': ('Uses of blacklisted test module execution code: %s',
              'blacklisted-test-module-execution',
              'Uses of blacklisted test module execution code.'),
    'W8407': ('Uses of blacklisted sys.path updating through \'ensure_in_syspath\'. '
              'Please remove the import and any calls to \'ensure_in_syspath()\'.',
              'blacklisted-syspath-update',
              'Uses of blacklisted sys.path updating through ensure_in_syspath.'),
    }


class BlacklistedImportsChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = 'blacklisted-imports'
    msgs = BLACKLISTED_IMPORTS_MSGS
    priority = -2

    def open(self):
        self.blacklisted_modules = ('salttesting',
                                    'integration',
                                    'unit',
                                    'mock',
                                    'six',
                                    'distutils.version',
                                    'unittest',
                                    'unittest2')

    @check_messages('blacklisted-imports')
    def visit_import(self, node):
        '''triggered when an import statement is seen'''
        module_filename = node.root().file
        if fnmatch.fnmatch(module_filename, '__init__.py*') and \
                not fnmatch.fnmatch(module_filename, 'test_*.py*'):
            return
        modnode = node.root()
        names = [name for name, _ in node.names]

        for name in names:
            self._check_blacklisted_module(node, name)

    @check_messages('blacklisted-imports')
    def visit_importfrom(self, node):
        '''triggered when a from statement is seen'''
        module_filename = node.root().file
        if fnmatch.fnmatch(module_filename, '__init__.py*') and \
                not fnmatch.fnmatch(module_filename, 'test_*.py*'):
            return
        basename = node.modname
        self._check_blacklisted_module(node, basename)

    def _check_blacklisted_module(self, node, mod_path):
        '''check if the module is blacklisted'''
        for mod_name in self.blacklisted_modules:
            if mod_path == mod_name or mod_path.startswith(mod_name + '.'):
                names = []
                for name, name_as in node.names:
                    if name_as:
                        names.append('{0} as {1}'.format(name, name_as))
                    else:
                        names.append(name)
                try:
                    import_from_module = node.modname
                    if import_from_module == 'salttesting.helpers':
                        for name in names:
                            if name == 'ensure_in_syspath':
                                self.add_message('blacklisted-syspath-update', node=node)
                                continue
                            msg = 'Please use \'from tests.support.helpers import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module in ('salttesting.mock', 'mock', 'unittest.mock', 'unittest2.mock'):
                        for name in names:
                            msg = 'Please use \'from tests.support.mock import {0}\''.format(name)
                            if import_from_module in ('salttesting.mock', 'unittest.mock', 'unittest2.mock'):
                                message_id = 'blacklisted-module'
                            else:
                                message_id = 'blacklisted-external-module'
                            self.add_message(message_id, node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.parser':
                        for name in names:
                            msg = 'Please use \'from tests.support.parser import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.case':
                        for name in names:
                            msg = 'Please use \'from tests.support.case import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.unit':
                        for name in names:
                            msg = 'Please use \'from tests.support.unit import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module.startswith(('unittest', 'unittest2')):
                        for name in names:
                            msg = 'Please use \'from tests.support.unit import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'salttesting.mixins':
                        for name in names:
                            msg = 'Please use \'from tests.support.mixins import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'six':
                        for name in names:
                            msg = 'Please use \'from salt.ext.six import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if import_from_module == 'distutils.version':
                        for name in names:
                            msg = 'Please use \'from salt.utils.versions import {0}\''.format(name)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                        continue
                    if names:
                        for name in names:
                            if name in ('TestLoader', 'TextTestRunner', 'TestCase', 'expectedFailure',
                                        'TestSuite', 'skipIf', 'TestResult'):
                                msg = 'Please use \'from tests.support.unit import {0}\''.format(name)
                                self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                                continue
                            if name in ('SaltReturnAssertsMixin', 'SaltMinionEventAssertsMixin'):
                                msg = 'Please use \'from tests.support.mixins import {0}\''.format(name)
                                self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                                continue
                            if name in ('ModuleCase', 'SyndicCase', 'ShellCase', 'SSHCase'):
                                msg = 'Please use \'from tests.support.case import {0}\''.format(name)
                                self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                                continue
                            if name == 'run_tests':
                                msg = 'Please remove the \'if __name__ == "__main__":\' section from the end of the module'
                                self.add_message('blacklisted-test-module-execution', node=node, args=msg)
                                continue
                            if mod_name in ('integration', 'unit'):
                                if name in ('SYS_TMP_DIR',
                                            'TMP',
                                            'FILES',
                                            'PYEXEC',
                                            'MOCKBIN',
                                            'SCRIPT_DIR',
                                            'TMP_STATE_TREE',
                                            'TMP_PRODENV_STATE_TREE',
                                            'TMP_CONF_DIR',
                                            'TMP_SUB_MINION_CONF_DIR',
                                            'TMP_SYNDIC_MINION_CONF_DIR',
                                            'TMP_SYNDIC_MASTER_CONF_DIR',
                                            'CODE_DIR',
                                            'TESTS_DIR',
                                            'CONF_DIR',
                                            'PILLAR_DIR',
                                            'TMP_SCRIPT_DIR',
                                            'ENGINES_DIR',
                                            'LOG_HANDLERS_DIR',
                                            'INTEGRATION_TEST_DIR'):
                                    msg = 'Please use \'from tests.support.paths import {0}\''.format(name)
                                    self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                                    continue
                                msg = 'Please use \'from tests.{0} import {1}\''.format(mod_path, name)
                                self.add_message('blacklisted-import', node=node, args=(mod_path, msg))
                                continue
                            msg = 'Please report this error to SaltStack so we can fix it: Trying to import {0} from {1}'.format(name, mod_path)
                            self.add_message('blacklisted-module', node=node, args=(mod_path, msg))
                except AttributeError:
                    if mod_name in ('integration', 'unit', 'mock', 'six', 'distutils.version',
                                    'unittest', 'unittest2'):
                        if mod_name in ('integration', 'unit'):
                            msg = 'Please use \'import tests.{0} as {0}\''.format(mod_name)
                            message_id = 'blacklisted-import'
                        elif mod_name == 'mock':
                            msg = 'Please use \'import tests.support.{0} as {0}\''.format(mod_name)
                            message_id = 'blacklisted-external-import'
                        elif mod_name == 'six':
                            msg = 'Please use \'import salt.ext.{0} as {0}\''.format(name)
                            message_id = 'blacklisted-external-import'
                        elif mod_name == 'distutils.version':
                            msg = 'Please use \'import salt.utils.versions\' instead'
                            message_id = 'blacklisted-import'
                        elif mod_name.startswith(('unittest', 'unittest2')):
                            msg = 'Please use \'import tests.support.unit as {}\' instead'.format(mod_name)
                            message_id = 'blacklisted-import'
                        self.add_message(message_id, node=node, args=(mod_path, msg))
                        continue
                    msg = 'Please report this error to SaltStack so we can fix it: Trying to import {0}'.format(mod_path)
                    self.add_message('blacklisted-import', node=node, args=(mod_path, msg))

BLACKLISTED_LOADER_USAGE_MSGS = {
    'W8501': ('Blacklisted salt loader dunder usage. Setting dunder attribute %r to module %r. '
              'Use \'salt.support.mock\' and \'patch.dict()\' instead.',
              'unmocked-patch-dunder',
              'Uses a blacklisted salt loader dunder usage in tests.'),
    'W8502': ('Blacklisted salt loader dunder usage. Setting attribute %r to module %r. '
              'Use \'salt.support.mock\' and \'patch()\' instead.',
              'unmocked-patch',
              'Uses a blacklisted salt loader dunder usage in tests.'),
    'W8503': ('Blacklisted salt loader dunder usage. Updating dunder attribute %r on module %r. '
              'Use \'salt.support.mock\' and \'patch.dict()\' instead.',
              'unmocked-patch-dunder-update',
              'Uses a blacklisted salt loader dunder usage in tests.'),
}


class BlacklistedLoaderModulesUsageChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = 'blacklisted-unmocked-patching'
    msgs = BLACKLISTED_LOADER_USAGE_MSGS
    priority = -2

    def open(self):
        self.process_module = False
        self.salt_dunders = (
            '__opts__', '__salt__', '__runner__', '__context__', '__utils__',
            '__ext_pillar__', '__thorium__', '__states__', '__serializers__',
            '__ret__', '__grains__', '__pillar__', '__sdb__', '__proxy__',
            '__low__', '__orchestration_jid__', '__running__', '__intance_id__',
            '__lowstate__', '__env__'
        )
        self.imported_salt_modules = {}

    def close(self):
        self.process_module = False
        self.imported_salt_modules = {}

    @check_messages('blacklisted-unmocked-patching')
    def visit_module(self, node):
        module_filename = node.root().file
        if not fnmatch.fnmatch(os.path.basename(module_filename), 'test_*.py*'):
            return
        self.process_module = True

    @check_messages('blacklisted-unmocked-patching')
    def leave_module(self, node):
        if self.process_module:
            # Reset
            self.process_module = False
            self.imported_salt_modules = {}

    @check_messages('blacklisted-unmocked-patching')
    def visit_import(self, node):
        '''triggered when an import statement is seen'''
        if self.process_module:
            # Store salt imported modules
            for module, import_as in node.names:
                if not module.startswith('salt'):
                    continue
                if import_as and import_as not in self.imported_salt_modules:
                    self.imported_salt_modules[import_as] = module
                    continue
                if module not in self.imported_salt_modules:
                    self.imported_salt_modules[module] = module

    @check_messages('blacklisted-unmocked-patching')
    def visit_importfrom(self, node):
        '''triggered when a from statement is seen'''
        if self.process_module:
            if not node.modname.startswith('salt'):
                return
            # Store salt imported modules
            for module, import_as in node.names:
                if import_as and import_as not in self.imported_salt_modules:
                    self.imported_salt_modules[import_as] = import_as
                    continue
                if module not in self.imported_salt_modules:
                    self.imported_salt_modules[module] = module

    @check_messages('blacklisted-loader-usage')
    def visit_assign(self, node, *args):
        if not self.process_module:
            return

        node_left = node.targets[0]

        if isinstance(node_left, astroid.Subscript):
            # Were're changing an existing attribute
            if not isinstance(node_left.value, astroid.Attribute):
                return
            if node_left.value.attrname in self.salt_dunders:
                self.add_message(
                    'unmocked-patch-dunder-update',
                    node=node,
                    args=(node_left.value.attrname,
                          self.imported_salt_modules[node_left.value.expr.name])
                )
                return

        if not isinstance(node_left, astroid.AssignAttr):
            return

        try:
            if node_left.expr.name not in self.imported_salt_modules:
                # If attributes are not being set on salt's modules,
                # leave it alone, for now!
                return
        except AttributeError:
            # This mmight not be what we're looking for
            return

        # we're assigning to an imported salt module!
        if node_left.attrname in self.salt_dunders:
            # We're changing salt dunders
            self.add_message(
                'unmocked-patch-dunder',
                node=node,
                args=(node_left.attrname,
                      self.imported_salt_modules[node_left.expr.name])
            )
            return

        # Changing random attributes
        self.add_message(
            'unmocked-patch',
            node=node,
            args=(node_left.attrname,
                  self.imported_salt_modules[node_left.expr.name])
        )


MOVED_TEST_CASE_CLASSES_MSGS = {
    'W8490': ('Moved test case base class detected. %s',
              'moved-test-case-class',
              'Moved test case base class detected.'),
}


class MovedTestCaseClassChecker(BaseChecker):

    __implements__ = IAstroidChecker

    name = 'moved-test-case-class'
    msgs = MOVED_TEST_CASE_CLASSES_MSGS
    priority = -2

    def open(self):
        self.process_module = False

    def close(self):
        self.process_module = False

    @check_messages('moved-test-case-class')
    def visit_module(self, node):
        module_filename = node.root().file
        if not fnmatch.fnmatch(os.path.basename(module_filename), 'test_*.py*'):
            return
        self.process_module = True

    @check_messages('moved-test-case-class')
    def leave_module(self, node):
        if self.process_module:
            # Reset
            self.process_module = False

    @check_messages('moved-test-case-class')
    def visit_importfrom(self, node):
        '''triggered when a from statement is seen'''
        if self.process_module:
            if not node.modname.startswith('tests.integration'):
                return
            # Store salt imported modules
            for module, import_as in node.names:
                if import_as:
                    self._check_moved_imports(node, module, import_as)
                    continue
                self._check_moved_imports(node, module)

    @check_messages('moved-test-case-class')
    def visit_classdef(self, node):
        for base in node.bases:
            if base.attrname in ('ModuleCase', 'SyndicCase', 'ShellCase', 'SSHCase'):
                msg = 'Please use \'from tests.support.case import {0}\''.format(base.attrname)
            self.add_message('moved-test-case-class', node=node, args=(msg,))

    def _check_moved_imports(self, node, module, import_as=None):
        names = []
        for name, name_as in node.names:
            if name not in ('ModuleCase', 'SyndicCase', 'ShellCase', 'SSHCase'):
                continue
            if name_as:
                msg = 'Please use \'from tests.support.case import {0} as {1}\''.format(name, name_as)
            else:
                msg = 'Please use \'from tests.support.case import {0}\''.format(name)
            self.add_message('moved-test-case-class', node=node, args=(msg,))


def register(linter):
    '''
    Required method to auto register this checker
    '''
    linter.register_checker(BlacklistedImportsChecker(linter))
    linter.register_checker(MovedTestCaseClassChecker(linter))
    linter.register_checker(BlacklistedLoaderModulesUsageChecker(linter))
