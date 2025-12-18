"""
TinyObj's Custom Errors
"""

from typing import Optional

class Position:
	"""Tracks position in source code"""
	def __init__(self, idx: int, 
			  ln: int, col: int, 
			  filename: str, 
			  text: str) -> None:
		self.idx: int = idx
		self.ln: int = ln
		self.col: int = col
		self.filename: str = filename
		self.text: str = text
		
	def advance(self, current_char: Optional[str] = None) -> 'Position': 
		"""Move position forward one character"""
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 1

		return self

	def copy(self) -> 'Position':
		copy_position = Position(self.idx, self.ln, self.col, self.filename, self.text)
		return copy_position
	
###########################################

# ERRORS

def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

##############################

class TinyObjError(Exception):
	"""Base error class for TinyObj"""
	def __init__(self, pos_start: Position, pos_end: Position, 
			  error_name: str, details: str) -> None:
		self.pos_start: Position = pos_start
		self.pos_end:	Position = pos_end
		self.error_name:str      = error_name
		self.details:	str	 	 = details

	def __str__(self) -> str:
		return (
			f"{self.error_name}: {self.details}\n"
			f"File {self.pos_start.filename}, line {self.pos_start.ln}\n"
			f"{string_with_arrows(self.pos_start.text, self.pos_start, self.pos_end)}" # ?
		)

class LexerError(TinyObjError):
	"""Lexer-specific errors"""
	def __init__(self, pos_start: Position, pos_end: Position, details: str) -> None:
		super().__init__(pos_start, pos_end, "LexerError", details)

class ParserError(TinyObjError):
	"""Parser-specific errors"""
	def __init__(self, pos_start: Position, pos_end: Position, details: str) -> None:
		super().__init__(pos_start, pos_end, "ParserError", details)

class InterpreterError(TinyObjError):
	"""Interpreter-specific errors"""
	def __init__(self, pos_start: Position, pos_end: Position, details: str) -> None:
		super().__init__(pos_start, pos_end, "InterpreterError", details)