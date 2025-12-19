from redis.asyncio import Redis
from tp_helper.base_queues.base_stream_queue_repo import BaseStreamQueueRepo

from tp_shared.mos_passes_service.schemas.mos_passes_ovga_result_message import (
    MosPassesOvgaResultStreamMessage,
)
from tp_shared.types.system_type import SystemType


class MosPassesOvgaTasksResultsStreamQueueRepo(BaseStreamQueueRepo):
    QUEUE_NAME = "mos:passes:service:ovga:results:stream"

    def __init__(self, redis_client: Redis, system_type: SystemType | None = None):
        queue_name = self.QUEUE_NAME
        if system_type is not None:
            queue_name += f":{system_type}"
        super().__init__(
            redis_client=redis_client,
            queue_name=queue_name,
            schema=MosPassesOvgaResultStreamMessage,
        )
