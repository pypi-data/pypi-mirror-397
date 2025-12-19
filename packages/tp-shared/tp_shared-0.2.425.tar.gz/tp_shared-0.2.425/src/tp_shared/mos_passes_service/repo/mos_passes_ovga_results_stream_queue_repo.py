from redis.asyncio import Redis
from tp_helper.base_queues.base_stream_queue_repo import BaseStreamQueueRepo

from tp_shared.mos_passes_service.schemas.mos_passes_ovga_result_message import (
    MosPassesOvgaResultStreamMessage,
)


class MosPassesOvgaTasksResultsStreamQueueRepo(BaseStreamQueueRepo):
    QUEUE_NAME = "mos:passes:service:ovga:results:stream"

    def __init__(self, redis_client: Redis):
        super().__init__(
            redis_client=redis_client,
            queue_name=self.QUEUE_NAME,
            schema=MosPassesOvgaResultStreamMessage,
        )
