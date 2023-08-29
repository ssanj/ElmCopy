import unittest

import renamer as R
class RenamerTest(unittest.TestCase):

  def test_no_arguments(self):
    existing_function = r"""separator : Html Msg
separator =
  Html.node "HR2"
    []
    []"""

    expected_function = r"""hr3 : Html Msg
hr3 =
  Html.node "HR2"
    []
    []"""

    self.assert_rename(existing_name="separator", new_name="hr3", existing_function=existing_function, expected_function=expected_function)

  def test_single_arguments(self):
    existing_function = r"""defaultModel : Auth.User -> Model
defaultModel settings =
    { jobExecution = Nothing
    , jobDetail = Nothing
    , showJobDetail = False
    , searchByDate = Nothing
    , searchByLoading = False
    , searchByDateError = Nothing
    , jobExecutionByDate = Nothing
    , error = Nothing
    , baseApiUrl = settings.baseApiUrl
    , appVersion = settings.appVersion
    }"""

    expected_function = r"""anotherModel : Auth.User -> Model
anotherModel settings =
    { jobExecution = Nothing
    , jobDetail = Nothing
    , showJobDetail = False
    , searchByDate = Nothing
    , searchByLoading = False
    , searchByDateError = Nothing
    , jobExecutionByDate = Nothing
    , error = Nothing
    , baseApiUrl = settings.baseApiUrl
    , appVersion = settings.appVersion
    }"""

    self.assert_rename(existing_name="defaultModel", new_name="anotherModel", existing_function=existing_function, expected_function=expected_function)

  def test_multi_arguments(self):
    existing_function = r"""toLayout : Auth.User -> Model -> Layouts.Layout Msg
toLayout user model =
  Layouts.Menu
    { user = user
    }"""

    expected_function = r"""toLayout2 : Auth.User -> Model -> Layouts.Layout Msg
toLayout2 user model =
  Layouts.Menu
    { user = user
    }"""

    self.assert_rename(existing_name="toLayout", new_name="toLayout2", existing_function=existing_function, expected_function=expected_function)

  def test_multi_line_arguments(self):
    existing_function = r"""getJobsByDate :
  { baseApiUrl : String
  , date : String
  , onResponse : Result Http.Error JobExecution -> msg
  }
  -> Effect msg
getJobsByDate options =
  let
      url : String
      url = str3 options.baseApiUrl "/job/executions/by-date/" options.date

      cmd : Cmd msg
      cmd =
        Http.get
        { url = url
        , expect = Http.expectJson options.onResponse decodeJobExecution
        }
  in
  Effect.sendCmd cmd"""

    expected_function = r"""getJobsExtended :
  { baseApiUrl : String
  , date : String
  , onResponse : Result Http.Error JobExecution -> msg
  }
  -> Effect msg
getJobsExtended options =
  let
      url : String
      url = str3 options.baseApiUrl "/job/executions/by-date/" options.date

      cmd : Cmd msg
      cmd =
        Http.get
        { url = url
        , expect = Http.expectJson options.onResponse decodeJobExecution
        }
  in
  Effect.sendCmd cmd"""

    self.assert_rename(existing_name="getJobsByDate", new_name="getJobsExtended", existing_function=existing_function, expected_function=expected_function)

  def test_arguments_with_brackets(self):
    existing_function = r"""makeDateDefinitionRows : (Int, Api.Stats.Date) -> Html Msg
makeDateDefinitionRows (index, dateDefinition) =
    let
        makeRowHeader : Html Msg
        makeRowHeader =
            Html.th
                [ Attr.scope "row"
                ]
                [ Html.text (String.fromInt (index + 1)) ]


        makeRowColumns : List (Html Msg)
        makeRowColumns  =
            [ Html.td
                []
                [ Html.text dateDefinition.date ]
            ]
    in
      Html.tr
        []
        (makeRowHeader :: makeRowColumns)"""

    expected_function = r"""anotherSeparator : (Int, Api.Stats.Date) -> Html Msg
anotherSeparator (index, dateDefinition) =
    let
        makeRowHeader : Html Msg
        makeRowHeader =
            Html.th
                [ Attr.scope "row"
                ]
                [ Html.text (String.fromInt (index + 1)) ]


        makeRowColumns : List (Html Msg)
        makeRowColumns  =
            [ Html.td
                []
                [ Html.text dateDefinition.date ]
            ]
    in
      Html.tr
        []
        (makeRowHeader :: makeRowColumns)"""

    self.assert_rename(existing_name="makeDateDefinitionRows", new_name="anotherSeparator", existing_function=existing_function, expected_function=expected_function)


  def test_no_arguments_with_curlies(self):
    existing_function = r"""getJobsNotRunLastWeek : { baseApiUrl : String, onResponse : ApplyResult (List (Html msg)) ( Metadata, (List Date) ) -> msg } -> Effect msg
getJobsNotRunLastWeek { baseApiUrl, onResponse } =
  getStatsEndpoint {
    baseApiUrl = baseApiUrl
  , statsUrl =  "days-zero-jobs-last-week"
  , statsDecoder = getDatesDecoder
  , onResponse = onResponse
  }"""

    expected_function = r"""xyzJobs : { baseApiUrl : String, onResponse : ApplyResult (List (Html msg)) ( Metadata, (List Date) ) -> msg } -> Effect msg
xyzJobs { baseApiUrl, onResponse } =
  getStatsEndpoint {
    baseApiUrl = baseApiUrl
  , statsUrl =  "days-zero-jobs-last-week"
  , statsDecoder = getDatesDecoder
  , onResponse = onResponse
  }"""

    self.assert_rename(existing_name="getJobsNotRunLastWeek", new_name="xyzJobs", existing_function=existing_function, expected_function=expected_function)


  def assert_rename(self, existing_name: str, new_name: str, existing_function: str , expected_function: str) -> None:
    renamer = R.Renamer()
    new_function = renamer.rename(existing_function, existing_name, new_name)
    # print(f'new_function===========================> {new_function}')
    self.assertEqual(new_function, expected_function)

if __name__ == '__main__':
  unittest.main()
