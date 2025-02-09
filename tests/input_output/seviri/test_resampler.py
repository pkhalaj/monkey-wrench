def test_open_seviri_native_remotely(get_token_or_skip):
    from monkey_wrench.input_output.seviri import RemoteSeviriFile
    product_id = "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA"
    fs_file = RemoteSeviriFile().open(product_id)
    assert f"{product_id}.nat" == fs_file.open().name
