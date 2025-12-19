class DirectoryAlreadyExists(Exception):
   def __init__(
      self, 
      path
      ):
      super().__init__(f"Output directory ({path}) already exists,cannot \
         overwrite it")


class MissingArgumentException(Exception):
   def __init__(
      self, 
      arg
      ):
      super().__init__(f"Missing argument (--{arg.replace("_", "-")})")