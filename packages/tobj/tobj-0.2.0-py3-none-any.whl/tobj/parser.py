"""
The TinyObj Parser
"""

# -------------------
# Errors
# -------------------

from tobj.errors import Position, ParserError

# -------------------
# Nodes
# -------------------

class ASTNode:
	"""Base class for all AST nodes"""
	def __init__(self, pos_start: Position, pos_end: Position):
		self.pos_start = pos_start
		self.pos_end = pos_end

class ObjectNode(ASTNode):
	"""Represents an object declaration: *ObjectName"""
	def __init__(self, path: str, pos_start: Position, pos_end: Position):
		super().__init__(pos_start, pos_end)
		self.path = path  # "User" or "User.profile.settings"
	
	def __repr__(self) -> str:
		return f"ObjectNode({self.path!r})"

class PropertyNode(ASTNode):
	"""Represents a property assignment: >key value"""
	def __init__(self, key: str, value, pos_start: Position, pos_end: Position):
		super().__init__(pos_start, pos_end)
		self.key = key      # "name" or "User.name"
		self.value = value  # Python value
	
	def __repr__(self) -> str:
		return f"PropertyNode({self.key!r}, {self.value!r})"

# -----------------
# Parser
# -----------------

from typing import List, Optional, Tuple
from tobj.lexer import Token, STAR, ARROW, DASH, IDENTIFIER, STRING, NUMBER, BOOLEAN, NOTHING, NEWLINE, EOF

class Parser:
	"""The TinyObj Parser"""
	def __init__(self, tokens: List[Token]):
		self.tokens: List[Token] = tokens
		self.pos: int = 0
		self.current_token: Optional[Token] = self.tokens[0] if tokens else None
	
	def advance(self) -> None:
		"""Move to next token"""
		self.pos += 1
		self.current_token = self.peek(0)
	
	def peek(self, offset: int = 1) -> Optional[Token]:
		"""Look ahead at future tokens"""
		peek_pos: int = self.pos + offset
		if peek_pos < len(self.tokens):
			return self.tokens[peek_pos]
		return None
	
	def expect(self, token_type: str) -> Token:
		"""Consume a token of expected type, or raise error"""
		if self.current_token is None:
			raise ParserError(
				self.tokens[-1].pos_start, 
				self.tokens[-1].pos_end,
				f"Expected {token_type}, but reached EOF (end of file)"
			)

		if self.current_token.type == token_type:
			token: Token = self.current_token
			self.advance()
			return token
		else:
			raise ParserError(
				self.current_token.pos_start,
				self.current_token.pos_end,
				f"Expected {token_type}, but got {self.current_token.type} "
			)
	
	def skip_newlines(self) -> None:
		"""Skip any NEWLINE tokens"""
		while self.current_token is not None and self.current_token.type == NEWLINE:
			self.advance()
	
	def token_to_value(self, token: Token):
		"""Convert a token to its Python value"""
		if token.type == STRING:
			return token.value
		elif token.type == NUMBER and token.value:
			if '.' in token.value:
				return float(token.value)
			else:
				return int(token.value)
		elif token.type == BOOLEAN:
			return token.value == 'true'
		elif token.type == NOTHING:
			return None
		elif token.type == IDENTIFIER:
			return token.value
		else:
			raise ParserError(
				token.pos_start,
				token.pos_end,
				f"Unexpected value token: {token.type}"
			)

	def parse_object(self) -> ObjectNode:
		"""Parse object declaration: *ObjectName"""
		star_tok: Token = self.expect('STAR')
		name_tok: Token = self.expect('IDENTIFIER')

		if name_tok.value is None: # to chill mypy out
			raise ParserError(star_tok.pos_start, star_tok.pos_end,
					 f"An unexpected error has occured.")

		return ObjectNode(
			path=name_tok.value,
			pos_start=star_tok.pos_start,
			pos_end=name_tok.pos_end
		)

	def parse_list_items(self) -> Tuple[List, Position]:
		"""Parse list items (handles both one-line and multi-line)"""
		items: List = []
		list_end_position: Position

		if self.current_token is None:
			raise ParserError(
				self.tokens[-1].pos_start,
				self.tokens[-1].pos_end,
				f"Expected DASH, but reached EOF (end of file)"
			)
		
		while self.current_token.type == DASH:
			self.expect(DASH)  # CONSUME the dash
				
			# Read the value
			value_tok: Token = self.current_token
			self.advance()
			value = self.token_to_value(value_tok)
			items.append(value)
			
			list_end_position = value_tok.pos_end

			if self.current_token.type == NEWLINE:
				self.skip_newlines()
		
		return items, list_end_position

	def parse_property(self) -> PropertyNode:
		arrow_tok: Token = self.expect(ARROW)

		# mypy pleaser
		if self.current_token is None:
			raise ParserError(
				arrow_tok.pos_start,
				arrow_tok.pos_end,
				f"An unexpected error has occured."
			)

		if self.current_token.type in (BOOLEAN, NOTHING):
			raise ParserError(
				self.current_token.pos_start,
				self.current_token.pos_end,
				f"Cannot use keyword '{self.current_token.value}' as property key. "
				f"Use quotes if you want a literal key: >\"{self.current_token.value}\" "
			)

		key_tok: Optional[Token] = None
		if self.current_token.type == IDENTIFIER:
			key_tok = self.expect(IDENTIFIER)
		elif self.current_token.type == STRING:
			key_tok = self.expect(STRING)
		else:
			raise ParserError(
				self.current_token.pos_start,
				self.current_token.pos_end,
				f"Expected property key (identifier or string), got {self.current_token.type} "
			)

		# mypy pleaser
		if key_tok.value is None:
			raise ParserError(
				self.current_token.pos_start,
				self.current_token.pos_end,
				f"Expected property key (identifier or string), got {self.current_token.type} "
			)
		
		# what's next? come at me!
		if self.current_token.type == DASH:
			items, list_end_pos = self.parse_list_items()
			return PropertyNode(
				key_tok.value,
				items,
				arrow_tok.pos_start, 
				list_end_pos
			)
		
		elif self.current_token.type == NEWLINE:
			# might be multi-line list starting on next line
			self.skip_newlines()
			
			if self.current_token.type == DASH:
				items, list_end_pos = self.parse_list_items()
				return PropertyNode(
					key_tok.value,
					items,
					arrow_tok.pos_start, 
					list_end_pos
				)
			else:
				return PropertyNode(
					key_tok.value,
					None,
					arrow_tok.pos_start, 
					key_tok.pos_end
				)
		
		else:
			# Simple property with value
			value_tok: Token = self.current_token
			self.advance()
			value = self.token_to_value(value_tok)
			if key_tok.value is None:
				raise ParserError(
					arrow_tok.pos_start,
					arrow_tok.pos_end,
					f"An unexpected error has occured."
				)
			return PropertyNode(key_tok.value, value, arrow_tok.pos_start, value_tok.pos_end)

	def parse(self) -> List[ASTNode]:
		"""Main parsing method"""
		nodes: List[ASTNode] = []
		
		while self.current_token is not None and self.current_token.type != EOF:
			self.skip_newlines()
			
			if self.current_token.type == STAR:
				node: ASTNode = self.parse_object()
				nodes.append(node)
			elif self.current_token.type == ARROW:
				node = self.parse_property()
				nodes.append(node)
			elif self.current_token.type == EOF:
				break
			else:
				raise ParserError(
					self.current_token.pos_start,
					self.current_token.pos_start,
					f"Unexpected token {self.current_token.type} "
				)
		
		return nodes

def main():
	from tobj.lexer import Lexer
	import pprint
	
	tobj_code = """
*User
>name Alice
>age 30
>tags
- python
- rust
- C++
"""
	
	# Lex it
	lexer = Lexer(tobj_code)
	tokens = lexer.tokenize()
	print("=== TOKENS ===")
	pprint.pprint(tokens)
	
	# Parse it
	parser = Parser(tokens)
	ast = parser.parse()
	print("\n=== AST ===")
	pprint.pprint(ast)

if __name__ == "__main__":
	main()