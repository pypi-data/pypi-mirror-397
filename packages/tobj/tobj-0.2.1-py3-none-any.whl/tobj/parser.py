"""
The TinyObj Parser

This module defines the Abstract Syntax Tree (AST) nodes and the Parser class 
responsible for consuming tokens produced by the Lexer and constructing the AST.
"""

# -------------------
# Errors
# -------------------

from tobj.errors import Position, ParserError

# -------------------
# Nodes
# -------------------

class ASTNode:
    """
    Base class for all AST nodes.

    :param pos_start: The starting position in the source code.
    :type pos_start: Position
    :param pos_end: The ending position in the source code.
    :type pos_end: Position
    """
    def __init__(self, pos_start: Position, pos_end: Position):
        """
        Initializes the base ASTNode with positional information.

        :param pos_start: The starting position.
        :type pos_start: Position
        :param pos_end: The ending position.
        :type pos_end: Position
        """
        self.pos_start = pos_start
        self.pos_end = pos_end

class ObjectNode(ASTNode):
    """
    Represents an object declaration: *ObjectName.

    :param path: The dot-separated path of the object (e.g., "User" or "User.profile").
    :type path: str
    """
    def __init__(self, path: str, pos_start: Position, pos_end: Position):
        """
        Initializes an ObjectNode.

        :param path: The object path.
        :type path: str
        :param pos_start: The starting position of the '*' token.
        :type pos_start: Position
        :param pos_end: The ending position of the name token.
        :type pos_end: Position
        """
        super().__init__(pos_start, pos_end)
        self.path = path
    
    def __repr__(self) -> str:
        """Returns a string representation of the node for debugging."""
        return f"ObjectNode({self.path!r})"

class PropertyNode(ASTNode):
    """
    Represents a property assignment: >key value or >key followed by a list.

    :param key: The property key.
    :type key: str
    :param value: The Python value assigned to the property (str, int, float, bool, None, or List).
    :type value: Any
    """
    def __init__(self, key: str, value, pos_start: Position, pos_end: Position):
        """
        Initializes a PropertyNode.

        :param key: The property key.
        :type key: str
        :param value: The property value.
        :type value: Any
        :param pos_start: The starting position of the '>' token.
        :type pos_start: Position
        :param pos_end: The ending position of the value/list token.
        :type pos_end: Position
        """
        super().__init__(pos_start, pos_end)
        self.key = key
        self.value = value
    
    def __repr__(self) -> str:
        """Returns a string representation of the node for debugging."""
        return f"PropertyNode({self.key!r}, {self.value!r})"

# -----------------
# Parser
# -----------------

from typing import List, Optional, Tuple
from tobj.lexer import Token, STAR, ARROW, DASH, IDENTIFIER, STRING, NUMBER, BOOLEAN, NOTHING, NEWLINE, EOF

class Parser:
    """
    The TinyObj Parser.

    Consumes a stream of tokens and builds a list of ASTNode objects (ObjectNode and PropertyNode).

    :param tokens: The input list of tokens from the Lexer.
    :type tokens: List[Token]
    :ivar pos: The current index in the token list.
    :vartype pos: int
    :ivar current_token: The token currently being processed.
    :vartype current_token: Optional[Token]
    """
    def __init__(self, tokens: List[Token]):
        """
        Initializes the Parser.

        :param tokens: The list of tokens to parse.
        :type tokens: List[Token]
        """
        self.tokens: List[Token] = tokens
        self.pos: int = 0
        self.current_token: Optional[Token] = self.tokens[0] if tokens else None
    
    def advance(self) -> None:
        """Move the parser position to the next token."""
        self.pos += 1
        self.current_token = self.peek(0)
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """
        Look ahead at a future token without advancing the position.

        :param offset: Number of tokens to look ahead. Defaults to 1.
        :type offset: int
        :return: The token at the peeked position, or None if past EOF.
        :rtype: Optional[Token]
        """
        peek_pos: int = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: str) -> Token:
        """
        Consume a token of the expected type.

        If the current token matches the expected type, it is consumed and returned.
        Otherwise, a ParserError is raised.

        :param token_type: The expected type of the token.
        :type token_type: str
        :return: The consumed token.
        :rtype: Token
        :raises ParserError: If the token type does not match or if EOF is reached unexpectedly.
        """
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
        """Consume and discard all contiguous NEWLINE tokens."""
        while self.current_token is not None and self.current_token.type == NEWLINE:
            self.advance()
    
    def token_to_value(self, token: Token):
        """
        Convert a value token (STRING, NUMBER, BOOLEAN, NOTHING) into its corresponding Python value.

        :param token: The token to convert.
        :type token: Token
        :return: The Python representation of the token's value.
        :rtype: Any
        :raises ParserError: If the token type is not a valid value type.
        """
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
        """
        Parses an object declaration: *ObjectName.

        :return: The constructed AST node.
        :rtype: ObjectNode
        """
        star_tok: Token = self.expect('STAR')
        name_tok: Token = self.expect('IDENTIFIER')

        if name_tok.value is None:
            raise ParserError(star_tok.pos_start, star_tok.pos_end,
                     f"An unexpected error has occured.")

        return ObjectNode(
            path=name_tok.value,
            pos_start=star_tok.pos_start,
            pos_end=name_tok.pos_end
        )

    def parse_list_items(self) -> Tuple[List, Position]:
        """
        Parses list items following a property key (handles both one-line and multi-line lists).

        :return: A tuple containing the list of parsed values and the position of the last parsed item's end.
        :rtype: Tuple[List, Position]
        """
        items: List = []
        list_end_position: Position

        if self.current_token is None:
            raise ParserError(
                self.tokens[-1].pos_start,
                self.tokens[-1].pos_end,
                f"Expected DASH, but reached EOF (end of file)"
            )
        
        while self.current_token.type == DASH:
            self.expect(DASH)
                
            value_tok: Token = self.current_token
            self.advance()
            value = self.token_to_value(value_tok)
            items.append(value)
            
            list_end_position = value_tok.pos_end

            if self.current_token is not None and self.current_token.type == NEWLINE:
                self.skip_newlines()
            elif self.current_token is None or self.current_token.type == EOF:
                break
            elif self.current_token.type != DASH:
                break
        
        return items, list_end_position

    def parse_property(self) -> PropertyNode:
        """
        Parses a property assignment: >key value, >key, or >key followed by a list.

        :return: The constructed AST node.
        :rtype: PropertyNode
        :raises ParserError: If a keyword is used as a key, or an unexpected token is found.
        """
        arrow_tok: Token = self.expect(ARROW)

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

        if key_tok.value is None:
            raise ParserError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                f"Expected property key (identifier or string), got {self.current_token.type} "
            )
        
        # Check for list, simple value, or missing value
        if self.current_token is None:
            return PropertyNode(key_tok.value, None, arrow_tok.pos_start, key_tok.pos_end)
            
        elif self.current_token.type == DASH:
            # Case 1: List starting immediately on the same line (>key - item1 - item2)
            items, list_end_pos = self.parse_list_items()
            return PropertyNode(
                key_tok.value,
                items,
                arrow_tok.pos_start, 
                list_end_pos
            )
        
        elif self.current_token.type == NEWLINE:
            # Case 2: List starting on the next line or property with no value
            self.skip_newlines()
            
            if self.current_token is not None and self.current_token.type == DASH:
                # Sub-case: Multi-line list (>key \n - item1 \n - item2)
                items, list_end_pos = self.parse_list_items()
                return PropertyNode(
                    key_tok.value,
                    items,
                    arrow_tok.pos_start, 
                    list_end_pos
                )
            else:
                # Sub-case: Property with no value (>key \n)
                return PropertyNode(
                    key_tok.value,
                    None,
                    arrow_tok.pos_start, 
                    key_tok.pos_end
                )
        
        else:
            # Case 3: Simple property with value (>key value)
            value_tok: Token = self.current_token
            self.advance()
            value = self.token_to_value(value_tok)

            return PropertyNode(key_tok.value, value, arrow_tok.pos_start, value_tok.pos_end)

    def parse(self) -> List[ASTNode]:
        """
        Main parsing method.

        Iterates through the tokens and dispatches to object or property parsing methods.

        :return: The complete Abstract Syntax Tree, represented as a list of top-level nodes.
        :rtype: List[ASTNode]
        :raises ParserError: If an unexpected token is encountered outside of a valid structure.
        """
        nodes: List[ASTNode] = []
        
        while self.current_token is not None and self.current_token.type != EOF:
            self.skip_newlines()
            
            if self.current_token is None or self.current_token.type == EOF:
                break
                
            elif self.current_token.type == STAR:
                node: ASTNode = self.parse_object()
                nodes.append(node)
            elif self.current_token.type == ARROW:
                node = self.parse_property()
                nodes.append(node)
            else:
                raise ParserError(
                    self.current_token.pos_start,
                    self.current_token.pos_start,
                    f"Unexpected token {self.current_token.type} "
                )
        
        return nodes

def main():
    """Example usage of the Lexer and Parser to demonstrate AST construction."""
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