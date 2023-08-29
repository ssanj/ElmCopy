class ElmCopyRegex:
  function_def_reg: str = r'^([a-z][a-z|A-Z|0-9]*)\s*:'
  let_statement_reg = r'^\s+let(\s*$|\s+[A-Z|a-z|0-9]+)'
  in_statement_reg = r'^\s+in(\s*$|\s+[A-Z|a-z|0-9]+)'
