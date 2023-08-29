import sublime, sublime_plugin
from typing import Optional, List, cast

from . import function_detail as FD
from . import settings_loader as SL
from . import elm_copy_setting as ECS
from . import renamer as R
from . import elm_copy_regex as REG

import re

class ElmCopyCommand(sublime_plugin.TextCommand):

  print("elm_copy command has loaded.")

  def run(self, edit: sublime.Edit) -> None:
    if self and self.view:
      self.log("elm_copy command is running")

      self.settings: ECS.ElmCopySetting = self.load_settings()
      self.debug(self.settings.debug, f'settings: {self.settings}')
      self.renamer = R.Renamer()
      self.regex = REG.ElmCopyRegex()

      cursor_location_region = self.view.sel()[0] # check if this is valid
      self.debug(self.settings.debug, f"starting cursor region={cursor_location_region}")

      last_line_number_in_file = self.get_last_line_number(self.view)
      self.debug(self.settings.debug, f"lines in the file={last_line_number_in_file}")

      function_detail = self.find_top_of_function(self.view, cursor_location_region)

      start_of_function_definiton_region = function_detail.function_region
      self.debug(self.settings.debug, f"function starting region={start_of_function_definiton_region}")

      function_name = function_detail.function_name
      self.debug(self.settings.debug, f"function name={function_detail.function_name}")

      starting_line = self.region_to_row(self.view, cursor_location_region)
      self.debug(self.settings.debug, f"line number at cursor={starting_line}")

      line = self.get_region_line(self.view, cursor_location_region)
      self.debug(self.settings.debug, f"cursor line contents={line}")

      # We need to search for the bottom of the function, starting from the very top of the definition,
      # not, where the cursor is. This is because we want to handle let/in pairs, which can't be
      # tracked from the middle of the function
      end_of_function_implementation_region = self.find_bottom_of_function(self.view, start_of_function_definiton_region, last_line_number_in_file)
      self.debug(self.settings.debug, f"function ending region={end_of_function_implementation_region}")

      self.replace_function(self.view, start_of_function_definiton_region, end_of_function_implementation_region, function_name)
    else:
      sublime.message_dialog("Could not find self")

  def load_settings(self) -> ECS.ElmCopySetting:
    loaded_settings: sublime.Settings = sublime.load_settings('ElmCopy.sublime-settings')
    return SL.SettingsLoader(loaded_settings).load()

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

  def replace_function(self, view: sublime.View, starting: sublime.Region, ending: sublime.Region, existing_name: str):
    window = view.window()
    if window is not None:
      def on_done_function(new_name: str):
        self.function_name_chosen(view, starting, ending, existing_name, new_name)

      window.show_input_panel("Enter the name of the new function", existing_name, on_done=on_done_function, on_cancel=None, on_change=None)
    else:
      sublime.message_dialog("Could not find window for current view")

  def function_name_chosen(self, view: sublime.View, starting: sublime.Region, ending: sublime.Region, existing_name: str, new_name: str):
    function_content = self.get_function_content(view, starting, ending)
    renamed_function = self.rename_function(original_function=function_content, existing_name=existing_name, new_name=new_name)
    margin = '\n\n' # make this configurable
    new_function = f'{margin}{renamed_function}{margin}'

    self.copy_function(view, new_function, ending)


  def get_function_content(self, view: sublime.View, starting: sublime.Region, ending: sublime.Region) -> str:
    function_region = sublime.Region(starting.begin(), ending.end())
    self.debug(self.settings.debug, f"body region: {function_region}")
    function_body = self.get_all_region_lines(view, function_region)
    self.debug(self.settings.debug, f"body: {function_body}")
    return function_body

  def rename_function(self, original_function: str, existing_name: str, new_name: str) -> str:
    self.debug(self.settings.debug, f'renaming existing function name: {existing_name}')
    renamed = self.renamer.rename(original_function, existing_name, new_name)
    self.debug(self.settings.debug, f'renamed function: {renamed}')
    return renamed

  def copy_function(self, view: sublime.View, function_content: str, ending: sublime.Region):
    view.run_command('replace_function', { "region": [ending.begin(), ending.end()], "text": function_content })

  def get_last_line_number(self, view: sublime.View) -> int:
    region = sublime.Region(0, view.size())
    (row, _) = view.rowcol(region.end())
    return row + 1

  def find_top_of_function(self, view: sublime.View, starting_from: sublime.Region) -> FD.FunctionDetail:
    safe_guard = 0
    region = starting_from
    max_lines_to_consider = self.settings.max_function_length

    while safe_guard <= max_lines_to_consider:
      line = self.get_region_line(view, region)
      function_names = re.findall(self.regex.function_def_reg, line)

      if len(function_names) != 0:
        # add a check for tuple with two elements
        return FD.FunctionDetail(function_names[0][0], region)
      else:
        line_number: int = self.region_to_row(view, region)
        prev_line_number: int = line_number - 1

        if prev_line_number < 0:
          error = "Exceeded beginning of file looking for the start of the function"
          sublime.message_dialog(error)
          raise Exception(error);

        region = self.row_to_region(view, prev_line_number)
        safe_guard += 1

    return cast(FD.FunctionDetail, self.failWithSafeGuardError(max_lines_to_consider))

  def find_bottom_of_function(self, view: sublime.View, starting_from: sublime.Region, last_line: int) -> sublime.Region:
    safe_guard = 0
    lets = 0
    region = starting_from
    max_lines_to_consider = self.settings.max_function_length

    current_line_number: int = 0

    while safe_guard <= max_lines_to_consider:
      line = self.get_region_line(view, region)
      current_line_number = self.region_to_row(view, region)
      self.debug(self.settings.debug, f"iteration: {safe_guard} - line:{current_line_number} - [{line}], lets:{lets}")

      if len(line) == 0 and lets == 0:
        return region
      else:
        if re.match(self.regex.let_statement_reg, line) is not None:
          # check for let, increment if found
          lets += 1
        elif re.match(self.regex.in_statement_reg, line) is not None:
          # check for in, decrement lets if found
          lets -= 1

        next_line_number: int = current_line_number + 1
        self.debug(self.settings.debug, f"iteration: {safe_guard} - next line number:{next_line_number}, lets:{lets}")

        if next_line_number > last_line:
          return cast(sublime.Region, self.failOutOfBoundsError(last_line))

        # check for jumping over the last line of the file
        region = self.row_to_region(view, next_line_number)

        safe_guard +=1

    return cast(sublime.Region, self.failWithSafeGuardError(max_lines_to_consider))

  def failWithSafeGuardError(self, max_lines_to_consider: int) -> None:
    error = f"safe_guard exceeded {max_lines_to_consider} lines.\nTo support longer functions update the `max_function_length` setting to a value > {max_lines_to_consider}"
    sublime.message_dialog(error)
    raise Exception(error)

  def failOutOfBoundsError(self, lines_in_file: int) -> None:
    error = f"File length exceeded {lines_in_file} lines."
    sublime.message_dialog(error)
    raise Exception(error)

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

  def log(self, message: str):
    print(f'[ElmCopy] - {message}')

  def debug(self, debug: bool, message: str):
    if debug:
      print(f'[ElmCopy][DEBUG] - {message}')


class ReplaceFunctionCommand(sublime_plugin.TextCommand):

  def run(self, edit: sublime.Edit, region: sublime.Region, text: str) -> None:
      if self and self.view:
        region = sublime.Region(*region)
        self.view.replace(edit, region, text)
