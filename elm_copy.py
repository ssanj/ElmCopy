import sublime, sublime_plugin
from typing import Optional, List

from . import function_detail as FD
from . import settings_loader as SL
from . import elm_copy_setting as ECS
import re

class ElmCopyCommand(sublime_plugin.TextCommand):

  print("ElmCopy is running........")
  function_def_reg: str = r'^([a-z][a-z|A-Z|0-9]*)\s*:(\s*$|\s*[A-Z])'
  let_statement_reg = r'^\s+let(\s*$|\s+[A-Z|a-z|0-9]+)'
  in_statement_reg = r'^\s+in(\s*$|\s+[A-Z|a-z|0-9]+)'
  debug = True

  def run(self, edit: sublime.Edit) -> None:
    if self and self.view:
      print("ElmCopy is running")
      self.settings: sublime.Settings = sublime.load_settings('elm_copy.sublime-settings')
      settings_loader = SL.SettingsLoader(self.settings)
      elm_copy_settings = settings_loader.load()
      print(f'[ElmCopy] - settings: {elm_copy_settings}')

      cursor_location_region = self.view.sel()[0] # check if this is valid
      last_line_number_in_file = self.get_last_line_number(self.view)

      function_detail = self.find_top_of_function(self.view, cursor_location_region)

      start_of_function_definiton_region = function_detail.function_region
      function_name = function_detail.function_name
      starting_line = self.region_to_row(self.view, cursor_location_region)

      starting_region_converted = self.row_to_region(self.view, starting_line)
      line = self.get_region_line(self.view, cursor_location_region)

      # We need to search for the bottom of the function, starting from the very top of the definition,
      # not, where the cursor is. This is because we want to handle let/in pairs, which can't be
      # tracked from the middle of the function
      end_of_function_implementation_region = self.find_bottom_of_function(self.view, start_of_function_definiton_region, last_line_number_in_file)

      if ElmCopyCommand.debug:
        print(f"starting region={cursor_location_region}")
        print(f"function name={function_detail.function_name}")

        print(f"first line number={starting_line}")
        print(f"last line={last_line_number_in_file}")

        print(f"starting line={line}")
        print(f"starting region from line={starting_region_converted}")
        print(f"ending region={end_of_function_implementation_region}")

      self.replace_function(self.view, edit, start_of_function_definiton_region, end_of_function_implementation_region, function_name)
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

  def replace_function(self, view: sublime.View, edit: sublime.Edit, starting: sublime.Region, ending: sublime.Region, existing_name: str):
    window = view.window()
    if window is not None:
      def on_done_function(new_name: str):
        self.function_name_chosen(view, edit, starting, ending, existing_name, new_name)

      window.show_input_panel("Enter the name of the new function", existing_name, on_done=on_done_function, on_cancel=None, on_change=None)
    else:
      sublime.message_dialog("Could not find window for current view")

  def function_name_chosen(self, view: sublime.View, edit: sublime.Edit, starting: sublime.Region, ending: sublime.Region, existing_name: str, new_name: str):
    function_content = self.get_function_content(view, starting, ending)
    renamed_function = self.rename_function(original_function=function_content, existing_name=existing_name, new_name=new_name)
    margin = '\n\n' # make this configurable
    new_function = f'{margin}{renamed_function}{margin}'

    self.copy_function(view, edit, new_function, ending)


  def get_function_content(self, view: sublime.View, starting: sublime.Region, ending: sublime.Region) -> str:
    function_region = sublime.Region(starting.begin(), ending.end())
    print(f"body region: {function_region}")
    function_body = self.get_all_region_lines(view, function_region)
    print(f"body: {function_body}")
    return function_body

  def rename_function(self, original_function: str, existing_name: str, new_name: str) -> str:
    print(f'existing name: {existing_name}')
    function_def_replacement_reg: str = f'^{existing_name}(\\s*:)'
    function_impl_replacement_reg: str = f'^{existing_name}(\\s*([a-zA-Z0-9]+\\s*=))'
    first_group = r'\1'

    function_with_new_def_name = re.sub(function_def_replacement_reg, f'{new_name}{first_group}', original_function, count = 1, flags = re.MULTILINE)
    function_with_new_impl_name = re.sub(function_impl_replacement_reg, f'{new_name}{first_group}', function_with_new_def_name, count = 1, flags = re.MULTILINE)

    return function_with_new_impl_name

  def copy_function(self, view: sublime.View, edit: sublime.Edit, function_content: str, ending: sublime.Region):
    view.run_command('replace_function', { "region": [ending.begin(), ending.end()], "text": function_content })

  def get_last_line_number(self, view: sublime.View) -> int:
    region = sublime.Region(0, view.size())
    (row, _) = view.rowcol(region.end())
    return row + 1

  def find_top_of_function(self, view: sublime.View, starting_from: sublime.Region) -> FD.FunctionDetail:
    safe_guard = 0
    region = starting_from

    while safe_guard < 20: # make this configurable
      line = self.get_region_line(view, region)
      function_names = re.findall(ElmCopyCommand.function_def_reg, line)

      if len(function_names) != 0:
        # add a check for tuple with two elements
        return FD.FunctionDetail(function_names[0][0], region)
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

    while safe_guard < 20: # make this configurable
      line = self.get_region_line(view, region)
      print(f"line: {safe_guard} {line}, lets:{lets}")

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
        print(f"next_line_number: {safe_guard} {next_line_number}, lets:{lets}")

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

class ReplaceFunctionCommand(sublime_plugin.TextCommand):

  def run(self, edit: sublime.Edit, region: sublime.Region, text: str) -> None:
      if self and self.view:
        region = sublime.Region(*region)
        self.view.replace(edit, region, text)
