# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import copy

from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content import \
    template_content_validator as validator
from vitrage.tests.mocks import utils
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    ValidatorTest
from vitrage.utils import file as file_utils


class TemplateContentValidatorTest(ValidatorTest):

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):

        template_dir_path = '%s/templates/general' % utils.get_resources_dir()
        cls.templates = file_utils.load_yaml_files(template_dir_path)
        cls.first_template = cls.templates[0]

        cls._hide_useless_logging_messages()

    @property
    def clone_template(self):
        return copy.deepcopy(self.first_template)

    def test_template_validator(self):
        for template in self.templates:
            self._execute_and_assert_with_correct_result(template)

    def test_not_operator(self):
        basic_correct_not_condition_path = \
            '%s/templates/not_operator/basic_correct_not_condition.yaml' % \
            utils.get_resources_dir()
        basic_correct_not_condition_template = \
            file_utils.load_yaml_file(basic_correct_not_condition_path)
        self._execute_and_assert_with_correct_result(
            basic_correct_not_condition_template)

        basic_incorrect_not_condition_path = \
            '%s/templates/not_operator/basic_incorrect_not_condition.yaml' % \
            utils.get_resources_dir()
        basic_incorrect_not_condition_template = \
            file_utils.load_yaml_file(basic_incorrect_not_condition_path)
        self._execute_and_assert_with_fault_result(
            basic_incorrect_not_condition_template,
            86)

        complicated_correct_not_condition_path = \
            '%s/templates/not_operator/' \
            'complicated_correct_not_condition.yaml' % \
            utils.get_resources_dir()
        complicated_correct_not_condition_template = \
            file_utils.load_yaml_file(complicated_correct_not_condition_path)
        self._execute_and_assert_with_correct_result(
            complicated_correct_not_condition_template)

        complicated_incorrect_not_condition_path = \
            '%s/templates/not_operator/' \
            'complicated_incorrect_not_condition.yaml' % \
            utils.get_resources_dir()
        complicated_incorrect_not_condition_template = \
            file_utils.load_yaml_file(complicated_incorrect_not_condition_path)
        self._execute_and_assert_with_fault_result(
            complicated_incorrect_not_condition_template,
            86)

    def test_validate_entity_definition_with_no_unique_template_id(self):

        template = self.clone_template
        definitions = template[TemplateFields.DEFINITIONS]

        for entity in definitions[TemplateFields.ENTITIES]:
            entity_dict = entity[TemplateFields.ENTITY]
            entity_dict[TemplateFields.TEMPLATE_ID] = 'aaa'

        self._execute_and_assert_with_fault_result(template, 2)

    def test_validate_relationship_with_no_unique_template_id(self):

        template = self.clone_template
        definitions = template[TemplateFields.DEFINITIONS]
        entity = definitions[TemplateFields.ENTITIES][0]
        entity_id = entity[TemplateFields.ENTITY][TemplateFields.TEMPLATE_ID]
        relationship = definitions[TemplateFields.RELATIONSHIPS][0]
        relationship_dict = relationship[TemplateFields.RELATIONSHIP]
        relationship_dict[TemplateFields.TEMPLATE_ID] = entity_id

        self._execute_and_assert_with_fault_result(template, 2)

    def test_validate_relationship_with_invalid_target(self):

        template = self.clone_template
        definitions = template[TemplateFields.DEFINITIONS]
        relationship = definitions[TemplateFields.RELATIONSHIPS][0]
        relationship_dict = relationship[TemplateFields.RELATIONSHIP]
        relationship_dict[TemplateFields.TARGET] = 'unknown'

        self._execute_and_assert_with_fault_result(template, 3)

    def test_validate_relationship_with_invalid_source(self):

        template = self.clone_template
        definitions = template[TemplateFields.DEFINITIONS]
        relationship = definitions[TemplateFields.RELATIONSHIPS][0]
        relationship_dict = relationship[TemplateFields.RELATIONSHIP]
        relationship_dict[TemplateFields.SOURCE] = 'unknown'

        self._execute_and_assert_with_fault_result(template, 3)

    def test_validate_scenario_invalid_condition(self):

        template = self.clone_template
        scenario = template[TemplateFields.SCENARIOS][0]
        scenario_dict = scenario[TemplateFields.SCENARIO]

        scenario_dict[TemplateFields.CONDITION] = 'and resource'
        self._execute_and_assert_with_fault_result(template, 85)

        scenario_dict[TemplateFields.CONDITION] = 'resource or'
        self._execute_and_assert_with_fault_result(template, 85)

        scenario_dict[TemplateFields.CONDITION] = 'not or resource'
        self._execute_and_assert_with_fault_result(template, 85)

        scenario_dict[TemplateFields.CONDITION] = \
            'alarm_on_host (alarm or resource'
        self._execute_and_assert_with_fault_result(template, 85)

        scenario_dict[TemplateFields.CONDITION] = 'aaa'
        self._execute_and_assert_with_fault_result(template, 3)

        scenario_dict[TemplateFields.CONDITION] = 'resource and aaa'
        self._execute_and_assert_with_fault_result(template, 3)

    def _execute_and_assert_with_fault_result(self, template, status_code):

        result = validator.content_validation(template)
        self._assert_fault_result(result, status_code)

    def _execute_and_assert_with_correct_result(self, template):

        result = validator.content_validation(template)
        self._assert_correct_result(result)

    def _create_scenario_actions(self, target, source):

        actions = []
        raise_alarm_action = self._create_raise_alarm_action(target)
        actions.append({TemplateFields.ACTION: raise_alarm_action})

        set_state_action = self._create_set_state_action(target)
        actions.append({TemplateFields.ACTION: set_state_action})

        mark_host_down_action = self._create_mark_down_action(target)
        actions.append({TemplateFields.ACTION: mark_host_down_action})

        causal_action = self._create_add_causal_relationship_action(target,
                                                                    source)
        actions.append({TemplateFields.ACTION: causal_action})

        return actions
