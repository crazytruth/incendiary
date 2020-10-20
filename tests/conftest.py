import pytest

from botocore.endpoint import Endpoint
from insanic import Insanic
from insanic.conf import settings


settings.configure(
    SERVICE_NAME="tracer",
    AWS_ACCESS_KEY_ID="testing",
    AWS_SECRET_ACCESS_KEY="testing",
    AWS_DEFAULT_REGION="us-east-1",
    ENVIRONMENT="tests",
)


@pytest.fixture(autouse=True)
def insanic_application():
    app = Insanic("trace", version="0.1.0")

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
def mock_boto(monkeypatch):
    def _mock_send(self, request):
        return {
            "SamplingRuleRecords": [],
        }

    monkeypatch.setattr(Endpoint, "_send", _mock_send)
