from typing import NamedTuple
import sublime

class FunctionDetail(NamedTuple):
  function_name: str
  function_region: sublime.Region
