import pytest

from botocore.endpoint import Endpoint
from insanic import Insanic
from insanic.conf import settings

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.emitters.udp_emitter import UDPEmitter

settings.configure(SERVICE_NAME="iniesta",
                   GATEWAY_REGISTRATION_ENABLED=False,
                   MMT_ENV="test",
                   GRPC_SERVE=False)


class DummyEmitter(UDPEmitter):

    def _send_data(self, data):
        pass


@pytest.fixture(autouse=True)
def insanic_application():
    app = Insanic("trace")

    yield app


#
# @pytest.fixture(autouse=True)
# def set_redis_connection_info(redisdb, monkeypatch):
#     port = redisdb.connection_pool.connection_kwargs['path'].split('/')[-1].split('.')[1]
#     db = redisdb.connection_pool.connection_kwargs['db']
#
#     monkeypatch.setattr(settings, 'REDIS_PORT', int(port))
#     monkeypatch.setattr(settings, 'REDIS_HOST', '127.0.0.1')
#     monkeypatch.setattr(settings, 'REDIS_DB', db)

@pytest.fixture(autouse=True)
def mock_emitter(monkeypatch):
    monkeypatch.setattr(xray_recorder, '_emitter', DummyEmitter())


@pytest.fixture(autouse=True)
def mock_boto(monkeypatch):
    def _mock_send(self, request):
        return {
            'SamplingRuleRecords': [],
        }

    monkeypatch.setattr(Endpoint, '_send', _mock_send)


@pytest.fixture(autouse=True)
def clean_up_threads():
    yield
    #
    # threads = []
    # for t in threading.enumerate():
    #     if not t.daemon and t.name != "MainThread":
    #         # threads.append(t)
    #         t._stop()

    a = 1
