from httpx import Request
from insanic.services import Service

from incendiary.xray.hooks import (
    begin_subsegment,
    end_subsegment,
    end_subsegment_with_exception,
)


class IncendiaryService(Service):

    xray_recorder = None

    async def _dispatch_send(
        self,
        request: Request,
        *,
        timeout: float = None,
        retry_count: int = None,
    ):
        subsegment = begin_subsegment(
            request=request, name=self.service_name, recorder=self.xray_recorder
        )
        try:
            response = await super()._dispatch_send(
                request=request, timeout=timeout, retry_count=retry_count,
            )
        except Exception as e:
            end_subsegment_with_exception(
                request=request,
                exception=e,
                subsegment=subsegment,
                recorder=self.xray_recorder,
            )
            raise
        else:
            end_subsegment(
                request=request,
                response=response,
                recorder=self.xray_recorder,
                subsegment=subsegment,
            )

            return response
