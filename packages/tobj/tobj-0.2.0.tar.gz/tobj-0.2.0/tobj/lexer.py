"""
Lexer for TOBJ
"""
from typing import List, Optional, Tuple
from tobj.errors import Position, LexerError

STAR: str = "STAR"           # *
ARROW: str = "ARROW"         # >
DASH: str = "DASH"           # -
IDENTIFIER: str = "IDENTIFIER"  # name, User.profile, etc.
STRING: str = "STRING"       # "quoted text"
NUMBER: str = "NUMBER"       # 42, 3.14
BOOLEAN: str = "BOOLEAN"     # true, false
NOTHING: str = "NOTHING"     # nothing
NEWLINE: str = "NEWLINE"     # \n
EOF: str = "EOF"             # end of file

WHITESPACE: Tuple[str, ...] = (
	' ', '\t', '\r', '\f', 
	'\xa0', '\v', '\u1680', 
	'\u2002', '\u2003', '\u2009', 
	'\u200a', '\u200b','\u3000', 
	'\u2007','\u2008','\u2028',
	'\u2029'
)

class Token:
	"""A single TinyObj token"""
	def __init__(self, type: str, value: Optional[str], pos_start: Position, pos_end: Position) -> None:
		self.type = type
		self.value = value
		self.pos_start = pos_start
		self.pos_end = pos_end

	def __repr__(self) -> str:
		return f"Token(type={self.type}, value={self.value!r}, {self.pos_start.ln}:{self.pos_start.col}-{self.pos_end.ln}:{self.pos_end.col})"


class Lexer:
	"""The TinyObj Lexer"""
	def __init__(self, text: str, filename: str = '<string>') -> None:
		self.text: str = text
		self.pos: Position = Position(0, 1, 1, filename, self.text)
		self.current_char: Optional[str] = self.text[0] if text else None
	
	def advance(self) -> None:
		"""Move to the next character"""
		self.pos.advance(self.current_char)
		self.current_char = self.peek(0)

	
	def peek(self, offset: int = 1) -> Optional[str]:
		"""Look ahead at the next character without advancing"""
		peek_pos: int = self.pos.idx + offset
		if peek_pos < len(self.text):
			return self.text[peek_pos]
		return None
	
	def skip_whitespace(self) -> None:
		"""Skip spaces and tabs (but NOT newlines!)"""
		while self.current_char is not None and self.current_char in WHITESPACE:
			self.advance()
	
	def skip_comment(self) -> None:
		"""Skip characters until the end of the line"""
		while self.current_char is not None and self.current_char != '\n':
			self.advance()
	
	def tokenize(self) -> List[Token]:
		tokens: List[Token] = []
		
		while self.current_char is not None:
			start_pos: Position = self.pos.copy()

			# skip whitespace
			if self.current_char in WHITESPACE:
				self.skip_whitespace()
				continue
			
			# 1. Handle # comments
			if self.current_char == '#':
				self.skip_comment()
				continue
			
			# 2. Handle // comments
			# check if current is '/' and the next one is also '/'
			if self.current_char == '/' and self.peek() == '/':
				self.skip_comment()
				continue

			if self.current_char == '.' and self.peek() == '.' and self.peek(2) == '.':
				# notice how i don't skip comment here - the ellipsis gets ignored
				# but the line isn't.
				continue

			# handle newlines
			if self.current_char == '\n':
				self.advance()
				pos_end = self.pos
				tokens.append(Token(NEWLINE, '\n', start_pos, pos_end))
			
			# handle single tokens by giving them a girlfriend
			elif self.current_char == '*':
				self.advance()
				pos_end = self.pos				
				tokens.append(Token(STAR, '*', start_pos, pos_end))
			
			elif self.current_char == '>':
				self.advance()
				pos_end = self.pos		
				tokens.append(Token(ARROW, '>', start_pos, pos_end))
			
			# handle numbers
			elif self.current_char.isdigit() or (self.current_char == '-' and self.peek() and (next_char := self.peek()) and next_char.isdigit()):
				number = ''

				# handle negatives
				if self.current_char == '-':
					number += '-'
					self.advance()
				
				# read them digits
				while self.current_char is not None and self.current_char.isdigit():
					number += self.current_char
					self.advance()
				
				# handle decimal dots for floating (i'm floating!)
				if self.current_char == '.' and self.peek() and next_char and next_char.isdigit():
					number += '.'
					self.advance()
					while self.current_char is not None and self.current_char.isdigit():
						number += self.current_char
						self.advance()
				
				tokens.append(Token(NUMBER, number, start_pos, self.pos))
			

			elif self.current_char == '-':
				
				self.advance()
				pos_end = self.pos				
				tokens.append(Token(DASH, '-', start_pos, pos_end))
			
			# handle strings
			elif self.current_char == '"':
				self.advance()
				
				string_value: List[str] = []

				while self.current_char is not None and self.current_char != '"':
					# is ts escape?
					if self.current_char == '\\':
						# oh boy it's escaping time
						self.advance()
						if self.current_char == 'n':
							string_value.append('\n')
						elif self.current_char == 't':
							string_value.append('\t')
						elif self.current_char == '"':
							string_value.append('"')
						elif self.current_char == '\\':
							string_value.append('\\')
						else: # unknown escape
							string_value.append(self.current_char)
						self.advance()
					else:
						string_value.append(self.current_char)
						self.advance()
				
				# oh boy errors!
				if self.current_char != '"':
					# raise SyntaxError(f"Unterminated string (you didn't close the string) at {start_line}:{start_column}")
					raise LexerError(start_pos, self.pos, "Unterminated string (unclosed string)")

				self.advance()
				tokens.append(Token(STRING, "".join(string_value), start_pos, self.pos))

			
			# handle identifiers and keywords (true, false, nothing)
			elif self.current_char.isalpha() or self.current_char in '_$':
				# save position for good errors (im looking at you C++)
	
				# we collect the tasty characters
				identifier = ''
				while self.current_char is not None and (
					self.current_char.isalnum() or
					self.current_char in '._$+'
				):
					identifier += self.current_char
					self.advance()
				
				# check if it's a keyword
				if identifier == 'true' or identifier == 'false':
					tokens.append(Token(BOOLEAN, identifier, start_pos, self.pos))
				elif identifier == 'nothing':
					tokens.append(Token(NOTHING, identifier, start_pos, self.pos))
				else:
					tokens.append(Token(IDENTIFIER, identifier, start_pos, self.pos))
			
			else:
				# lexer doesn't know what the hell this is
				# raise SyntaxError(f"Unexpected character '{self.current_char}' at {self.line}:{self.column}")
				bad_char_pos: Position = self.pos.copy()
				bad_char: str = self.current_char
				self.advance()
				raise LexerError(bad_char_pos, self.pos, f"Unexpected character '{bad_char}'")
		tokens.append(Token(EOF, None, self.pos, self.pos)) # We don't need the position of EOF.
		return tokens

def main():
	import pprint
	lexer = Lexer("*Temps >readings - -5 - 10 - -3.14")
	pprint.pprint(lexer.tokenize())

if __name__ == "__main__":
	main()