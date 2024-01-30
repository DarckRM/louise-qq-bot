from typing import Callable, Set

from botpy.message import DirectMessage
from src.model.enum import FeatureType


class Servicer():
    def name() -> str:
        pass

    async def invoke(message: DirectMessage) -> bool:
        pass

    def get_feature(feature_name: str) -> (FeatureType, Callable):
        pass