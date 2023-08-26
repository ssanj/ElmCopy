from re import DOTALL
import sublime, sublime_plugin
from typing import Optional, List

import re

class ElmCopyCommand(sublime_plugin.TextCommand):

  print("ElmCopy is running........")
  function_def_reg: str = r'^([a-z][a-z|A-Z|0-9]*)\s*:\s*[A-Z]'

  def run(self, edit: sublime.Edit) -> None:
    if self and self.view:
      print("ElmCopy is running")
      top = self.find_top_of_function(self.view)
      starting_line = self.region_to_row(self.view, top)
      starting_region = self.row_to_region(self.view, starting_line)
      line = self.get_region_line(self.view, starting_region)

      print(f"starting region={top}")
      print(f"starting line={starting_line}")
      print(f"starting region={starting_region}")
      print(f"starting line={line}")
    else:
      sublime.message_dialog("Could not find self")

  def is_enabled(self) -> bool:
    return self.is_elm()


  def is_visible(self) -> bool:
    return self.is_elm()

  def is_elm(self) -> bool:
     syntax: Optional[sublime.Syntax] = self.view.syntax()
     if syntax is not None:
        return syntax.name == 'Elm'
     else:
        return False

  def find_top_of_function(self, view: sublime.View) -> sublime.Region:
    region = view.sel()[0] # check if this is valid
    safe_guard = 0

    while safe_guard < 10: # make this configurable
      line = self.get_region_line(view, region)
      function_names = re.findall(ElmCopyCommand.function_def_reg, line)

      if len(function_names) != 0:
        return region
      else:
        line_number: int = self.region_to_row(view, region)
        prev_line_number: int = line_number - 1

        if prev_line_number < 0:
          raise Exception("Exceeded beginning of file");

        region = self.row_to_region(view, prev_line_number)
        safe_guard += 1

    raise Exception("safe_guard exceeded")

  def region_to_row(self, view: sublime.View, region: sublime.Region) -> int:
    start = region.begin()
    (row, _) = view.rowcol(start)
    return row + 1

  def row_to_region(self, view: sublime.View, row: int) -> sublime.Region:
    # row should be zero-based to text_point, but we use 1-base in the code
    point = view.text_point(max(row - 1, 0), 0)
    return view.line(point)

  def get_region_line(self, view: sublime.View, region: sublime.Region) -> str:
    line_region = view.line(region)
    return view.substr(line_region)
