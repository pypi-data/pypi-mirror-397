from enum import Enum


class SceneType(str, Enum):
    CAMERAS = "cameras"
    LIDARS_AND_CAMERAS = "lidars_and_cameras"
    CAMERAS_SEQUENCE = "cameras_sequence"
    LIDARS_AND_CAMERAS_SEQUENCE = "lidars_and_cameras_sequence"
    AGGREGATED_LIDARS_AND_CAMERAS_SEQUENCE = "aggregated_lidars_and_cameras_sequence"
