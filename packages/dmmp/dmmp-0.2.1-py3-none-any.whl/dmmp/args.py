import tomllib
import tomli_w
import os
from .exceptions import MissingArgumentException


def _get_toml_args(
   path: str
   ):
   """Get the arguments in a .toml file
   
   :param path: The path of the .toml file
   """
   try:
      with open(path, "rb") as f:
         data = tomllib.load(f)
         return data
      
   except Exception as e:
      return {}


def get_args(
   config_file: str = None,
   dirs_to_map: list[tuple[str, str]] = None, 
   folders_ignore: list[str] = None,
   save_path: str = None,
   name_output: str = None,
   metadata_file_names: str = None
   ):
   """Merge the arguments passed by the CLI and the configuration file.

   Scan the configuration .toml file and the arguments passed in the
   CLI, creates a new dict and returns it, with the CLI arguments being
   the priority.

   :param config_file: .toml file to get configuration from.
   :param dirs_to_map: Directory to scan + number of nested folders to iterate.
   :param folders_ignore: List of folders to ignore.
   :param save_path: Path to save output.
   :param name_output: Name of the output directory.
   :param metadata_file_names: File names containing the directory metadata (no extension).   
   """

   # It's ok to be null, toml shouldnt be considered if not specified
   toml_dict = _get_toml_args(config_file)
   
   cli_dict = {
      k:v for k, v in {
      "config_file":config_file,
      "dirs_to_map":dirs_to_map,
      "folders_ignore":folders_ignore,
      "save_path":save_path,
      "name_output":name_output,
      "metadata_file_names":metadata_file_names,
      }.items() if v !=None
   }

   merged_dict = toml_dict | cli_dict

   # if there is no toml nor cli argument, fallback to default ones.
   # they weren't set as default arguments because the default arguments
   # would override the toml ones everytime, that's why they are done
   # after the merge
   merged_dict["folders_ignore"] = merged_dict.get("folders_ignore", [])
   merged_dict["save_path"] = merged_dict.get("save_path", os.getcwd())
   merged_dict["config_file"] = merged_dict.get("config_file", "config.toml")
   merged_dict["name_output"] = merged_dict.get("name_output", "dmmp-output") 
   merged_dict["metadata_file_names"] = \
      merged_dict.get("metadata_file_names", ["*"]) 

   return merged_dict


def validate_args(
   args: dict, 
   required_args: list[str]
   ):
   """Validate args.

   Compare if all args in a dict are present in required args.
   
   :param args: arguments.
   :param required_args: arguments that should be present in argument 
   keys.
   """
   for arg in required_args:
      if arg not in args.keys():
         raise MissingArgumentException(arg)
    

def write_args_to_toml(
   args: dict, 
   config_file_name: str
   ):
   """Write given args to a .toml file.

   :param args: arguments to write.
   :param config_file_name: the .toml output file name.
   """
   temp_args = args.copy()
   if temp_args.get("save_path") == os.getcwd():
      del temp_args["save_path"]

   if temp_args.get("config_file"):
      del temp_args["config_file"]
   
   with open(os.path.join(os.getcwd(), config_file_name), "wb") as f:
      tomli_w.dump(temp_args, f)