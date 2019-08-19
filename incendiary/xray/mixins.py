from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.async_recorder import AsyncSubsegmentContextManager
from aws_xray_sdk.core.models.subsegment import SubsegmentContextManager


class CaptureMixin:

    @classmethod
    def capture_async(cls, name=None):
        """
        A decorator that records enclosed function in a subsegment.
        It only works with asynchronous function

        :param str name: The name of the subsegment. If not specified the function name will be used.
        :return:
        """
        return AsyncSubsegmentContextManager(xray_recorder, name=name)

    @classmethod
    def capture(self, name=None):
        """
        Return a subsegment context manger.
        :param str name: the name of the subsegment. If not specified the function name will be used.
        """
        return SubsegmentContextManager(xray_recorder, name=name)
    #
