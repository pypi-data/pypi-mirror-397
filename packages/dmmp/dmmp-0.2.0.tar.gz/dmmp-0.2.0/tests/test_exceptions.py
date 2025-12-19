import sys
from pathlib import Path
import pytest

new_lib_path = str(Path(__file__).resolve().parents[1])

sys.path.append(new_lib_path)

from src.dmmp.exceptions import (
   MissingArgumentException,
   DirectoryAlreadyExists,
) 
                                 
import pytest

def test_missing_argument():
   with pytest.raises(MissingArgumentException):
      raise MissingArgumentException("test")


def test_directory_already_exists():
   with pytest.raises(DirectoryAlreadyExists):
      raise DirectoryAlreadyExists("test")