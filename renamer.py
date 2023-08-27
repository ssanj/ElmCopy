import re
from typing import NamedTuple

class Renamer:

  def rename(self, original_function: str, existing_name: str, new_name: str) -> str:
    function_def_replacement_reg: str = f'^{existing_name}(\\s*:)'
    function_impl_replacement_reg: str = f'^{existing_name}(\\s*([a-zA-Z0-9]+\\s*)*\\s*=)'
    first_group = r'\1'

    function_with_new_def_name = re.sub(function_def_replacement_reg, f'{new_name}{first_group}', original_function, count = 1, flags = re.MULTILINE)
    function_with_new_impl_name = re.sub(function_impl_replacement_reg, f'{new_name}{first_group}', function_with_new_def_name, count = 1, flags = re.MULTILINE)

    return function_with_new_impl_name

