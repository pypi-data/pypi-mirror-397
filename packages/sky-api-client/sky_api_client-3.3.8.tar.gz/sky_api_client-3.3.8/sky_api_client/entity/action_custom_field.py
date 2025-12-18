from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('action_custom_field')
class ActionCustomField(Entity):
    LIST_URL = '/constituent/v1/actions/{id}/customfields'
    CREATE_URL = '/constituent/v1/actions/customfields'
    UPDATE_URL = '/constituent/v1/actions/customfields/{id}'
    DELETE_URL = '/constituent/v1/actions/customfields/{id}'
