from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry


@EntityRegistry.register('gift_batch_gift_v2')
class GiftBatchGiftV2(Entity):
    CREATE_URL = '/gft-gifts/v2/batchgifts/{id}'
