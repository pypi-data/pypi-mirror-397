"""
TinyObj v0.2.1,
a tiny object format for freedom.
"""
from tobj.interpreter import Interpreter
from tobj.parser import Parser
from tobj.lexer import Lexer
from tobj.main import dump, dumps, load, loads

__all__ = [
    "Interpreter",
    "Parser",
    "Lexer",
    
	"dump", "dumps",
    "load", "loads",
]

__version__ = "0.2.1"
__author__ = "Razka Rizaldi"