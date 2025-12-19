"""
TinyObj's Custom Errors
"""

from typing import Optional


class Position:
    """
    Tracks position in source code.

    :param idx: Current index in the source text.
    :type idx: int
    :param ln: Current line number (1-indexed).
    :type ln: int
    :param col: Current column number (1-indexed).
    :type col: int
    :param filename: Name of the source file.
    :type filename: str
    :param text: The full source text.
    :type text: str
    """
    def __init__(self, idx: int, ln: int, col: int, filename: str, text: str) -> None:
        """
        Initializes a Position object.

        :param idx: Starting index.
        :type idx: int
        :param ln: Starting line number.
        :type ln: int
        :param col: Starting column number.
        :type col: int
        :param filename: Source filename.
        :type filename: str
        :param text: Full source text.
        :type text: str
        """
        self.idx: int = idx
        self.ln: int = ln
        self.col: int = col
        self.filename: str = filename
        self.text: str = text

    def advance(self, current_char: Optional[str] = None) -> 'Position':
        """
        Move position forward one character.

        Updates the index, column, and line based on the current character.

        :param current_char: The character being advanced over.
        :type current_char: Optional[str]
        :return: The updated Position object (self).
        :rtype: Position
        """
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 1

        return self

    def copy(self) -> 'Position':
        """
        Creates a deep copy of the current Position object.

        :return: A new Position object with the same state.
        :rtype: Position
        """
        copy_position = Position(self.idx, self.ln, self.col, self.filename, self.text)
        return copy_position


def string_with_arrows(text, pos_start, pos_end):
    """
    Generates a string representation of the source code snippet
    highlighting the error range with carets (^).

    :param text: The full source code text.
    :type text: str
    :param pos_start: The starting position of the error.
    :type pos_start: Position
    :param pos_end: The ending position of the error.
    :type pos_end: Position
    :return: The highlighted source code snippet.
    :rtype: str
    """
    result = ''

    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line)

        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace('\t', '')


class TinyObjError(Exception):
    """
    Base error class for TinyObj.

    All custom errors in the TinyObj language should inherit from this class.

    :param pos_start: Starting position of the error in source code.
    :type pos_start: Position
    :param pos_end: Ending position of the error in source code.
    :type pos_end: Position
    :param error_name: The name of the error (e.g., "LexerError").
    :type error_name: str
    :param details: Specific details about the error.
    :type details: str
    """
    def __init__(self, pos_start: Position, pos_end: Position, error_name: str, details: str) -> None:
        """
        Initializes a TinyObjError.

        :param pos_start: Starting position of the error.
        :type pos_start: Position
        :param pos_end: Ending position of the error.
        :type pos_end: Position
        :param error_name: The name of the error.
        :type error_name: str
        :param details: Specific details about the error.
        :type details: str
        """
        self.pos_start: Position = pos_start
        self.pos_end: Position = pos_end
        self.error_name: str = error_name
        self.details: str = details

    def __str__(self) -> str:
        """
        Generates a user-friendly string representation of the error,
        including the error type, details, file, line number, and a highlighted
        snippet of the source code.

        :return: The formatted error message.
        :rtype: str
        """
        return (
            f"{self.error_name}: {self.details}\n"
            f"File {self.pos_start.filename}, line {self.pos_start.ln}\n"
            f"{string_with_arrows(self.pos_start.text, self.pos_start, self.pos_end)}"
        )


class LexerError(TinyObjError):
    """
    Lexer-specific errors, raised during the tokenization phase.

    :param pos_start: Starting position of the error.
    :type pos_start: Position
    :param pos_end: Ending position of the error.
    :type pos_end: Position
    :param details: Specific details about the lexing error.
    :type details: str
    """
    def __init__(self, pos_start: Position, pos_end: Position, details: str) -> None:
        super().__init__(pos_start, pos_end, "LexerError", details)


class ParserError(TinyObjError):
    """
    Parser-specific errors, raised during the syntax analysis (AST construction) phase.

    :param pos_start: Starting position of the error.
    :type pos_start: Position
    :param pos_end: Ending position of the error.
    :type pos_end: Position
    :param details: Specific details about the parsing error.
    :type details: str
    """
    def __init__(self, pos_start: Position, pos_end: Position, details: str) -> None:
        super().__init__(pos_start, pos_end, "ParserError", details)


class InterpreterError(TinyObjError):
    """
    Interpreter-specific errors, raised during the runtime execution phase.

    :param pos_start: Starting position of the error.
    :type pos_start: Position
    :param pos_end: Ending position of the error.
    :type pos_end: Position
    :param details: Specific details about the runtime error.
    :type details: str
    """
    def __init__(self, pos_start: Position, pos_end: Position, details: str) -> None:
        super().__init__(pos_start, pos_end, "InterpreterError", details)