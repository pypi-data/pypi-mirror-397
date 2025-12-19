"""
TinyObj v0.2.2,
a tiny object format for freedom.

This module provides the public API for the TinyObj format, including functions
for deserialization (`loads`, `load`) and serialization (`dumps`, `dump`).
"""
from . import dumps, load, loads

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
	"""Test serialization and deserialization integrity"""
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