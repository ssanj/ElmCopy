import unittest

import elm_copy_regex as R
import re
class ElmCopyRegexTest(unittest.TestCase):

  def test_definition_on_single_line(self):
    line = "viewDaysWithZeroJobsLastWeek : Model -> List (Html Msg)"
    self.assert_function_definition(line, 'viewDaysWithZeroJobsLastWeek')

  def test_definition_on_single_line_with_braces(self):
    line = "makeJobDefinitionRows : (Int, Api.Stats.JobDefinition) -> Html Msg"
    self.assert_function_definition(line, 'makeJobDefinitionRows')

  def test_definition_on_single_line_with_curly(self):
    line = "myCoolFunction : { baseApiUrl : String, onResponse : ApplyResult (List (Html msg)) ( Metadata, (List Date) ) -> msg } -> Effect msg"
    self.assert_function_definition(line, 'myCoolFunction')

  def test_definition_on_multiple_lines(self):
    line = "getDaysWithZeroJobsLastWeek :"
    self.assert_function_definition(line, 'getDaysWithZeroJobsLastWeek')

  def assert_function_definition(self, line: str, expected_result: str) -> None:
    regex: str = R.ElmCopyRegex().function_def_reg
    result = re.findall(regex, line)
    if len(result) != 0:
      # print(f"result========================> {result}")
      self.assertEqual(result[0], expected_result)
    else:
      self.fail(f"Expected result to be have at least one element and at least one tuple in that element. Got: {result}")

if __name__ == '__main__':
  unittest.main()
