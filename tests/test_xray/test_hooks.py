import pytest

from httpx import Request, Response, TransportError

from incendiary.xray.hooks import (
    begin_subsegment,
    end_subsegment,
    end_subsegment_with_exception,
)


class TestHooks:
    @pytest.fixture()
    def request_object(self):
        return Request(method="GET", url="https://www.example.com/test")

    @pytest.fixture()
    def response(self):
        return Response(status_code=204)

    @pytest.fixture()
    def segment(self, incendiary_application):
        segment = incendiary_application.xray_recorder.begin_segment("1")
        yield segment
        incendiary_application.xray_recorder.end_segment()

    @pytest.fixture()
    def subsegment(self, request_object, incendiary_application):
        return begin_subsegment(
            request_object, incendiary_application.xray_recorder
        )

    def test_begin_subsegment_without_segment(
        self, incendiary_application, request_object
    ):

        subsegment = begin_subsegment(
            request_object, incendiary_application.xray_recorder
        )

        assert hasattr(request_object, "give_up")
        assert request_object.give_up is True

        assert subsegment is None

    def test_begin_subsegment_with_segment(
        self, incendiary_application, request_object, segment
    ):

        subsegment = begin_subsegment(
            request_object, incendiary_application.xray_recorder
        )

        assert subsegment is not None
        assert hasattr(request_object, "give_up")
        assert request_object.give_up is False
        assert subsegment.http["request"]["method"] == "GET"
        assert subsegment.http["request"]["url"] == str(request_object.url)
        assert subsegment.trace_id in request_object.headers["x-amzn-trace-id"]

        # clean up
        subsegment.close()

    def test_end_subsegment_without_segment(
        self, incendiary_application, request_object, response
    ):

        subsegment = begin_subsegment(
            request_object, incendiary_application.xray_recorder
        )

        end = end_subsegment(
            request=request_object,
            response=response,
            recorder=incendiary_application.xray_recorder,
            subsegment=subsegment,
        )

        assert end is None

    @pytest.mark.parametrize(
        "response",
        [
            Response(status_code=200, text="{}"),
            Response(status_code=204),
            Response(status_code=400, text="{}"),
            Response(status_code=500),
        ],
    )
    @pytest.mark.parametrize("pass_subsegment", [True, False])
    def test_end_subsegment_with_segment(
        self,
        incendiary_application,
        request_object,
        segment,
        subsegment,
        response,
        pass_subsegment,
    ):

        end = end_subsegment(
            request=request_object,
            response=response,
            recorder=incendiary_application.xray_recorder,
            subsegment=subsegment if pass_subsegment else None,
        )

        assert end is not None
        assert end.http["response"]["status"] == response.status_code

        if response.status_code >= 400:
            assert "response" in end.annotations
            assert end.annotations["response"] == response.text
            if response.status_code >= 500:
                assert end.fault is True
            else:
                assert end.error is True

        assert hasattr(end, "end_time")
        assert segment.ref_counter.value == 0

    def test_end_exception_without_segment(
        self, incendiary_application, request_object
    ):
        subsegment = begin_subsegment(
            request_object, incendiary_application.xray_recorder
        )

        end = end_subsegment_with_exception(
            request=request_object,
            exception=Exception(),
            recorder=incendiary_application.xray_recorder,
            subsegment=subsegment,
        )

        assert end is None

    @pytest.mark.parametrize("pass_subsegment", [True, False])
    @pytest.mark.parametrize(
        "exceptions",
        [
            Exception(),
            OSError(),
            TransportError(
                "test", request=Request("GET", url="http://www.test.com/")
            ),
        ],
    )
    def test_end_exception_with_segment(
        self,
        incendiary_application,
        request_object,
        segment,
        subsegment,
        pass_subsegment,
        exceptions,
    ):

        end = end_subsegment_with_exception(
            request=request_object,
            exception=exceptions,
            recorder=incendiary_application.xray_recorder,
            subsegment=subsegment if pass_subsegment else None,
        )

        assert end.fault is True
        assert hasattr(end, "end_time")
        assert segment.ref_counter.value == 0
        assert hasattr(end, "cause")
