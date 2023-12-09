from typing import Callable, Set
from src.model.enum import FeatureType


class Servicer():
    def name() -> str:
        pass

    def get_feature(feature_name: str) -> (FeatureType, Callable):
        pass