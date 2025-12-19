import sys
from pathlib import Path
import pytest

new_lib_path = str(Path(__file__).resolve().parents[1])

sys.path.append(new_lib_path)

from src.dmmp.args import _get_toml_args, validate_args, write_args_to_toml, get_args
from src.dmmp.exceptions import MissingArgumentException
import os
import json
import tomllib


generic_dict = {"data1":"1", "data2":"2"}

def test_get_toml_args():
   data = _get_toml_args(os.path.join(os.getcwd(), "tests", "test_content", "config.toml"))
   assert data == {"data":"test"}

def test_validate_args():
   validate_args(generic_dict, ["data1", "data2"])

   with pytest.raises(MissingArgumentException):
      validate_args({"not_data1":"1", "data2":"2"}, ["data1", "data2"])

def test_write_args_to_toml():
   path = os.path.join(os.getcwd(), "tests", "temp.toml")
   write_args_to_toml(generic_dict, path)
   data = _get_toml_args(path)
   assert data == generic_dict  
   os.remove(path)


def get_cli_args_and_output(key: str):
   cli_args = json.load(open("tests/cli_inputs.json"))[key]
   output = json.load(open("tests/outputs.json"))[key]
   return cli_args, output

def test_get_args_case1():
   cli_args = {
        "config_file": "test_content/case1.toml",
        "dirs_to_map": [["src", "2"], ["tests", "1"]],
        "folders_ignore": [".git", "__pycache__"],
        "save_path": "./output",
        "name_output": "scan-result",
        "metadata_file_names": ["meta", "info"]
   } 
   
   output = {
        "config_file": "test_content/case1.toml",
        "dirs_to_map": [["src", "2"], ["tests", "1"]],
        "folders_ignore": [".git", "__pycache__"],
        "save_path": "./output",
        "name_output": "scan-result",
        "metadata_file_names": ["meta", "info"]
   }
   assert(get_args(**cli_args) == output)
   

def test_get_args_case2():
   cli_args = {
        "dirs_to_map": [["src", "2"], ["tests", "1"]],
        "folders_ignore": [".git", "__pycache__"],
        "save_path": "./output",
        "name_output": "scan-result",
        "metadata_file_names": ["meta", "info"]
   } 
   
   output = {
        "config_file": "config.toml",
        "dirs_to_map": [["src", "2"], ["tests", "1"]],
        "folders_ignore": [".git", "__pycache__"],
        "save_path": "./output",
        "name_output": "scan-result",
        "metadata_file_names": ["meta", "info"]
   }
   assert(get_args(**cli_args) == output)

def test_get_args_case2():
   cli_args = {} 
   
   output = {
        "config_file": "config.toml",
        "folders_ignore": [],
        "save_path": os.getcwd(),
        "name_output": "dmmp-output",
        "metadata_file_names": ["*"]
   }
   assert(get_args(**cli_args) == output)

def test_get_args_case3():
   cli_args = {
      "config_file": "tests/test_content/case3.toml"
   } 
   
   output = {
        "config_file": "tests/test_content/case3.toml",
        "folders_ignore": [".venv", "node_modules"],
        "save_path": "C:/temp",
        "name_output": "specific-name",
        "metadata_file_names": ["desc", "test"]
   }
   assert(get_args(**cli_args) == output)
