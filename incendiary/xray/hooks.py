from json import JSONDecodeError

import traceback
from typing import Optional

import ujson as json
from aws_xray_sdk.core import AsyncAWSXRayRecorder

from aws_xray_sdk.core.exceptions import exceptions
from aws_xray_sdk.core.models import http
from aws_xray_sdk.core.models.subsegment import Subsegment
from aws_xray_sdk.ext.util import inject_trace_header, strip_url
from httpx import Request, TransportError

from insanic import status


# All aiohttp calls will entail outgoing HTTP requests, only in some ad-hoc
# exceptions the namespace will be flip back to local.
from incendiary.xray.utils import get_safe_dict

REMOTE_NAMESPACE = "remote"
LOCAL_NAMESPACE = "local"
LOCAL_EXCEPTIONS = (
    # DNS issues
    OSError,
    TransportError,
)


def begin_subsegment(
    request: Request, recorder: AsyncAWSXRayRecorder, name: str = None
) -> Optional[Subsegment]:
    """
    Begins a subsegment before sending an interservice
    request.

    :param request: The httpx request object for interservice communications.
    :param recorder: The AWS X-Ray recorder for this application.
    :return: The started subsegment.
    """
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
) -> Optional[Subsegment]:
    """
    The function that ends the subsegment after a response gets
    received.

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
            else:
                resp = get_safe_dict(resp)
                resp = json.dumps(resp)
            subsegment.put_annotation("response", resp)

    # recorder.end_subsegment()
    subsegment.close()
    return subsegment


def end_subsegment_with_exception(
    *,
    request: Request,
    exception: Exception,
    subsegment: Optional[Subsegment] = None,
    recorder: AsyncAWSXRayRecorder,
) -> Optional[Subsegment]:
    """
    The function that ends the subsegment when an
    exception is raised while attempting to send an
    interservice request.
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
    return subsegment
