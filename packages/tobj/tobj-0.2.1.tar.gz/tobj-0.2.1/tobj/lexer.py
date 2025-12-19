"""
Lexer for TOBJ

This module contains the Lexer responsible for converting TinyObj source code 
into a sequence of tokens.
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
    """
    A single TinyObj token, representing a meaningful unit in the source code.

    :param type: The token type (e.g., STAR, NUMBER, IDENTIFIER).
    :type type: str
    :param value: The literal value of the token, if applicable.
    :type value: Optional[str]
    :param pos_start: The starting position of the token in the source.
    :type pos_start: Position
    :param pos_end: The position immediately after the last character of the token.
    :type pos_end: Position
    """
    def __init__(self, type: str, value: Optional[str], pos_start: Position, pos_end: Position) -> None:
        """
        Initializes a Token object.

        :param type: The token type.
        :type type: str
        :param value: The token's value.
        :type value: Optional[str]
        :param pos_start: The starting position.
        :type pos_start: Position
        :param pos_end: The ending position.
        :type pos_end: Position
        """
        self.type = type
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self) -> str:
        """
        Returns a string representation of the token for debugging.
        """
        return f"Token(type={self.type}, value={self.value!r}, {self.pos_start.ln}:{self.pos_start.col}-{self.pos_end.ln}:{self.pos_end.col})"


class Lexer:
    """
    The TinyObj Lexer (scanner).

    It takes raw TinyObj text and converts it into a list of Token objects.

    :param text: The full source code text.
    :type text: str
    :param filename: The name of the source file. Defaults to '<string>'.
    :type filename: str
    :ivar pos: The current position in the source text.
    :vartype pos: Position
    :ivar current_char: The character at the current position, or None if EOF.
    :vartype current_char: Optional[str]
    """
    def __init__(self, text: str, filename: str = '<string>') -> None:
        """
        Initializes the Lexer.

        :param text: The source code to tokenize.
        :type text: str
        :param filename: The name of the source file. Defaults to '<string>'.
        :type filename: str
        """
        self.text: str = text
        self.pos: Position = Position(0, 1, 1, filename, self.text)
        self.current_char: Optional[str] = self.text[0] if text else None
    
    def advance(self) -> None:
        """
        Moves the lexer's position to the next character and updates `current_char`.
        """
        self.pos.advance(self.current_char)
        self.current_char = self.peek(0)

    
    def peek(self, offset: int = 1) -> Optional[str]:
        """
        Looks ahead at a character without advancing the position.

        :param offset: How many characters to look ahead. Defaults to 1.
        :type offset: int
        :return: The character at the peeked position, or None if past EOF.
        :rtype: Optional[str]
        """
        peek_pos: int = self.pos.idx + offset
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None
    
    def skip_whitespace(self) -> None:
        """
        Skips all standard horizontal whitespace characters (but NOT newlines!).
        """
        while self.current_char is not None and self.current_char in WHITESPACE:
            self.advance()
    
    def skip_comment(self) -> None:
        """
        Skips characters from the current position until a newline character or EOF.
        """
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
    
    def tokenize(self) -> List[Token]:
        """
        The main tokenization loop. Reads the source code and produces a list of Tokens.

        :return: A list of all tokens found in the source code, ending with an EOF token.
        :rtype: List[Token]
        :raises LexerError: If an unterminated string is found or an unexpected character is encountered.
        """
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
                pos_end = self.pos.copy()
                tokens.append(Token(NEWLINE, '\n', start_pos, pos_end))
            
            # handle single tokens by giving them a girlfriend
            elif self.current_char == '*':
                self.advance()
                pos_end = self.pos.copy()              
                tokens.append(Token(STAR, '*', start_pos, pos_end))
            
            elif self.current_char == '>':
                self.advance()
                pos_end = self.pos.copy()      
                tokens.append(Token(ARROW, '>', start_pos, pos_end))
            
            # handle numbers
            elif self.current_char.isdigit() or (self.current_char == '-' and self.peek() is not None and (next_char := self.peek()) and next_char.isdigit()):
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
                if self.current_char == '.' and self.peek() is not None and (next_char := self.peek()) and next_char.isdigit():
                    number += '.'
                    self.advance()
                    while self.current_char is not None and self.current_char.isdigit():
                        number += self.current_char
                        self.advance()
                
                tokens.append(Token(NUMBER, number, start_pos, self.pos.copy()))
            

            elif self.current_char == '-':
                
                self.advance()
                pos_end = self.pos.copy()              
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
                tokens.append(Token(STRING, "".join(string_value), start_pos, self.pos.copy()))

            
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
                    tokens.append(Token(BOOLEAN, identifier, start_pos, self.pos.copy()))
                elif identifier == 'nothing':
                    tokens.append(Token(NOTHING, identifier, start_pos, self.pos.copy()))
                else:
                    tokens.append(Token(IDENTIFIER, identifier, start_pos, self.pos.copy()))
            
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
    """
    Example usage of the Lexer.
    """
    import pprint
    lexer = Lexer("*Temps >readings - -5 - 10 - -3.14")
    pprint.pprint(lexer.tokenize())

if __name__ == "__main__":
    main()