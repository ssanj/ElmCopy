from re import DOTALL
import sublime, sublime_plugin
from typing import Optional, List

from . import function_detail as FD

import re

class ElmCopyCommand(sublime_plugin.TextCommand):

  print("ElmCopy is running........")
  function_def_reg: str = r'^([a-z][a-z|A-Z|0-9]*)\s*:\s*[A-Z]'
  let_statement_reg = r'^\s+let'
  in_statement_reg = r'^\s+in'
  debug = True

  def run(self, edit: sublime.Edit) -> None:
    if self and self.view:
      print("ElmCopy is running")

      starting_region = self.view.sel()[0] # check if this is valid
      last_line_number = self.get_last_line_number(self.view)


      function_detail = self.find_top_of_function(self.view, starting_region)

      function_definiton_region = function_detail.function_region
      starting_line = self.region_to_row(self.view, starting_region)

      starting_region_converted = self.row_to_region(self.view, starting_line)
      line = self.get_region_line(self.view, starting_region)

      ending_region = self.find_bottom_of_function(self.view, starting_region, last_line_number)

      if ElmCopyCommand.debug:
        print(f"starting region={starting_region}")
        print(f"function name={function_detail.function_name}")

        print(f"first line number={starting_line}")
        print(f"last line={last_line_number}")

        print(f"starting line={line}")
        print(f"starting region from line={starting_region_converted}")
        print(f"ending region={ending_region}")

      self.copy_function(self.view, function_definiton_region, ending_region)
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

  def copy_function(self, view: sublime.View, starting: sublime.Region, ending: sublime.Region):
    function_region = sublime.Region(starting.begin(), ending.end())
    print(f"body region: {function_region}")
    function_body = self.get_all_region_lines(view, function_region)
    print(f"body: {function_body}")
    # view.set_clipboard(function_body)

  def get_last_line_number(self, view: sublime.View) -> int:
    region = sublime.Region(0, view.size())
    (row, _) = view.rowcol(region.end())
    return row + 1

  def find_top_of_function(self, view: sublime.View, starting_from: sublime.Region) -> FD.FunctionDetail:
    safe_guard = 0
    region = starting_from

    while safe_guard < 10: # make this configurable
      line = self.get_region_line(view, region)
      function_names = re.findall(ElmCopyCommand.function_def_reg, line)

      if len(function_names) != 0:
        return FD.FunctionDetail(function_names[0], region)
      else:
        line_number: int = self.region_to_row(view, region)
        prev_line_number: int = line_number - 1

        if prev_line_number < 0:
          raise Exception("Exceeded beginning of file");

        region = self.row_to_region(view, prev_line_number)
        safe_guard += 1

    raise Exception("safe_guard exceeded")

  def find_bottom_of_function(self, view: sublime.View, starting_from: sublime.Region, last_line: int) -> sublime.Region:
    safe_guard = 0
    lets = 0
    region = starting_from

    while safe_guard < 10: # make this configurable
      line = self.get_region_line(view, region)
      print(f"line: {safe_guard} {line}")

      if len(line) == 0 and lets == 0:
        return region
      else:
        if re.match(ElmCopyCommand.let_statement_reg, line) is not None:
          # check for let, increment if found
          lets += 1
        elif re.match(ElmCopyCommand.in_statement_reg, line) is not None:
          # check for in, decrement lets if found
          lets -= 1


        line_number: int = self.region_to_row(view, region)
        next_line_number: int = line_number + 1
        print(f"next_line_number: {safe_guard} {next_line_number}")

        # check for jumping over the last line of the file
        region = self.row_to_region(view, next_line_number)

        safe_guard +=1

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

  def get_all_region_lines(self, view: sublime.View, region: sublime.Region) -> str:
    line_regions: List[sublime.Region] = view.lines(region)
    lines = list(map(lambda region: view.substr(region), line_regions))
    return '\n'.join(lines)
