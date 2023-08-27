# ElmCopy

[Sublime Text](https://www.sublimetext.com/) plugin that Copies an [Elm](https://elm-lang.org/) Function

![Copying a function with ElmCopy](copy-function.gif)

## Installation

- Open the command palette with `CMD + SHIT + P`
- Select `Package Control: Add Repository`
- Enter https://github.com/ssanj/ElmCopy for the repository
- Select `Package Control: Install Package`
- Choose ElmCopy


## Functionality

Copies an Elm function and gives it another name.

Place the cursor anywhere within an Elm function, and press `SUPER+HOME` or open the command palette with `CMD+SHIFT+P`
and choose `ElmCopy: function`. Enter the new function name when prompted. Once complete the original function will
be copied below itself with a new name.

### Settings

| Setting | Description | Default |
| ------  | ----------- | ------- |
| max_function_length | The length of the longest function to copy | 100 |
| debug | Turns on debug logging | false |
| margin | The lines above and below the copied function when pasted | 2 |

Default settings:

```
{
  // The longest function that can be parsed. Increase if longer functions are needed. This is a sanity check to ensure
  // the parser isn't going into an infinite loop if there's an error.
  "max_function_length": 100,

  // Whether to turn on debug logging
  "debug": false,

  // number of lines to use as a margin before and after the copied function.
  "margin": 2
}
```

