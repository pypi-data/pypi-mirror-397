from datetime import datetime
from typing import List, Optional, Union

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.scene.scene_type import SceneType

SceneMetadata = dict[str, Union[str, bool, int, float]]


class SceneSummary(BaseSerializer):
    scene_uuid: str
    external_id: str
    workspace_id: str
    created: datetime
    calibration_id: Optional[str] = None
    frame_relative_times: Optional[List[int]] = None
    lidars: Optional[set[str]] = None
    cameras: Optional[set[str]] = None
    scene_type: SceneType
    is_multi_sensor: bool
    is_motion_compensated: bool
    metadata: SceneMetadata = {}
