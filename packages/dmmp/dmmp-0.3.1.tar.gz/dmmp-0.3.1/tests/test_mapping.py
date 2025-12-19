import sys
from pathlib import Path
import pytest

new_lib_path = str(Path(__file__).resolve().parents[1])

sys.path.append(new_lib_path)

from src.dmmp.exceptions import DirectoryAlreadyExists
from src.dmmp.mapper import Mapper
import os
import shutil

mapper = Mapper("", "", ["desc"], ["*"])


def test_get_link():
   mapper._temp_mapping = {
      "id":{
         "folder":"/path/here",
         "name":"test"
      }
   }
   assert(mapper._get_link("id") == "/path/here/test|test")
   mapper._temp_mapping = {}

def test_get_desc_data():
   
   mapper._get_desc_data(os.path.join(
         "tests", 
         "test_content", 
         "desc.dmmp"))
   
   assert(
      mapper._temp_mapping == 
         {
            "123":{
               "name":"data",
               "desc":"data\ntest\n\n\ntest\n",
               "folder":"data/",
               "origin":"tests/test_content/desc.dmmp"
            }
         }
      )

def test_update_progress_bar():
   mapper._update_progress_bar(50, "Task 5")   
   assert(mapper._progress_bar.postfix == "Task 5")
   assert(mapper._progress_bar_percentage == 50)


mapper1_path = os.path.join(os.getcwd(), "tests", "test_content")
mapper1 = Mapper(
   mapper1_path,
   "temp",
   ["desc"],
   ["*"]
)

def test_write_map_and_assert_dir_exists():
   mapper1._temp_mapping = {
      "123":{
         "name":"data",
         "desc":"data",
         "folder":"data/",
         "origin":"tests/test_content/desc.dmmp"
      }
   }
   mapper1._write_map()
   
   with pytest.raises(DirectoryAlreadyExists):
      mapper1._write_map()

   with pytest.raises(DirectoryAlreadyExists):
      mapper1._assert_directory_exists(mapper1_path, "temp")
   
   shutil.rmtree(os.path.join(mapper1_path, "temp"))
   mapper1._assert_directory_exists(mapper1_path, "temp")
