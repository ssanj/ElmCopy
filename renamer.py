import re
from typing import NamedTuple

class RenameResult(NamedTuple):
  original_function: str
  function_definition_replacement: str
  function_implementation_replacement: str
  final_result: str


class Renamer:

  def rename(self, original_function: str, existing_name: str, new_name: str) -> RenameResult:
    function_def_replacement_reg: str = f'^{existing_name}(\\s*:)'
    function_impl_replacement_reg: str = f'^{existing_name}(\\s*([a-zA-Z0-9\\(\\),\\{{\\}})]+\\s*)*\\s*=)'
    first_group = r'\1'

    function_with_new_def_name = re.sub(function_def_replacement_reg, f'{new_name}{first_group}', original_function, count = 1, flags = re.MULTILINE)

    function_with_new_impl_name = re.sub(function_impl_replacement_reg, f'{new_name}{first_group}', function_with_new_def_name, count = 1, flags = re.MULTILINE)

    return RenameResult(original_function=original_function, function_definition_replacement=function_with_new_def_name,  function_implementation_replacement=function_with_new_impl_name, final_result=function_with_new_impl_name)

