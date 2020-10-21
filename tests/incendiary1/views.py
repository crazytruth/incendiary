import traceback

from insanic.exceptions import BadRequest, ResponseTimeoutError
from insanic.loading import get_service
from insanic.views import InsanicView
from sanic.response import json


class MockView(InsanicView):
    authentication_classes = []
    permission_classes = []

    async def get(self, request, *args, **kwargs):
        segment = request.app.xray_recorder.current_segment()
        try:
            assert segment.sampled is bool(
                int(request.query_params.get("expected_sample"))
            )
            assert segment.in_progress is True
        except AssertionError:

            traceback.print_exc()
            raise

        return json({}, status=202)


class MockErrorView(InsanicView):
    authentication_classes = []
    permission_classes = []

    async def get(self, request, *args, **kwargs):
        # segment = request.app.xray_recorder.current_segment()
        raise BadRequest("trace error!")


class MockInterServiceError(InsanicView):
    authentication_classes = []
    permission_classes = []

    async def get(self, request, *args, **kwargs):
        try:
            service = get_service("incendiary")

            resp, status = await service.http_dispatch(
                "GET", "/trace_error_2", include_status_code=True
            )

            segment = request.app.xray_recorder.current_segment()
            subsegment = segment.subsegments[0]

            try:
                assert subsegment.trace_id == segment.trace_id
                assert subsegment.error is True

                assert subsegment.http["response"]["status"] == 400 == status
            except AssertionError:
                traceback.print_exc()
                raise
        except Exception:
            traceback.print_exc()
            raise
        return json({}, status=204)


class ExceptionView(InsanicView):
    authentication_classes = []
    permission_classes = []

    async def get(self, request, *args, **kwargs):
        try:
            service = get_service("incendiary_exception")

            try:
                await service.http_dispatch(
                    "GET",
                    "/trace_error_2",
                    include_status_code=True,
                    response_timeout=1,
                )
            except ResponseTimeoutError:

                segment = request.app.xray_recorder.current_segment()
                subsegment = segment.subsegments[0]

                try:
                    assert subsegment.trace_id == segment.trace_id
                    assert subsegment.fault is True

                    assert len(subsegment.cause["exceptions"]) > 0
                except AssertionError:
                    traceback.print_exc()
                    raise
        except Exception:
            traceback.print_exc()
            raise
        return json({}, status=204)


class MockInterServiceView(InsanicView):
    authentication_classes = []
    permission_classes = []

    async def get(self, request, *args, **kwargs):
        segment = request.app.xray_recorder.current_segment()
        try:
            expected_sample = bool(
                int(request.query_params.get("expected_sample"))
            )
            try:
                assert segment.sampled is expected_sample
                assert segment.in_progress is True
            except AssertionError:
                traceback.print_exc()
                raise

            service = get_service("incendiary")

            resp, status = await service.http_dispatch(
                "GET",
                "/trace_2",
                query_params={"expected_sample": int(expected_sample)},
                include_status_code=True,
            )
            try:
                assert status == 201
                assert resp == {"i am": "service_2"}, resp
            except AssertionError:
                traceback.print_exc()
                raise
        except Exception:
            traceback.print_exc()
            raise

        return json({}, status=202)
