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

from oslo_log import log as logging

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import EventAction
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.heat.stack import HEAT_STACK_DATASOURCE
from vitrage.datasources.resource_transformer_base import \
    ResourceTransformerBase
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import extract_field_value
import vitrage.graph.utils as graph_utils


LOG = logging.getLogger(__name__)


class HeatStackTransformer(ResourceTransformerBase):

    UPDATE_ID_PROPERTY = {
        'orchestration.stack.create.end': ('stack', 'id'),
        'orchestration.stack.update.end': ('stack', 'id'),
        'orchestration.stack.update.end': ('stack', 'id'),
        'orchestration.stack.delete.end': ('stack', 'id'),
        None: ('id',)
    }

    # Event types which need to refer differently
    UPDATE_EVENT_TYPES = {
        'orchestration.stack.delete.end': EventAction.DELETE_ENTITY,
    }

    def __init__(self, transformers):
        super(HeatStackTransformer, self).__init__(transformers)

    def _create_snapshot_entity_vertex(self, entity_event):

        name = entity_event['stack_name']
        entity_id = entity_event['id']
        state = entity_event['stack_status']
        update_timestamp = entity_event['updated_time']

        return self._create_vertex(entity_event,
                                   name,
                                   entity_id,
                                   state,
                                   update_timestamp)

    def _create_update_entity_vertex(self, entity_event):

        event_type = entity_event[DSProps.EVENT_TYPE]
        name = extract_field_value(entity_event, 'stack', 'stack_name')
        state = extract_field_value(entity_event, 'stack', 'stack_status')
        update_timestamp = \
            extract_field_value(entity_event, 'stack', 'updated_time')
        entity_id = extract_field_value(entity_event,
                                        *self.UPDATE_ID_PROPERTY[event_type])

        return self._create_vertex(entity_event,
                                   name,
                                   entity_id,
                                   state,
                                   update_timestamp)

    def _create_vertex(self,
                       entity_event,
                       name,
                       entity_id,
                       state,
                       update_timestamp):

        metadata = {
            VProps.NAME: name,
        }

        sample_timestamp = entity_event[DSProps.SAMPLE_DATE]

        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            entity_id=entity_id,
            entity_category=EntityCategory.RESOURCE,
            entity_type=HEAT_STACK_DATASOURCE,
            entity_state=state,
            sample_timestamp=sample_timestamp,
            update_timestamp=update_timestamp,
            metadata=metadata)

    def _create_entity_key(self, entity_event):
        event_type = entity_event.get(DSProps.EVENT_TYPE, None)
        stack_id = extract_field_value(entity_event,
                                       *self.UPDATE_ID_PROPERTY[event_type])

        key_fields = self._key_values(HEAT_STACK_DATASOURCE, stack_id)
        return tbase.build_key(key_fields)

    def get_type(self):
        return HEAT_STACK_DATASOURCE