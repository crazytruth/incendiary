import pytest
from aws_xray_sdk.core import xray_recorder, AsyncAWSXRayRecorder
from aws_xray_sdk.core.sampling.sampler import DefaultSampler
from insanic import Insanic


from incendiary.xray.app import Incendiary

from .utils import StubbedEmitter


@pytest.fixture(autouse=True)
def stub_emitter(monkeypatch):
    # monkeypatch.setattr(xray_recorder, '_emitter', StubbedEmitter())
    monkeypatch.setattr(
        Incendiary,
        "extra_recorder_configurations",
        {"emitter": StubbedEmitter()},
    )


@pytest.fixture(autouse=True)
def reset_recorder(insanic_application):
    Incendiary.load_config(insanic_application.config)

    yield
    from incendiary.xray.sampling import IncendiaryDefaultSampler

    insanic_application.sampler = IncendiaryDefaultSampler(insanic_application)
    xray_recorder.configure(**Incendiary.xray_config(insanic_application))
    xray_recorder.sampler = DefaultSampler()


@pytest.fixture(autouse=True)
def reset_registry():

    yield
    from insanic.services.registry import registry

    registry.reset()


@pytest.fixture()
def incendiary_application():
    app = Insanic("tracer")
    Incendiary.init_app(app, AsyncAWSXRayRecorder())

    return app
