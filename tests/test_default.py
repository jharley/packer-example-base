def test_ami_launch(host):
    assert host.system_info.type == 'linux'
