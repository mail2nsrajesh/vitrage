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

from vitrage.common.constants import DatasourceAction
from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.entity_graph.initialization_status import InitializationStatus
from vitrage.entity_graph.processor import processor as proc
from vitrage.tests.mocks import mock_driver
from vitrage.tests.unit.entity_graph.base import TestEntityGraphUnitBase


class TestFunctionalBase(TestEntityGraphUnitBase):

    def _create_processor_with_graph(self, conf, processor=None,
                                     uuid=False):
        events = self._create_mock_events()

        if not processor:
            processor = proc.Processor(conf, InitializationStatus(),
                                       uuid=uuid)

        for event in events:
            processor.process_event(event)

        return processor

    def _create_mock_events(self):
        gen_list = mock_driver.simple_zone_generators(
            self.NUM_ZONES,
            self.NUM_HOSTS,
            snapshot_events=self.NUM_ZONES,
            snap_vals={DSProps.DATASOURCE_ACTION:
                       DatasourceAction.INIT_SNAPSHOT})
        gen_list += mock_driver.simple_host_generators(
            self.NUM_ZONES,
            self.NUM_HOSTS,
            self.NUM_HOSTS,
            snap_vals={DSProps.DATASOURCE_ACTION:
                       DatasourceAction.INIT_SNAPSHOT})
        gen_list += mock_driver.simple_instance_generators(
            self.NUM_HOSTS,
            self.NUM_INSTANCES,
            self.NUM_INSTANCES,
            snap_vals={DSProps.DATASOURCE_ACTION:
                       DatasourceAction.INIT_SNAPSHOT})
        return mock_driver.generate_sequential_events_list(gen_list)
