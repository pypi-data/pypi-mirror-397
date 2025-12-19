"""
TinyObj v0.2.3,
a tiny object format for freedom.
"""
from typing import Any, Dict, Optional, List
from tobj.interpreter import Interpreter
from tobj.parser import Parser
from tobj.lexer import Lexer
from tobj.errors import LexerError, ParserError, InterpreterError

def loads(string_code: str, *, filename: str = "<string>") -> Optional[Dict[str, Any]]:
    """
    Parse TOBJ from a string.

    The primary entry point for deserializing TinyObj code. It chains the 
    Lexer, Parser, and Interpreter to convert the source string into a 
    Python dictionary.

    :param string_code: TOBJ source code.
    :type string_code: str
    :param filename: Name to show in error messages. Defaults to "<string>".
    :type filename: str
    :return: Parsed Python dict, or None if the input string is empty.
    :rtype: Optional[Dict[str, Any]]
    :raises LexerError: An error encountered during the tokenization phase.
    :raises ParserError: An error encountered during the AST construction phase.
    :raises InterpreterError: An error encountered during the final dict construction phase.
    """
    if string_code:
        tokens = Lexer(string_code, filename).tokenize()
        ast = Parser(tokens).parse()
        result = Interpreter(ast).interpret()
        return result
    
    return None


def load(file) -> Optional[Dict[str, Any]]:
    """
    Parse TinyObj from a file object.

    Reads the entire content of a file-like object and passes it to `loads`.

    :param file: File-like object to read from (must have a `.read()` method).
    :return: Parsed Python dict.
    :rtype: Optional[Dict[str, Any]]
    """
    content = file.read()
    filename = getattr(file, 'name', '<file>')
    return loads(content, filename=filename)

def dumps(data: Dict[str, Any]) -> str:
    """
    Converts a Python dictionary into a TinyObj string format.

    This function recursively serializes nested dictionaries and lists into 
    the object (*), property (>), and list (-) format of TinyObj.

    :param  The Python dictionary to serialize.
    :type  Dict[str, Any]
    :return: The resulting TinyObj source code string.
    :rtype: str
    """
    output: List[str] = []

    def format_value(value: Any) -> str:
        """Converts a Python value into its TinyObj string representation."""
        import json
        if isinstance(value, str):
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
        The main recursive worker function that traverses the dictionary structure.
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
    """
    Converts a Python dictionary to TinyObj format and writes it to a file object.

    :param  The Python dictionary to dump.
    :type data: Dict[str, Any]
    :param file: File-like object to write the resulting TinyObj string to.
    """
    tobj_result = dumps(data)
    file.write(tobj_result)


__all__ = [
    "Interpreter",
    "Parser",
    "Lexer",
    
	"dump", "dumps",
    "load", "loads",
    
    "LexerError", "ParserError", "InterpreterError",
]

__version__ = "0.2.2"
__author__ = "Razka Rizaldi"