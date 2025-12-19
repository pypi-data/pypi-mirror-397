from dotenv import load_dotenv
import argparse
from .mapper import Mapper
from .args import get_args, validate_args, write_args_to_toml


if __name__ == "__main__":

   load_dotenv()  

   parser = argparse.ArgumentParser(
      prog="DMM",
      description="Directory Metadata Mapper"
   )
   add_arg = parser.add_argument
   add_arg('-c', '--config-file', 
            required=False, 
            help=".toml file to get configuration from ") 
   
   add_arg('-d', '--dirs-to-map', 
            required=False, 
            help="Directory to scan + number of nested folders to iterate", 
            nargs=2, 
            action="append")
   
   add_arg('-i', '--folders-ignore', 
            required=False, 
            help="List of folders to ignore", 
            nargs="+")
   
   add_arg('-s', '--save-path', 
            required=False, 
            help="Path to save output")
   
   add_arg('-n', '--name-output', 
            required=False, 
            help="Name of the output directory")
   
   add_arg('-m', '--metadata-file-names', 
            required=False, 
            help="File names containing the directory metadata (no extension)",
            nargs="+")
   
   args = parser.parse_args()
   
   formatted_args = get_args(**vars(args))

   required_args = [
      "dirs_to_map",
      "folders_ignore",
      "save_path",
      "name_output",
      "metadata_file_names",
      ]


   validate_args(formatted_args, required_args=required_args)

   mapper = Mapper(formatted_args.get("save_path"),
                  formatted_args.get("name_output"), 
                  formatted_args.get("folders_ignore"), 
                  formatted_args.get("metadata_file_names"))
   mapper(formatted_args.get("dirs_to_map"))
   
   write_args_to_toml(formatted_args, formatted_args["config_file"])