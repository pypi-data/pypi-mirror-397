from __future__ import absolute_import

import pytest

import examples.get_scene_summary as get_scene_summary_example
import kognic.io.client as IOC


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestGetSceneSummary:
    def test_get_scene_summary(self, client: IOC.KognicIOClient, existing_lacs_scene_uuid: str):
        scene_summary = get_scene_summary_example.run(client=client, scene_uuid=existing_lacs_scene_uuid)
        assert len(scene_summary.metadata.keys()) > 0
        assert scene_summary.is_motion_compensated is True
        assert scene_summary.frame_relative_times is not None
        assert scene_summary.frame_relative_times[0] == 0
        assert scene_summary.scene_uuid == existing_lacs_scene_uuid
