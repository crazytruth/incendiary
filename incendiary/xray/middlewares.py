import traceback
import ujson as json

from insanic import __version__
from insanic.conf import settings
from insanic.request import Request
from sanic.response import BaseHTTPResponse

from incendiary.xray.utils import abbreviate_for_xray, get_safe_dict

from aws_xray_sdk.core.models import http
from aws_xray_sdk.ext.util import calculate_segment_name, construct_xray_header


async def before_request(request: Request) -> None:
    """
    The request middleware that runs when Sanic receives a
    request. Starts a segment if sampling determines if
    it should be traced.
    """
    xray_recorder = request.app.xray_recorder

    headers = request.headers
    xray_header = construct_xray_header(headers)

    name = calculate_segment_name(request.host, xray_recorder)

    # custom decision to skip if INCENDIARY_XRAY_ENABLED is false
    sampling_decision = xray_recorder.sampler.calculate_sampling_decision(
        trace_header=xray_header,
        recorder=xray_recorder,
        service_name=request.host,
        method=request.method,
        path=request.path,
    )

    segment = xray_recorder.begin_segment(
        name=name,
        traceid=xray_header.root,
        parent_id=xray_header.parent,
        sampling=sampling_decision,
    )

    if segment.sampled:
        segment.save_origin_trace_header(xray_header)
        segment.put_annotation("insanic_version", __version__)
        segment.put_annotation(
            "service_version", settings.get("APPLICATION_VERSION", "?")
        )
        segment.put_http_meta(http.URL, request.url)
        segment.put_http_meta(http.METHOD, request.method)
        segment.put_http_meta(http.USER_AGENT, headers.get("User-Agent"))

        client_ip = headers.get(settings.FORWARDED_FOR_HEADER) or headers.get(
            "HTTP_X_FORWARDED_FOR"
        )
        if client_ip:
            segment.put_http_meta(http.CLIENT_IP, client_ip)
            segment.put_http_meta(http.X_FORWARDED_FOR, True)
        else:
            segment.put_http_meta(http.CLIENT_IP, request.remote_addr)

        attributes = [
            "args",
            "content_type",
            "cookies",
            "data",
            "host",
            "ip",
            "method",
            "path",
            "scheme",
            "url",
        ]
        for attr in attributes:
            if hasattr(request, attr):
                payload = getattr(request, attr)

                if isinstance(payload, dict):
                    payload = abbreviate_for_xray(get_safe_dict(payload))
                payload = json.dumps(payload)

                segment.put_metadata(f"{attr}", payload, "request")


async def after_request(request: Request, response: BaseHTTPResponse) -> None:
    """
    Ends the segment before response is returned.
    """
    xray_recorder = request.app.xray_recorder
    segment = xray_recorder.current_segment()

    if segment.sampled:
        # setting user was moved from _before_request,
        # because calling request.user authenticates, and if
        # authenticators are not set for request, will end not being
        # able to authenticate correctly

        user = request.user

        if user.id:
            segment.set_user(user.id)
            segment.put_annotation("user__level", user.level)

        segment.put_http_meta(http.STATUS, response.status)

        cont_len = response.headers.get("Content-Length")
        # truncate response if too lo
        segment.put_annotation("response", response.body.decode()[:1000])
        if cont_len:
            segment.put_http_meta(http.CONTENT_LENGTH, int(cont_len))

        if hasattr(response, "exception"):
            stack = traceback.extract_stack(limit=xray_recorder.max_trace_back)
            segment.add_exception(response.exception, stack)

    xray_recorder.end_segment()
    return response
