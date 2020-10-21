from json import JSONDecodeError

import traceback
from typing import Optional

import ujson as json
from aws_xray_sdk.core import AsyncAWSXRayRecorder

from aws_xray_sdk.core.exceptions import exceptions
from aws_xray_sdk.core.models import http
from aws_xray_sdk.core.models.subsegment import Subsegment
from aws_xray_sdk.ext.util import inject_trace_header, strip_url
from httpx import Request

from insanic import status


# All aiohttp calls will entail outgoing HTTP requests, only in some ad-hoc
# exceptions the namespace will be flip back to local.
from incendiary.xray.utils import get_safe_dict

REMOTE_NAMESPACE = "remote"
LOCAL_NAMESPACE = "local"
LOCAL_EXCEPTIONS = (
    # DNS issues
    OSError,
)


def begin_subsegment(
    request: Request, recorder: AsyncAWSXRayRecorder, name: str = None
) -> Optional[Subsegment]:
    name = name or strip_url(str(request.url))

    try:
        subsegment = recorder.begin_subsegment(name, REMOTE_NAMESPACE)
    except (
        exceptions.SegmentNotFoundException,
        exceptions.AlreadyEndedException,
    ):
        subsegment = None

    # No-op if subsegment is `None` due to `LOG_ERROR`.
    if not subsegment:
        request.give_up = True
    else:
        request.give_up = False
        subsegment.put_http_meta(http.METHOD, request.method)
        subsegment.put_http_meta(http.URL, str(request.url))
        inject_trace_header(request.headers, subsegment)

    return subsegment


def end_subsegment(
    *, request, response, recorder, subsegment: Optional[Subsegment] = None
) -> None:
    """
    As long as the request returns a response, this gets run

    :param request: The request object for interservice communications.
    :param response: Response object of the request.
    :param subsegment: Subsegment of this request.
    :param recorder: The aws xray recorder.
    """

    if getattr(request, "give_up", None):
        return

    subsegment = subsegment or recorder.current_subsegment()
    if subsegment.sampled:
        subsegment.put_http_meta(http.STATUS, response.status_code)

        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            try:
                resp = response.json()
            except JSONDecodeError:
                resp = response.text
            resp = get_safe_dict(resp)
            subsegment.put_annotation("response", json.dumps(resp))

    # recorder.end_subsegment()
    subsegment.close()


def end_subsegment_with_exception(
    *,
    request: Request,
    exception: Exception,
    subsegment: Optional[Subsegment],
    recorder: AsyncAWSXRayRecorder,
) -> None:
    """
    exception when establishing connection

    :param request:
    :param exception:
    :param subsegment:
    :param recorder:
    :return:
    """

    if getattr(request, "give_up", None):
        return

    subsegment = subsegment or recorder.current_subsegment()

    if subsegment.sampled:
        subsegment.add_exception(
            exception, traceback.extract_stack(limit=recorder._max_trace_back),
        )

        if isinstance(exception, LOCAL_EXCEPTIONS):
            subsegment.namespace = LOCAL_NAMESPACE

    subsegment.close()
