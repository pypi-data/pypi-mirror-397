import sys; sys.path.insert(0, "/home/kamel/Code/git/sftppathlib")
import pytest
from sftppathlib import get_config_path, load_configs


def test_config():
    config_path = get_config_path()
    config = load_configs(config_path)

    assert config == {'tomelet.com': {'root': 'www', 'hostname': 'sftp.domeneshop.no', 'port': '22', 'username': 'tomelet', 'password': 'Smal-Byste-Gk-imot-88'}, 'elisefilm.no': {'root': 'www', 'hostname': 'sftp.domeneshop.no', 'port': '22', 'username': 'tomelet', 'password': 'Smal-Byste-Gk-imot-88'}}
