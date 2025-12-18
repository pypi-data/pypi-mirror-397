"""
TinyObj v0.1.0,
a tiny object format for freedom.
"""
from typing import Optional, Dict, Any, List
from tobj.interpreter import Interpreter
from tobj.parser import Parser
from tobj.lexer import Lexer

def loads(string_code: str, *, filename: str = "<string>") -> Optional[Dict[str, Any]]:
	"""Parse TOBJ from a string

	Args:
		string_code (str): TOBJ source code
		filename (str, optional): Name to show in error messages. Defaults to "<string>".

	Returns:
		Optional[Dict[str, Any]]: Parsed Python dict

	Raises:
		LexerError: An error while lexing
		ParserError: An error while parsing
		InterpreterError: An error while interpreting
	"""
	if string_code:
		return Interpreter(Parser(Lexer(string_code, filename).tokenize()).parse()).interpret()
	
	return None

def load(file) -> Optional[Dict[str, Any]]:
	"""Parse TinyObj from a file object

	Args:
		file: File-like object to read from

	Returns:
		Optional[Dict[str, Any]]: Parsed Python dict
	"""
	content = file.read()
	filename = getattr(file, 'name', '<file>')
	return loads(content, filename=filename)

def dumps(data: Dict[str, Any]) -> str:
	"""
	Converts a Python dictionary into a TinyObj string format using a single
	recursive function.
	"""
	output: List[str] = []

	def format_value(value: Any) -> str:
		"""Converts a Python value into its TinyObj string representation."""
		import json
		if isinstance(value, str):
			# Use json.dumps for safe string escaping (e.g., handles quotes)
			return json.dumps(value)
		elif isinstance(value, bool):
			return str(value).lower()
		elif value is None:
			return "nothing"
		elif isinstance(value, (int, float)):
			return str(value)
		return str(value)

	def serialize_recursive(current_dict: Dict, path_prefix: str) -> None:
		"""
		The main recursive worker function.
		"""
		for key, value in current_dict.items():
			current_path = f"{path_prefix}.{key}" if path_prefix else key

			if isinstance(value, dict) and value:
				if output:
					output.append("")
				output.append(f"*{current_path}")
				
				serialize_recursive(value, current_path)

			elif isinstance(value, list):
				output.append(f"> {key}")
				
				for item in value:
					formatted_item = format_value(item)
					output.append(f"- {formatted_item}")

			elif not isinstance(value, dict):
				formatted_value = format_value(value)
				output.append(f"> {key} {formatted_value}")
				

	serialize_recursive(data, path_prefix="")
	
	return "\n".join(output) + "\n"

def dump(data: Dict[str, Any], file) -> None:
	tobj_result = dumps(data)
	file.write(tobj_result)

def test_case(name: str, code: str) -> None:
	"""Run a single test case with error handling"""
	print(f"\n{'='*60}")
	print(f"TEST: {name}")
	print(f"{'='*60}")
	print("INPUT:")
	print(code)
	print("\n" + "-"*60)
	
	try:
		result = loads(string_code=code)
		print("RESULT:")
		import json
		print(json.dumps(result, indent=2))
		print("✅ PASSED")
	except Exception as e:
		print(f"❌ ERROR: {type(e).__name__}: {e}")

def test_case_file(name: str, code: str) -> None:
	"""Run a single test case with error handling from a file"""
	print(f"\n{'='*60}")
	print(f"TEST: {name}")
	print(f"{'='*60}")
	print("INPUT:")
	print(code)
	print("\n" + "-"*60)
	
	try:
		with open(code, 'r') as f:
			result = load(file=f)
		print("RESULT:")
		import json
		print(json.dumps(result, indent=2))
		print("✅ PASSED")
	except Exception as e:
		print(f"❌ ERROR: {type(e).__name__}: {e}")

def test_roundtrip():
    """Test serialization and deserialization"""
    print(f"\n{'='*60}")
    print(f"TEST: Round-trip (loads → dumps → loads)")
    print(f"{'='*60}")
    
    original = """
*User
> name Alice
> age 30
> active true

*User.profile
> bio "Hello World"
> score 9001

*User.tags
> favorites
- python
- rust
- C++
"""
    
    try:
        # Load original
        data1 = loads(original)
        print("Original data:")
        import json
        print(json.dumps(data1, indent=2))
        
        # Serialize back to TinyObj
        serialized = dumps(data1)
        print("\nSerialized TinyObj:")
        print(serialized)
        
        # Load again
        data2 = loads(serialized)
        print("Re-loaded data:")
        print(json.dumps(data2, indent=2))
        
        # Compare
        if data1 == data2:
            print("\n✅ PASSED - Data matches after round-trip!")
        else:
            print(f"\n❌ FAILED - Data mismatch!")
            print(f"Original: {data1}")
            print(f"After round-trip: {data2}")
    
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

def main():
	"""Run all edge case tests"""
	
	def test_error_formatting():
		"""Test that errors display correctly"""
		from tobj.errors import Position, LexerError
		
		text = ">name Alice"
		pos_start = Position(0, 1, 1, "<test>", text)
		pos_end = Position(4, 1, 5, "<test>", text)
		
		error = LexerError(pos_start, pos_end, "Test error")
		print(error)
		print("Error formatting works!")

	test_error_formatting()
	
	# Test 1: Property before object
	test_case("Property before any object", """
>name Alice
""")
	
	# Test 2: Empty object
	test_case("Empty object", """
*User
*Config
>version 1
""")
	
	# Test 3: Multiple top-level objects
	test_case("Multiple top-level objects", """
*User
>name Alice

*Device
>model "Phone"
""")
	
	# Test 4: Empty list
	test_case("Empty list (property with no value)", """
*User
>items
""")
	
	# Test 5: Nested object without parent
	test_case("Nested object without explicit parent", """
*User.profile.settings
>theme dark
""")
	
	# Test 6: Basic working example
	test_case("Basic working example", """
*User
>name Alice
>age 30
>tags
- python
- rust
""")
	
	# Test 7: One-liner list
	test_case("One-liner list", """
*Config
>values - a - b - c
""")
	
	# Test 8: Mixed types
	test_case("Mixed types", """
*Data
>string "hello"
>number 42
>float 3.14
>bool true
>"nothing" nothing
""")
	
	test_case("Simple object", """
*User
> name Alice
> age 30
""")
    
	test_case("Nested objects", """
*User.profile.settings
> theme dark
""")
    
	test_case("Lists", """
*Config
> items
- a
- b
- c
""")
    
	test_case("Mixed types", """
*Data
> string "hello"
> number 42
> float 3.14
> bool true
> nothing nothing
""")

	test_case('Mixed lists + one-liner' , "*Temps >readings - -5 - 10 - -3.14")

	test_case_file("Reading from file and dollar signs", "samples/names.tobj")

	test_roundtrip()

if __name__ == "__main__":
	main()