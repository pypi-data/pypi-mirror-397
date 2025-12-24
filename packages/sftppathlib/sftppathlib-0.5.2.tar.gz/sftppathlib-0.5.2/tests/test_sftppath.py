import sys; sys.path.insert(0, "/home/kamel/Code/git/sftppathlib")
import pytest
from sftppathlib import SFTPPath, load_configs, get_config_path

# SFTPPath.set_authority("tomelet.com", "www")

def test_non_implemented_abstractmethod():
    path = SFTPPath("sftp://tomelet.com")
    with pytest.raises(NotImplementedError):
        path.hardlink_to("hello")


def test_read():
    path = SFTPPath("sftp://tomelet.com/tmp")
    assert path.exists()


def test_alias():
    path = SFTPPath("sftp://tomelet.com/")
    assert repr(path) == "SFTPPath('sftp://tomelet.com/')"


def test_read_alias():
    path = SFTPPath("sftp://tomelet.com/")
    assert path.exists()


def test_iterdir():
    path = SFTPPath("sftp://tomelet.com/tmp")
    assert len(list(path.iterdir())) > 1


def test_from_config():
    configs = load_configs(get_config_path())
    path = SFTPPath.from_config("sftp://example.com",
        config=configs["tomelet.com"])
    assert str(path) == "SFTPPath('sftp://example.com')"
