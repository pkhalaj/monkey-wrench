from unittest import mock

from monkey_wrench.input_output.seviri import RemoteSeviriFile, Resampler
from tests.geometry.test_models import get_area_definition

# ======================================================
### Tests for RemoteSeviriFile()

product_id = "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA"


def test_RemoteSeviriFile(temp_dir, get_token_or_skip):
    fs_file = RemoteSeviriFile(fsspec_cache="filecache").open(product_id, temp_dir)
    assert f"{product_id}.nat" == fs_file.open().name


# ======================================================
### Tests for Resampler()

def test_Resampler(temp_dir, get_token_or_skip):
    scene = mock.MagicMock()
    scene.load = mock.MagicMock()
    resampled_scene = mock.MagicMock()
    scene.resample = mock.MagicMock(return_value=resampled_scene)

    with mock.patch("monkey_wrench.input_output.seviri._models.Scene", return_value=scene) as scene_class:
        resampler = Resampler(parent_output_directory_path=temp_dir, area=get_area_definition())
        resampler.resample(product_id)

        scene.load.assert_called_once_with(resampler.channel_names)
        scene.resample.assert_called_once_with(resampler.area, radius_of_influence=resampler.radius_of_influence)

        resampled_scene.save_datasets.assert_called_once_with(
            filename=f"{temp_dir}/2023/04/13/seviri_20230413_16_42.nc",
            **resampler.dataset_save_options
        )
        [file_list, reader], _ = scene_class.call_args
        assert str(file_list) == '[<FSFile "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA.nat">]'
        assert reader == "seviri_l1b_native"
