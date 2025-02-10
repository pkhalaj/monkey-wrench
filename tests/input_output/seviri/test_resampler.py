from unittest import mock

from monkey_wrench.input_output.seviri import RemoteSeviriFile, Resampler
from tests.geometry.test_models import get_area_definition

# ======================================================
### Tests for RemoteSeviriFile()

def test_RemoteSeviriFile(get_token_or_skip):
    product_id = "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA"
    fs_file = RemoteSeviriFile().open(product_id)
    assert f"{product_id}.nat" == fs_file.open().name


# ======================================================
### Tests for Resampler()

def test_Resampler(temp_dir, get_token_or_skip):
    product_id = "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA"
    fs_file = RemoteSeviriFile().open(product_id)

    scene = mock.MagicMock()
    scene.load = mock.MagicMock()
    resampled_scene = mock.MagicMock()
    scene.resample = mock.MagicMock(return_value=resampled_scene)

    with mock.patch("monkey_wrench.input_output.seviri._models.Scene", return_value=scene) as scene_class:
        resampler = Resampler(parent=temp_dir, area=get_area_definition())
        resampler.resample(product_id)

        scene_class.assert_called_once_with([fs_file], "seviri_l1b_native")
        scene.load.assert_called_once_with(resampler.channel_names)
        scene.resample.assert_called_once_with(resampler.area, radius_of_influence=resampler.radius_of_influence)

        resampled_scene.save_datasets.assert_called_once_with(
            filename=f"{temp_dir}/2023/04/13/seviri_20230413_16_42.nc",
            **resampler.dataset_save_options
        )
