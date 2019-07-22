import aiohttp
import pytest
import logging

from insanic.app import Insanic
from insanic.conf import settings

from insanic.responses import json_response
from insanic.services import Service
from insanic.views import InsanicView

from incendiary.xray.app import Incendiary

logger = logging.getLogger(__name__)


class TestIncendiaryXRayInitialize():

    def test_init(self, insanic_application):
        Incendiary.init_app(insanic_application)

        assert hasattr(insanic_application, "sampler")
        assert insanic_application.sampler is not None

    def test_patch_service_object(self, insanic_application):
        """
        tests if the patched extra session configs in session object persists

        :param insanic_application:
        :return:
        """

        Incendiary.patch_service()

        from insanic.services import Service

        assert Service.extra_session_configs != {}
        assert "trace_configs" in Service.extra_session_configs
