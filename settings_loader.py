import sublime

from . import elm_copy as ECC
from . import elm_copy_setting as ECS

class SettingsLoader:

  default_max_function_length: int = 100
  default_debug: bool = False
  default_margin: int = 2

  def __init__(self, settings: sublime.Settings) -> None:
    self.settings = settings
    self.log = ECC.ElmCopyCommand.warn

  def load(self) -> ECS.ElmCopySetting:
    max_function_length: int = self.get_max_function_length()
    debug: bool = self.get_debug()
    margin: int = self.get_margin()

    return ECS.ElmCopySetting(max_function_length, debug, margin)

  def get_max_function_length(self) -> int:
    if self.settings.has("max_function_length"):
      return self.settings.get("max_function_length")
    else:
      self.log(f'max_function_length setting not defined, defaulting to {SettingsLoader.default_max_function_length}')
      return SettingsLoader.default_max_function_length

  def get_debug(self) -> bool:
    if self.settings.has("debug"):
      return self.settings.get("debug")
    else:
      self.log(f'debug setting not defined, defaulting to {SettingsLoader.default_debug}')
      return SettingsLoader.default_debug

  def get_margin(self) -> int:
    if self.settings.has("margin"):
      return self.settings.get("margin")
    else:
      self.log(f'margin setting not defined, defaulting to {SettingsLoader.default_margin}')
      return SettingsLoader.default_margin
