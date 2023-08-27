import sublime

from . import elm_copy_setting as ECS

class SettingsLoader:
  def __init__(self, settings: sublime.Settings) -> None:
    self.settings = settings

  def load(self) -> ECS.ElmCopySetting:
    max_function_length: int = self.get_max_function_length()
    debug: bool = self.get_debug()
    margin: int = self.get_margin()

    return ECS.ElmCopySetting(max_function_length, debug, margin)

  def get_max_function_length(self) -> int:
    if self.settings.has("max_function_length"):
      return self.settings.get("max_function_length")
    else:
      print(f'[ElmCopy] - max_function_length setting not defined, defaulting to 20')
      return 20

  def get_debug(self) -> bool:
    if self.settings.has("debug"):
      return self.settings.get("debug")
    else:
      print(f'[ElmCopy] - debug setting not defined, defaulting to false')
      return False

  def get_margin(self) -> int:
    if self.settings.has("margin"):
      return self.settings.get("margin")
    else:
      print(f'[ElmCopy] - margin setting not defined, defaulting to 2')
      return 20
