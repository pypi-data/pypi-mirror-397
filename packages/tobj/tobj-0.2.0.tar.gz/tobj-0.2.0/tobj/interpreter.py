"""
The TinyObj Interpreter
"""

from typing import Dict, Any, List, Optional
from tobj.errors import InterpreterError
from tobj.parser import ASTNode, ObjectNode, PropertyNode

class Interpreter:
	"""Converts AST to Python dicts/lists"""
	
	def __init__(self, ast: List[ASTNode]) -> None:
		self.ast: List[ASTNode] = ast
		self.root: Dict[str, Any] = {}
		self.current_object_path: Optional[str] = None
	
	def interpret(self) -> Dict[str, Any]:
		"""Main method - returns the final dict"""
		for node in self.ast:
			if isinstance(node, ObjectNode):
				self.handle_object(node)
			elif isinstance(node, PropertyNode):
				self.handle_property(node)
		
		return self.root
	
	def handle_object(self, node: ObjectNode) -> None:
		"""Handle *ObjectName"""
		self.current_object_path = node.path
		
		parts: List[str] = node.path.split('.')
		
		current: Dict = self.root
		for part in parts:
			if not part in current:
				current[part] = {}
			current = current[part]
	
	def handle_property(self, node: PropertyNode) -> None:
		"""Handle >key value"""
		
		if self.current_object_path is None:
			raise InterpreterError(
				node.pos_start,
				node.pos_end,
				"Property without object context"
			)
		
		parts: List[str] = self.current_object_path.split('.')
		current: Dict = self.root
		for part in parts:
			current = current[part]
		
		current[node.key] = node.value

def main():
	from tobj.lexer import Lexer
	from tobj.parser import Parser
	from tobj.interpreter import Interpreter
	import pprint
	import json
	
	tobj_code = """
*User
>name Alice
>age 30
>active true
>pet nothing

*User.profile
>bio "Hello World"
>score 9001

*User.tags
>favorites
- python
- rust
- C++
"""
	
	print("=== INPUT ===")
	print(tobj_code)
	
	# Lex
	lexer = Lexer(tobj_code)
	tokens = lexer.tokenize()
	
	# Parse
	parser = Parser(tokens)
	ast = parser.parse()
	
	print("\n=== AST ===")
	pprint.pprint(ast)
	
	# Interpret
	interpreter = Interpreter(ast)
	result = interpreter.interpret()
	
	print("\n=== RESULT (Python dict) ===")
	pprint.pprint(result)
	
	print("\n=== RESULT (JSON) ===")
	print(json.dumps(result, indent=2))

	test1 = ">name Alice"
	

if __name__ == "__main__":
	main()