import copy

from aws_xray_sdk.core.sampling.sampler import DefaultSampler
from aws_xray_sdk.core.sampling.local.sampler import LocalSampler
from insanic import Insanic

from incendiary.loggers import logger


class IncendiaryDefaultSampler(DefaultSampler):
    _sample_rule = {
        "description": str,
        "service_name": str,
        "http_method": str,
        "url_path": str,
        "fixed_target": int,
        "rate": float,
    }

    def __init__(self, app: Insanic) -> None:
        """
        An Incendiary Sampler that determines if a request
        should be sampled or not.
        """
        self.app = app
        super().__init__()
        self._local_sampler = LocalSampler(self.local_rules)

    @property
    def local_rules(self) -> dict:
        rules = copy.deepcopy(self.app.config.INCENDIARY_XRAY_SAMPLING_RULES)
        if not self.app.config.INCENDIARY_XRAY_ENABLED:
            rules.update({"rules": []})
            rules.update({"default": {"fixed_target": 0, "rate": 0}})
        return rules

    def calculate_sampling_decision(
        self, trace_header, recorder, service_name, method, path
    ):
        """
        Return 1 if should sample and 0 if should not.
        The sampling decision coming from ``trace_header`` always has
        the highest precedence. If the ``trace_header`` doesn't contain
        sampling decision then it checks if sampling is enabled or not
        in the recorder. If not enabled it returns 1. Otherwise it uses
        sampling rule to decide.
        """
        if trace_header.sampled is not None and trace_header.sampled != "?":
            logger.debug(
                f"Sample decision: {trace_header.sampled} (from trace headers"
            )
            return trace_header.sampled
        elif not self.app.config.INCENDIARY_XRAY_ENABLED:
            logger.debug("Sample decision: False (from insanic config)")
            return 0
        elif not recorder.sampling:
            logger.debug("Sample decision: True (from recorder sampling)")
            return 1
        elif self.should_trace(sampling_req={"method": method, "path": path}):
            logger.debug("Sample decision: True (from sampler rules)")
            return 1
        else:
            logger.debug("Sample decision: False (not sampled)")
            return 0
