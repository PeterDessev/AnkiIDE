from typing import Union

def isSurrogate(char: Union[str, int]):
    if isinstance(char, str):
        return ord(char) >= "\uD800" and ord(char) <= "\uDFFF"
    else:
        return char >= "\uD800" and char <= "\uDFFF"

def isScalar(char:str):
    return not isSurrogate(char)

def isNonCharacter(char: Union[str, int]):
    charNum:int = None
    if isinstance(input, str):
        charNum:int = ord(char)
    else:
        charNum:int = char
    return ((charNum >= ord("\uFDD0") and charNum <= ord("\uFDEF")) or 
        (char in ["\uFFFE", "\uFFFF", "\u1FFFE", "\u1FFFF", "\u2FFFE", "\u2FFFF", 
            "\u3FFFE", "\u3FFFF", "\u4FFFE", "\u4FFFF", "\u5FFFE", "\u5FFFF", 
            "\u6FFFE", "\u6FFFF", "\u7FFFE", "\u7FFFF", "\u8FFFE", "\u8FFFF", 
            "\u9FFFE", "\u9FFFF", "\uAFFFE", "\uAFFFF", "\uBFFFE", "\uBFFFF", 
            "\uCFFFE", "\uCFFFF", "\uDFFFE", "\uDFFFF", "\uEFFFE", "\uEFFFF", 
            "\uFFFFE", "\uFFFFF", "\u10FFFE", "\u10FFFF"]))
        
def isASCII(char:str):
    return ord(char) >= ord("\u0000") and ord(char) <= ord("\u007F")

def isASCIITabOrNewline(char:str):
    char = ord(char)
    return char == ord("\u0009") or char == ord("\u000A") or char == ord("\u000D")

def isASCIIWhiteSpace(char:Union[str, int]):
    if isinstance(char, str):
        char = ord(char)
    return isASCIITabOrNewline(chr(char)) or char == ord("\u000C") or char == ord("\u0020")

def isC0Control(char:Union[str, int]):
    if isinstance(char, str):
        char = ord(char)
    return char >= ord("\u0000") and char <= ord("\u001F")

def isC0ControlOrSpace(char:str):
    return isC0Control(char) or ord(char) == ord("\u0020")

def isControl(char:Union[str, int]):
    if isinstance(char, str):
        char = ord(char)
    return isC0Control(char) or (char >= ord("\u007F") and char <= ord("\u009F"))

def isASCIIDigit(char:str):
    char = ord(char)
    return char >= ord("\u0030") and char <= ord("\u0039")

def isASCIIUpperHex(char:str):
    char = ord(char)
    return char >= ord("\u0041") and char <= ord("\u0046")

def isASCIILowerHex(char:str):
    char = ord(char)
    return char >= ord("\u0061") and char <= ord("\u0066")

def isASCIIHexDigit(char:str):
    return isASCIILowerHex(char) or isASCIIUpperHex(char)

def isASCIIUpperAlpha(char:str):
    char = ord(char)
    return char >= ord("\u0041") and char <= ord("\u005A")

def isASCIILowerAlpha(char:str):
    char = ord(char)
    return char >= ord("\u0061") and char <= ord("\u007A") 

def isASCIIAlpha(char:str):
    return isASCIILowerAlpha(char) or isASCIIUpperAlpha(char)

def isASCIIAlphaNumeric(char:str):
    return isASCIIDigit(char) or isASCIIAlpha(char)
