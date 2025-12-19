import os
from tqdm import tqdm
import re
from .exceptions import DirectoryAlreadyExists


class Mapper():
   def __init__(
      self, 
      save_path: str, 
      dir_output_name: str, 
      folders_to_ignore: list[str], 
      metadata_file_names: list[str]
      ):
      self._assert_directory_exists(save_path, dir_output_name)
      self._folders_to_ignore = {item for item in folders_to_ignore}
      self._save_path = save_path
      self._progress_bar = tqdm(total=100)
      self._folders_sum = 0
      self._metadata_file_names = {item for item in metadata_file_names}
      self._temp_mapping = {}
      self._dir_output_name = dir_output_name
      self._progress_bar_percentage = 0
   

   def _assert_directory_exists(
      self, 
      save_path: str, 
      dir_output_name: str
      ):
      """Tests if given directory exists.

      :param save_path: path to save.
      :param dir_output_name: name of output to save. 
      """
      path = os.path.join(save_path, dir_output_name)
      if os.path.exists(path):
         raise DirectoryAlreadyExists(path) 


   def __call__(
      self,
      dirs_to_map: str
      ):
      """Scan, store and output a directory.

      Scan all directories necessary, saving important data on the
      object's state, lastly, it prints some data about the operation
      and saves the output.
      
      :param dirs_to_map: directories to map.
      """
      for index, array in enumerate(dirs_to_map):
         path = array[0]
         nested_folders = int(array[1])
         load_bar_start = index/len(dirs_to_map)*100
         load_bar_end = (index+1)/len(dirs_to_map)*100
         self._read_dir(path, nested_folders, load_bar=True, load_bar_start=load_bar_start, load_bar_end=load_bar_end)
      self._write_map()
      self._update_progress_bar(percentage=100, post_fix="Finished", close=True)
    
      print(f"{self._folders_sum} items were scanned.")
      output_path = os.path.join(self._save_path, self._dir_output_name)
      if os.path.exists(output_path):
         print(f"Output saved on path: {output_path}")
      else:
         print(f"No content to save.")


   def _update_progress_bar(
      self, 
      percentage: float, 
      post_fix: str, 
      close: bool=False
      ):
      """Updates progress bar state.

      :param percentage: percentage the process is in.
      :param post_fix: hint to what item is being currently processed. 
      :param close: represents if the progress bar needs to be closed.
      """
      val = float(f"{percentage:.2f}")
      self._progress_bar.n = val
      self._progress_bar_percentage = val
      
      self._progress_bar.refresh()
      self._progress_bar.set_postfix_str(post_fix)
      if close:
         self._progress_bar.close()


   def _read_dir(
      self,
      directory: str, 
      max_rec: int, 
      current_rec: int=0, 
      load_bar: bool=False, 
      load_bar_start: int=0, 
      load_bar_end: int=100
      ):
      """Recursively reads folders and update objects state.

      Recursively calls itself, entering all the necessary sub folders. 
      Check for files with specific names and reads them, updating the 
      mapping of content and the progress bar.

      :param directory: directory to scan.
      :param max_rec: max subfolders to scan.
      :param current_rec: current subfolder count.
      :param load_bar: if the load bar will be updated.
      :param load_bar_start: the start of the load bar percentage.
      :param load_bar_end: the end of the load bar percentage.
      """

      if ("*" in self._metadata_file_names and directory.endswith(".dmmp")) \
                                 or any(directory.endswith(f"{item}.dmmp") \
                                 for item in self._metadata_file_names):
         self._get_desc_data(directory)
      if current_rec>max_rec or not os.path.isdir(directory):
         return
      folders = os.listdir(directory)
      
      for index, folder in enumerate(folders):
         if folder not in self._folders_to_ignore:  
            self._read_dir(
               fr"{directory}\{folder}",
               max_rec=max_rec, 
               current_rec=current_rec+1)
            self._folders_sum = self._folders_sum+1
         if load_bar:
            percentage = index/len(folders)
            diff = load_bar_end-load_bar_start
            relative_percentage = (percentage*diff)+load_bar_start
            self._update_progress_bar(
               percentage=relative_percentage, 
               post_fix=folder)


   def _get_desc_data(
      self,
      directory: str
      ):
      """Get data from a directory and store its data.

      Find the file, open it, read line by line and store in the
      internal mapping.

      :param directory: file path to read.
      """
      with open(directory, "r", encoding="utf-8") as f:
            id = f.readline().strip()
            folder_path = f.readline().strip()
            name = f.readline().strip()
            desc = f.readline().strip()
            self._temp_mapping[id] = {            
               "name":name,
               "desc":desc,
               "folder":folder_path,
               "origin":"/".join(directory.split("\\"))
            }


   def _write_map(self):
      """Write the mapping to a directory.

      Get all the data saved on the internal mapping and write it to a 
      tree of separate files in a specific directory.
      """
      self._assert_directory_exists(self._save_path, self._dir_output_name)

      path = os.path.join(self._save_path, self._dir_output_name)
      
      for id, object in self._temp_mapping.items():
         temp_path = os.path.join(path, object.get("folder"))
         os.makedirs(temp_path, exist_ok=True)
         id_to_change = re.findall(r"\[\[(.*?)\]\]", object.get("desc"))
         desc = object.get("desc")

         for id in id_to_change:
            desc = desc.replace(id, self._get_link(id))

         with open(
            os.path.join(temp_path, f"{object.get("name")}.md"), 
            "w", 
            encoding="utf-8"
         ) as f1:
            f1.write(f"{desc}\n\nid: {id}\norigin: {object.get("origin")}")


   def _get_link(
      self, 
      id
      ):
      """Get markdown friendly from an id.

      Finds the output path of the item and use it to build a mardown 
      friendly link that can redirect to that path when clicked.

      :param id: id of the item.
      """
      obj = self._temp_mapping.get(id.strip())
      if obj:
         return f"{obj.get("folder")}/{obj.get("name")}|{obj.get("name")}"
      else:
         return f"{id}"