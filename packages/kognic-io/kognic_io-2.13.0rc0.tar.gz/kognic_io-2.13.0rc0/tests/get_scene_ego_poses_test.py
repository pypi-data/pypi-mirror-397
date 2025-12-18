from __future__ import absolute_import

import pytest

import examples.get_scene_ego_poses as get_scene_ego_poses_example
import kognic.io.client as IOC


@pytest.mark.integration
class TestGetSceneEgoPoses:
    def test_get_scene_ego_poses(self, client: IOC.KognicIOClient, existing_lacs_scene_with_ego_poses_uuid: str):
        ego_poses = get_scene_ego_poses_example.run(client=client, scene_uuid=existing_lacs_scene_with_ego_poses_uuid)
        assert ego_poses is not None
        assert len(ego_poses) == 2
        assert "1" in ego_poses
        assert "2" in ego_poses
        assert ego_poses["1"].position.x == pytest.approx(0.321306, rel=1e-4)

    def test_get_scene_ego_poses_none(self, client: IOC.KognicIOClient, existing_lacs_scene_uuid: str):
        ego_poses = client.scene.get_ego_poses(scene_uuid=existing_lacs_scene_uuid)
        assert ego_poses is None

    def test_get_scene_ego_poses_invalid_scene(self, client: IOC.KognicIOClient):
        ego_poses = client.scene.get_ego_poses(scene_uuid="00000000-0000-0000-0000-000000000000")
        assert ego_poses is None
