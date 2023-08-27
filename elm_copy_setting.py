class ElmCopySetting:
  def __init__(self, max_function_length: int, debug: bool, margin: int) -> None:
    self.max_function_length = max_function_length
    self.debug = debug
    self.margin = margin

  def __str__(self) -> str:
    return f"ElmCopySetting(max_function_length={self.max_function_length}, debug={self.debug}, margin={self.margin})"

  def __repr__(self) -> str:
    return self.__str__()
