import os,tempfile
from pathlib import Path
import pytest

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch):
    from app import storage
    handle,path=tempfile.mkstemp(suffix=".db");os.close(handle);monkeypatch.setattr(storage,"DB_PATH",Path(path));storage.initialize();yield;os.unlink(path)
