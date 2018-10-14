from enum import Enum


class TokenType(Enum):
    id: 0
    number: 1
    ST: 2
    String: 3
    Comment: 4
    KW: 5


specialsTokens = [
    "if",
    "while",
    "do",
    "for",
    "main",
    "return",
    "int",
    "float",
    "double",
    "char",
    "long",
    "void",
    "switch",
    "case",
    "enum",
    "new",
    "class",
    "default",
    "struct",
    "goto",
    "const",
    "union",
    "static",
    "try",
    "catch",
    "else",
    "break",
    "true",
    "false",
    "throw",
]
