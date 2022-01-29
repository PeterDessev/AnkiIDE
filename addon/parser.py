from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor, QTextDocument, QFont

from .tokens import *
from .codePoints import *
from .parseErrors import *
from .characterReferences import *
from . import default_config

defConfig = default_config.DEFAULT_CONFIG

def setStyle(fmt: QTextCharFormat, style: str) -> None:
    "Sets fmt to have all of the format charactaristics " \
        "listed out in style"

    if "italic" in style:
        fmt.setFontItalic(True)

    if "underline" in style:
        fmt.setFontUnderline(True)

    if "overline" in style:
        fmt.setFontOverline(True)

    if "strikeout" in style:
        fmt.setFontStrikeOut(True)

    if "bold" in style:
        fmt.setFontWeight(QFont.Bold)

class IDE():
    def __init__(self, config, document: QTextDocument) -> None:
        self.document = document
        self.config = config

        self.htmlStyles = 0
        self.htmlFormats = dict()

        self.jsStyles = 0
        self.jsFormats = dict()

        self.cssStyles = 0
        self.cssFormats = dict()

        self.isParsing = 0

        self.reset()

        # region Config Initialization
        try:
            self.htmlStyles = config["html"][config["profile"]
                                             ["html"]]["format"]
        except:
            print("AnkiIDE ERROR: Error accessing profile %s for html, check addon config"
                  % config["profile"]["html"])
            self.htmlStyles = defConfig["html"][config["profile"]
                                                ["html"]]["format"]

        try:
            self.jsStyles = config["javascript"][config["profile"]
                                                 ["javascript"]]["format"]
        except:
            print("AnkiIDE ERROR: Error accessing profile %s for javascript, check addon config"
                  % config["profile"]["javascript"])
            self.jsStyles = defConfig["javascript"][config["profile"]
                                                    ["javascript"]]["format"]

        try:
            self.cssStyles = config["css"][config["profile"]["css"]]["format"]
        except:
            print("AnkiIDE ERROR: Error accessing profile %s for css, check addon config"
                  % config["profile"]["css"])
            self.cssStyles = defConfig["css"][config["profile"]
                                              ["css"]]["format"]
        # endregion
        
        self.initializeFormats()

    def reset(self):       
        self.tokenState: tokenizationState = tokenizationState.dataState
        self.returnState = None

        self.lastEmitedStartTagToken: startTagToken = None

        self.parseIndex = 0
        self.nextChar = None
        self.insertionPoint = None
        self.reconsume = False
        self.token = None
        self.tempBuffer = None
        self.characterReferenceCode = None

        self.lineCount = 0
        self.lineIndex = 0

        self.originalInsertionMode = None
        self.reprocessToken = False
        self.openElementsStack = []
        self.templateInsertionModesStack = []
        self.activeFormattingElements = []
        self.headElement = None
        self.formElement = None
        self.characterTokenBuffer = []
        self.curScriptContents = ""

        self.raw: str = self.cleanText()
        self.inScript = False

    def initializeFormats(self) -> None:
        "Initialize all formats in the config into QTextCharFormat objects"

        # region HTML Format Initialization
        for formatName in self.htmlStyles:
            fmt = QTextCharFormat()
            try:
                fmt.setForeground(QColor(self.htmlStyles[formatName]["color"]))
            except:
                print("AnkiIDE Warning: Config profile \"%s\" is missing color attribute for \"%s\" format in HTML"
                      % (self.config["profile"]["html"], formatName))

            try:
                setStyle(fmt, self.htmlStyles[formatName]["style"])
            except:
                print("AnkiIDE Warning: Config profile \"%s\" is missing style attribute for \"%s\" format in HTML"
                      % (self.config["profile"]["html"], formatName))

            self.htmlFormats[formatName] = fmt
        # endregion

        # region JS Format Initialization
        for formatName in self.jsStyles:
            fmt = QTextCharFormat()
            try:
                fmt.setForeground(QColor(self.jsStyles[formatName]["color"]))
            except:
                print("AnkiIDE Warning: Config profile \"%s\" is missing color attribute for \"%s\" format in javascript"
                      % (self.config["profile"]["javascript"], formatName))

            try:
                setStyle(fmt, self.jsStyles[formatName]["style"])
            except:
                print("AnkiIDE Warning: Config profile \"%s\" is missing style attribute for \"%s\" format in javascript"
                      % (self.config["profile"]["javascript"], formatName))

            self.jsFormats[formatName] = fmt
        # endregion

        # region CSS Format Initialization
        for formatName in self.cssStyles:
            fmt = QTextCharFormat()
            try:
                fmt.setForeground(QColor(self.cssStyles[formatName]["color"]))
            except:
                print("AnkiIDE Warning: Config profile \"%s\" is missing color attribute for \"%s\" format in css"
                      % (self.config["profile"]["css"], formatName))

            try:
                setStyle(fmt, self.cssStyles[formatName]["style"])
            except:
                print("AnkiIDE Warning: Config profile \"%s\" is missing style attribute for \"%s\" format in css"
                      % (self.config["profile"]["css"], formatName))

            self.cssFormats[formatName] = fmt
        
    def cleanText(self) -> str:
        # Normalize New Lines
        plaintext = self.document.toPlainText()
        plaintext = plaintext.replace("\13\10", "\10")
        plaintext = plaintext.replace("\13", "")
        # self.document.setPlainText(plaintext)
        return plaintext

    def isAppropriateEndTagToken(self, token: endTagToken) -> bool:
        if(self.lastEmitedStartTagToken is None):
            return False
        if(not isinstance(token, endTagToken)):
            print("AnkiIDE ERROR: EndTagToken expected but was not recieved for isAppropriateEndTagToken")
            return False
        return token.tagName == self.lastEmitedStartTagToken.tagName

    def flushCharacterTokenBuffer(self) -> None:
        if self.characterTokenBuffer.__len__() > 0:
            for characterTokenInst in self.characterTokenBuffer: 
                print(characterTokenInst, end = "")
            print()

    # TODO: Implement error Handling
    def throwError(self, error: parseError, index: int, len: int) -> None:
        print("Encountered error %s in line %d, character %d with length %d" % (error.name, self.lineCount + 1, self.lineIndex + 1, len))          

    # TODO: Implement Script Parsing and Highlighting
    def parseScript(self):
        self.curScriptContents = ""

    # region Token Parsing
    def emitToken(self, token) -> None:
        # if not isinstance(token, characterToken):
        #     self.flushCharacterTokenBuffer()
        #     print(token)
        #     self.characterTokenBuffer = []
        # else:
        #     if self.inScript:
        #         self.curScriptContents += token.char
        #     self.characterTokenBuffer.append(token.char)

        if isinstance(token, startTagToken):
            self.highlightTag(token)
            self.lastEmitedStartTagToken = token

            if token.tagName == "script":
                self.inScript = True
                self.tokenState = tokenizationState.scriptDataState
            else:
                self.inScript = False

            if token.tagName == "plaintext":
                self.tokenState = tokenizationState.plainTextState
            elif token.tagName in ["textarea", "title"]:
                self.tokenState = tokenizationState.RCDataState
            elif token.tagName in ["noframes", "style", "noscript", "xmp"]:
                self.tokenState = tokenizationState.rawTextState

        elif isinstance(token, endTagToken):
            self.highlightTag(token)
            if token.tagName == "script":
                self.parseScript()

        elif isinstance(token, commentToken):
            self.highlightComment(token)

        elif isinstance(token, doctypeToken):
            self.highlightDoctype(token)
                
        return

    def emitCharacter(self, char: str, index: int):
        token: characterToken = characterToken()
        token.char = istr(char, index)
        self.emitToken(token)

    def flushCodePoints(self, buffer: str, index:int) -> None:
        for i in range(0, buffer.__len__()):
            self.emitCharacter(buffer[i], index - buffer.__len__() + i)

    def pushAttribute(self, token: tagToken):
        if not token.pushCurrentAttribute():
            beginIndex: int = token.currentAttribute.name.index
            errorLen: int = token.currentAttribute.name.text.__len__()
            self.throwError(parseError.duplicateAttribute, beginIndex, errorLen)

    def consumedAsPartOfAttribute(self) -> bool:
        return (self.returnState == tokenizationState.attributeValueDoubleQuotedState or
                self.returnState == tokenizationState.attributeValueSingleQuotedState or
                self.returnState == tokenizationState.attributeValueUnquotedState)

    class tokenizer():
        def parseDataState(self):
            if self.nextChar == "\u0026":  # Ampersand (&)
                self.returnState = tokenizationState.dataState
                self.tokenState = tokenizationState.characterReferenceState
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.tagOpenState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseRCDataState(self):
            if self.nextChar == "\u0026":  # Ampersand (&)
                self.returnState = tokenizationState.RCDataState
                self.tokenState = tokenizationState.characterReferenceState
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.RCDataLessThanSignState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseRawTextState(self):
            if self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.rawTextLessThanSignState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataState(self):
            if self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataLessThanSignState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parsePlainTextState(self):
            if self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emitCharacter(self.nextChar, self.token)

        def parseTagOpenState(self):
            if self.nextChar == "\u0021":  # Exclamation mark (!)
                self.tokenState = tokenizationState.markupDeclarationOpenState
            elif self.nextChar == "\u002F":  # Solidus (/)
                self.tokenState = tokenizationState.endTagOpenState
            elif isASCIIAlpha(self.nextChar):
                self.token: startTagToken = startTagToken()
                self.token.tagName = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.tagNameState
            elif self.nextChar == "\u003F":  # Question mark (?)
                self.throwError(parseError.unexpectedQuestionMarkInsteadOfTagName, self.parseIndex, 1)
                self.token: commentToken = commentToken()
                self.token.startIndex = self.parseIndex - 2
                self.token.data = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.bogusCommentState
            else:
                self.throwError(parseError.invalidFirstCharacterofTagName, self.parseIndex, 1)
                self.emitCharacter("\u003C", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.dataState

        def parseEndTagOpenState(self):
            if isASCIIAlpha(self.nextChar):
                self.token: endTagToken = endTagToken()
                self.token.tagName = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.tagNameState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingEndTagName, self.parseIndex, 1)
                self.tokenState = tokenizationState.dataState
            else:
                self.throwError(parseError.invalidFirstCharacterofTagName, self.parseIndex, 1)
                self.token: commentToken = commentToken()
                self.token.startIndex = self.parseIndex - 1
                self.token.data = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.bogusCommentState

        def parseTagNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Various white spaces
                self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u002F":  # Solidus (/)
                self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar.lower())
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token.tagName.text += "\uFFFD"
            else:
                self.token.tagName.append(self.nextChar)

        def parseRCDataLessThanSignState(self):
            if self.nextChar == "\u002F":  # Solidus (/)
                self.tempBuffer = ""
                self.tokenState = tokenizationState.RCDATAEndTagOpenState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.reconsume = True
                self.tokenState = tokenizationState.RCDataState

        def parseRCDATAEndTagOpenState(self):
            if isASCIIAlpha(self.nextChar):
                self.token: endTagToken = endTagToken()
                self.token.tagName = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.RCDATAEndTagNameState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)
                self.reconsume = True
                self.tokenState = tokenizationState.RCDataState

        def parseRCDATAEndTagNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Various white spaces
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u002F":  # Solidus (/)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.dataState
                    self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar.lower())
                self.tempBuffer += self.nextChar
            elif isASCIILowerAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar)
                self.tempBuffer += self.nextChar
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.RCDataState

            # Various white spaces, Greater than sign (>), and Solidus (/)
            if (self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u003E", "\u002F"] and
                    not self.isAppropriateEndTagToken(self.token)):
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.RCDataState

        def parseRawTextLessThanSignState(self):
            if self.nextChar == "\u002F":  # Solidus (/)
                self.tempBuffer = ""
                self.tokenState = tokenizationState.rawTextEndTagOpenState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.reconsume = True
                self.tokenState = tokenizationState.rawTextState

        def parseRawTextEndTagOpenState(self):
            if isASCIIAlpha(self.nextChar):
                self.token: endTagToken = endTagToken()
                self.token.tagName = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.rawTextEndTagNameState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                self.reconsume = True
                self.tokenState = tokenizationState.rawTextState

        def parseRawTextEndTagNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Various white spaces
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u002F":  # Solidus (/)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.dataState
                    self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar.lower())
                self.tempBuffer += self.nextChar
            elif isASCIILowerAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar)
                self.tempBuffer += self.nextChar
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.rawTextState

            # Various white spaces, Greater than sign (>), and Solidus (/)
            if (self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u003E", "\u002F"] and
                    not self.isAppropriateEndTagToken(self.token)):
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.rawTextState

        def parseScriptDataLessThanSignState(self):
            if self.nextChar == "\u002F":  # Solidus (/)
                self.tempBuffer = ""
                self.tokenState = tokenizationState.scriptDataEndTagOpenState
            elif self.nextChar == "\u0021":  # Exclamation mark (!)
                self.tokenState = tokenizationState.scriptDataEscapeStartState

                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u0021", self.parseIndex)  # Exclamation mark (!)
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataState

        def parseScriptDataEndTagOpenState(self):
            if isASCIIAlpha(self.nextChar):
                self.token: endTagToken = endTagToken()
                self.token.tagName = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEndTagNameState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataState

        def parseScriptDataEndTagNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Various white spaces
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u002F":  # Solidus (/)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.dataState
                    self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar.lower())
                self.tempBuffer += self.nextChar
            elif isASCIILowerAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar)
                self.tempBuffer += self.nextChar
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)
                self.emitToken(self.token)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataState

            # Various white spaces, Greater than sign (>), and Solidus (/)
            if (self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u003E", "\u002F"] and
                    not self.isAppropriateEndTagToken(self.token)):
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataState

        def parseScriptDataEscapeStartState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.scriptDataEscapeStartDashState
                self.emitCharacter(self.nextChar, self.parseIndex)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataState

        def parseScriptDataEscapeStartDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.scriptDataEscapeStartDashDashState
                self.emitCharacter(self.nextChar, self.parseIndex)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataState

        def parseScriptDataEscapedState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.scriptDataEscapedDashState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataEscapedLessThanSignState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emtiCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataEscapedDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.scriptDataEscapedDashDashState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataEscapedLessThanSignState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.tokenState = tokenizationState.scriptDataEscapedState
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.tokenState = tokenizationState.scriptDataEscapedState
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataEscapedDashDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataEscapedLessThanSignState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.scriptDataState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.tokenState = tokenizationState.scriptDataEscapedState
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.tokenState = tokenizationState.scriptDataEscapedState
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataEscapedLessThanSignState(self):
            if self.nextChar == "\u002F":  # Solidus (/)
                self.tempBuffer = ""
                self.tokenState = tokenizationState.scriptDataEscapedEndTagOpenState
            elif isASCIIAlpha(self.nextChar):
                self.tempBuffer = ""
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataDoubleEscapeStartState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEscapedState

        def parseScriptDataEscapedEndTagOpenState(self):
            if isASCIIAlpha(self.nextChar):
                self.token: endTagToken = endTagToken()
                self.token.tagName = istr("", self.parseIndex)
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEscapedState
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEscapedState

        def parseScriptDataEscapedEndTagNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Various white spaces
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u002F":  # Solidus (/)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                if self.isAppropriateEndTagToken(self.token):
                    self.tokenState = tokenizationState.dataState
                    self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar.lower())
                self.tempBuffer += self.nextChar
            elif isASCIILowerAlpha(self.nextChar):
                self.token.tagName.append(self.nextChar)
                self.tempBuffer += self.nextChar
            else:
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEscapedState

            # Various white spaces, Greater than sign (>), and Solidus (/)
            if (self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u003E", "\u002F"] and
                    not self.isAppropriateEndTagToken(self.token)):
                self.emitCharacter("\u003C", self.parseIndex)  # Less than sign (<)
                self.emitCharacter("\u002F", self.parseIndex)  # Solidus (/)

                for i in range(0, self.tempBuffer.__len__()):
                    self.emitCharacter(self.tempBuffer[i], self.parseIndex - (self.tempBuffer.__len__() - i))

                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEscapedState

        def parseScriptDataDoubleEscapeStartState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u002F", "\u003E"]:  # Various character
                if self.tempBuffer == "script":
                    self.tokenState = tokenizationState.scriptDataDoubleEscapedState
                else:
                    self.tokenState = tokenizationState.scriptDataEscapedState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif isASCIIUpperAlpha(self.nextChar):
                self.tempBuffer += self.nextChar.lower()
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif isASCIILowerAlpha(self.nextChar):
                self.tempBuffer += self.nextChar
                self.emitCharacter(self.nextChar, self.parseIndex)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataEscapedState

        def parseScriptDataDoubleEscapedState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedDashState
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedLessThanSignState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataDoubleEscapedDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedDashDashState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedLessThanSignState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedState
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.tokenState = tokenizationState.scriptDataDoubleEscapedState
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataDoubleEscapedDashDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedLessThanSignState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.scriptDataState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.tokenState = tokenizationState.scriptDataDoubleEscapedState
                self.emitCharacter("\uFFFD", self.parseIndex)
            else:
                self.tokenState = tokenizationState.scriptDataDoubleEscapedState
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseScriptDataDoubleEscapedLessThanSignState(self):
            if self.nextChar == "\u002F":  # Solidus (/)
                self.tempBuffer = ""
                self.tokenState = tokenizationState.scriptDataDoubleEscapeEndState
                self.emitCharacter(self.nextChar, self.parseIndex)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataDoubleEscapedState

        def parseScriptDataDoubleEscapeEndState(self):
            # Whitespace, Solidus (/), Greater than sign(>)
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u002F", "\u003E"]:
                if self.tempBuffer == "script":
                    self.tokenState = tokenizationState.scriptDataEscapedState
                else:
                    self.tokenState = tokenizationState.scriptDataDoubleEscapedState
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif isASCIIUpperAlpha(self.nextChar):
                self.tempBuffer += self.nextChar.lower()
                self.emitCharacter(self.nextChar, self.parseIndex)
            elif isASCIILowerAlpha(self.nextChar):
                self.tempBuffer += self.nextChar
                self.emitCharacter(self.nextChar, self.parseIndex)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.scriptDataDoubleEscapedState

        def parseBeforeAttributeNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar in ["\u002F", "\u003E"]:  # Solidus (/), Greater than sign (>)
                self.reconsume = True
                self.tokenState = tokenizationState.afterAttributeNameState
            elif self.nextChar == "\u003D":  # Equals sign (=)
                self.throwError(parseError.unexpectedEqualsSignBeforeAttributeName, self.parseIndex, 1)
                self.token: tagToken = self.token
                self.token.newAttribute(istr(self.nextChar, self.parseIndex), istr("", -1))
                self.tokenState = tokenizationState.attributeNameState
            else:
                self.token: tagToken = self.token
                self.token.newAttribute(istr("", self.parseIndex), istr("", -1))
                self.reconsume = True
                self.tokenState = tokenizationState.attributeNameState

        def parseAttributeNameState(self):
            # Whitespace, Solidus (/), Greater than sign (>)
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020", "\u002F", "\u003E"]:
                self.reconsume = True
                self.tokenState = tokenizationState.afterAttributeNameState
                self.pushAttribute(self.token)
            elif self.nextChar == "\u003D":  # Equals sign (=)
                self.tokenState = tokenizationState.beforeAttributeValueState
                self.pushAttribute(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token: tagToken = self.token
                self.token.currentAttribute.name.append(self.nextChar.lower())
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token.currentAttribute.name.text += "\uFFFD"  # Replacement character
            elif self.nextChar in ["\u0022", "\u0027", "\u003C"]:  # Quotation mark ("), Apostrophe ('), Less than sign (<)
                self.throwError(parseError.unexpectedCharacterInAttributeName, self.parseIndex, 1)
                self.token: tagToken = self.token
                self.token.currentAttribute.name.append(self.nextChar)
            else:
                self.token: tagToken = self.token
                self.token.currentAttribute.name.append(self.nextChar)

        def parseAfterAttributeNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u002F":  # Solidus (/)
                self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003D":  # Equals sign (=)
                self.tokenState = tokenizationState.beforeAttributeValueState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.token: tagToken = self.token
                self.token.newAttribute(istr("", self.parseIndex), istr("", -1))
                self.reconsume = True
                self.tokenState = tokenizationState.attributeNameState

        def parseBeforeAttributeValueState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u0022":  # Quotation Mark (")
                self.tokenState = tokenizationState.attributeValueDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.tokenState = tokenizationState.attributeValueSingleQuotedState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingAttributeValue, self.parseIndex, 1)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.attributeValueUnquotedState

        def parseAttributeValueDoubleQuotedState(self):
            if self.nextChar == "\u0022":  # Quotation Mark (")
                self.tokenState = tokenizationState.afterAttributValueQuotedState
            elif self.nextChar == "\u0026":  # Ampersand (&)
                self.returnState = tokenizationState.attributeValueDoubleQuotedState
                self.tokenState = tokenizationState.characterReferenceState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: tagToken = self.token
                self.token.currentAttribute.value.text += "\uFFFD"  # Replacement character
            else:
                self.token: tagToken = self.token
                self.token.currentAttribute.value.append(self.nextChar)

        def parseAttributeValueSingleQuotedState(self):
            if self.nextChar == "\u0027":  # Apostrophe (')
                self.tokenState = tokenizationState.afterAttributValueQuotedState
            elif self.nextChar == "\u0026":  # Ampersand (&)
                self.returnState = tokenizationState.attributeValueSingleQuotedState
                self.tokenState = tokenizationState.characterReferenceState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: tagToken = self.token
                self.token.currentAttribute.value.text += "\uFFFD"  # Replacement character
            else:
                self.token: tagToken = self.token
                self.token.currentAttribute.value.append(self.nextChar)

        def parseAttributeValueUnquotedState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u0026":  # Ampersand (&)
                self.returnState = tokenizationState.attributeValueUnquotedState
                self.tokenState = tokenizationState.characterReferenceState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: tagToken = self.token
                self.token.currentAttribute.value.text += "\uFFFD"  # Replacement character
            # Qutoation mark ("), Apostrophe ('), Less than sign (<), Equals sign (=), Grave accent (`)
            elif self.nextChar in ["\u0022", "\u0027", "\u003C", "\u003D", "\u0060"]:
                self.throwError(parseError.unexpectedCharacterInAttributeValue, self.parseIndex, 1)
                self.token: tagToken() = self.token
                self.token.currentAttribute.value.append(self.nextChar)
            else:
                self.token: tagToken() = self.token
                self.token.currentAttribute.value.append(self.nextChar)

        def parseAfterAttributValueQuotedState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.beforeAttributeNameState
            elif self.nextChar == "\u002F":  # Solidus (/)
                self.tokenState = tokenizationState.selfClosingStartTagState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.missingWhiteSpaceBetweenAttributes, self.parseIndex, 1)
                self.tokenState = tokenizationState.beforeAttributeNameState
                self.reconsume = True

        def parseSelfClosingStartTagState(self):
            if self.nextChar == "\u003E":  # Greater than sign (>)
                self.token: tagToken = self.token
                self.token.selfClosing = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.throwError(parseError.unexpectedSolidusInTag, self.parseIndex, 1)
                self.tokenState = tokenizationState.beforeAttributeNameState
                self.reconsume = True

        def parseBogusCommentState(self):
            if self.nextChar == "\u003E": # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.token:commentToken = self.token
                self.token.endIndex = self.parseIndex + 1
                self.emitToken(self.token)
            elif self.nextChar == "\u0000": # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: commentToken = self.token
                self.token.append("\uFFFD") # Replacement character
            else:
                self.token: commentToken = self.token
                self.token.data.append(self.nextChar)

        def parseMarkupDeclarationOpenState(self):
            if self.raw[self.parseIndex: self.parseIndex + 2] == "\u002D\u002D":  # Two hyphen minus characters (--)
                self.parseIndex += 1
                self.token: commentToken = commentToken()
                self.token.startIndex = self.parseIndex - 3
                self.token.data = istr("", self.parseIndex + 1)
                self.tokenState = tokenizationState.commentStartState   
            elif self.raw[self.parseIndex: self.parseIndex + 7] == "DOCTYPE":
                self.parseIndex += 6
                self.tokenState = tokenizationState.doctypeState
            # "CDATA" with Left square bracket characters before and after ([CDATA[)
            elif self.raw[self.parseIndex: self.parseIndex + 7] == "\u005BCDATA\u005B":
                self.throwError(parseError.cdataInHTMLdata, self.parseIndex, 1)
                self.token: commentToken = commentToken()
                self.token.startIndex = self.parseIndex - 3
                self.token.data = istr(self.raw[self.parseIndex: self.parseIndex + 7], self.parseIndex)
                self.parseIndex += 6
            else:
                self.throwError(parseError.incorrectlyOpenedComment, self.parseIndex, 1)
                self.tokenState = tokenizationState.bogusCommentState
                self.reconsume = True

        def parseCommentStartState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentStartDashState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.abruptClosingOfEmptyComment, self.parseIndex, 1)
                self.tokenState = tokenizationState.dataState
                self.token.endIndex = self.parseIndex + 1
                self.emitToken(self.token)
            else:
                self.tokenState = tokenizationState.commentState
                self.reconsume = True

        def parseCommentStartDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentEndState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.abruptClosingOfEmptyComment, self.parseIndex, 1)
                self.tokenState = tokenizationState.dataState
                self.token.endIndex = self.parseIndex + 1
                self.emitToken(self.token)
            else:
                self.token: commentToken = self.token
                self.token.append("\u002D")  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentState
                self.reconsume = True

        def parseCommentState(self):
            if self.nextChar == "\u003C":  # Less than sign (<)
                self.token: commentToken = self.token
                self.token.data.append(self.nextChar)
                self.tokenState = tokenizationState.commentLessThanSignState
            elif self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentEndDashState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: commentToken = self.token
                self.token.append("\uFFFD")  # Replacement character
            else:
                self.token: commentToken = self.token
                self.token.data.append(self.nextChar)

        def parseCommentLessThanSignState(self):
            if self.nextChar == "\u0021":  # Exclamation mark (!)
                self.token: commentToken = self.token
                self.token.data.append(self.nextChar)
                self.tokenState = tokenizationState.commentLessThanSignBangState
            elif self.nextChar == "\u003C":  # Less than sign (<)
                self.token: commentToken = self.token
                self.token.data.append(self.nextChar)
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.commentState

        def parseCommentLessThanSignBangState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentLessThanSignBangDashState
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.commentState

        def parseCommentLessThanSignBangDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentLessThanSignBangDashDashState
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.commentEndDashState

        def parseCommentLessThanSignBangDashDashState(self):
            if self.nextChar == "\u003E":  # Greater than sign (>)
                self.reconsume = True
                self.tokenState = tokenizationState.commentEndState
            else:
                self.throwError(parseError.nestedComment, self.parseIndex, 1)
                self.reconsume = True
                self.tokenState = tokenizationState.commentState

        def parseCommentEndDashState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.tokenState = tokenizationState.commentEndState
            else:
                self.token: commentToken = self.token
                self.token.append("\u002D")  # Hyphen minus (-)
                self.reconsume = True
                self.tokenState = tokenizationState.commentState

        def parseCommentEndState(self):
            if self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.token.endIndex = self.parseIndex + 1
                self.emitToken(self.token)
            elif self.nextChar == "\u0021":  # Exclamation mark (!)
                self.tokenState = tokenizationState.commentEndBangState
            elif self.nextChar == "\u002D":  # Hyphen minus (-)
                self.token: commentToken = self.token
                self.token.data.append(self.nextChar)
            else:
                self.token: commentToken = self.token
                self.token.append("\u002D")  # Hyphen minus (-)
                self.token.append("\u002D")  # Hyphen minus (-)
                self.reconsume = True
                self.tokenState = tokenizationState.commentState

        def parseCommentEndBangState(self):
            if self.nextChar == "\u002D":  # Hyphen minus (-)
                self.token: commentToken = self.token
                self.token.append("\u002D")  # Hyphen minus (-)
                self.token.append("\u002D")  # Hyphen minus (-)
                self.token.append("\u0021")  # Exclamation mark (!)
                self.tokenState = tokenizationState.commentEndDashState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.incorrectlyClosedComment, self.parseIndex, 1)
                self.tokenState = tokenizationState.dataState
                self.token.endIndex = self.parseIndex + 1
                self.emitToken(self.token)
            else:
                self.token.append("\u002D")  # Hyphen minus (-)
                self.token.append("\u002D")  # Hyphen minus (-)
                self.token.append("\u0021")  # Exclamation mark (!)
                self.reconsume = True
                self.tokenState = tokenizationState.commentState

        def parseDoctypeState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.beforeDoctypeNameState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.reconsume = True
                self.tokenState = tokenizationState.beforeDoctypeNameState
            else:
                self.throwError(parseError.missingWhitespaceBeforeDoctypeName, self.parseIndex, 1)
                self.reconsume = True
                self.tokenState = tokenizationState.beforeDoctypeNameState

        def parseBeforeDoctypeNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif isASCIIUpperAlpha(self.nextChar):
                self.token: doctypeToken = doctypeToken()
                self.token.name = istr(self.nextChar.lower, self.parseIndex)
                self.tokenState = tokenizationState.doctypeNameState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: doctypeToken = doctypeToken()
                self.token.name = istr("\uFFFD", self.parseIndex)  # Replacement character
                self.tokenState = tokenizationState.doctypeNameState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingDoctypeName, self.parseIndex, 1)
                self.token: doctypeToken = doctypeToken()
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.token: doctypeToken = doctypeToken()
                self.token.name = istr(self.nextChar, self.parseIndex)
                self.tokenState = tokenizationState.doctypeNameState

        def parseDoctypeNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.afterDoctypeNameState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.name.append(self.nextChar.lower)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token.name.append("\uFFFD")  # Replacement character
                self.tokenState = tokenizationState.doctypeNameState
            else:
                self.token.name.appen(self.nextChar)

        def parseAfterDoctypeNameState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif isASCIIUpperAlpha(self.nextChar):
                self.token.name.append(self.nextChar.lower)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token.name.append("\uFFFD")  # Replacement character
                self.tokenState = tokenizationState.doctypeNameState
            else:
                if self.raw[self.parseIndex: self.parseIndex + 6].upper() == "PUBLIC":
                    self.parseIndex += 5
                    self.tokenState = tokenizationState.afterDoctypePublicKeywordState
                elif self.raw[self.parseIndex: self.parseIndex + 6].upper() == "SYSTEM":
                    self.parseIndex += 5
                    self.tokenState = tokenizationState.afterDoctypeSystemKeywordState
                else:
                    self.throwError(parseError.invalidCharacterSequenceAfterDoctypeName, self.parseIndex, 1)
                    self.token: doctypeToken = self.token
                    self.token.forceQuirks = True
                    self.reconsume = True
                    self.tokenState = tokenizationState.bogusDoctypeState

        def parseAfterDoctypePublicKeywordState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.beforeDoctypePublicIDState
            elif self.nextChar == "\u0022":  # Quotation mark (")
                self.throwError(parseError.missingWhitespaceAfterDoctypePublicKeyword, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.publicID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypePublicIDDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.throwError(parseError.missingWhitespaceAfterDoctypePublicKeyword, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.publicID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypePublicIDSingleQuotedState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingDoctypePublicIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.throwError(parseError.missingQuoteBeforeDoctypePublicIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseBeforeDoctypePublicIDState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u0022":  # Quotation mark (")
                self.token: doctypeToken = self.token
                self.token.publicID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypePublicIDDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.token: doctypeToken = self.token
                self.token.publicID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypePublicIDSingleQuotedState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingDoctypePublicIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.throwError(parseError.missingQuoteBeforeDoctypePublicIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseDoctypePublicIDDoubleQuotedState(self):
            if self.nextChar == "\u0022":  # Quotation mark (")
                self.tokenState = tokenizationState.afterDoctypePublicIDState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.publicID.append("\uFFFD")  # Replacement character
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.abruptDoctypePublicIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.token: doctypeToken = self.token
                self.token.publicID.append(self.nextChar)

        def parseDoctypePublicIDSingleQuotedState(self):
            if self.nextChar == "\u0027":  # Apostrophe (')
                self.tokenState = tokenizationState.afterDoctypePublicIDState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.publicID.append("\uFFFD")  # Replacement character
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.abruptDoctypePublicIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.token: doctypeToken = self.token
                self.token.publicID.append(self.nextChar)

        def parseAfterDoctypePublicIDState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.betweenDoctypePublicSystemIDsState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif self.nextChar == "\u0022":  # Quotation mark (")
                self.throwError(parseError.missingWhitespaceBetweenDoctypePublicAndSystemIds, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.throwError(parseError.missingWhitespaceBetweenDoctypePublicAndSystemIds, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDSingleQuotedState
            else:
                self.throwError(parseError.missingQuoteBeforeDoctypeSystemIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseBetweenDoctypePublicSystemIDsState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif self.nextChar == "\u0022":  # Quotation mark (")
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDSingleQuotedState
            else:
                self.throwError(parseError.missingQuoteBeforeDoctypeSystemIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseAfterDoctypeSystemKeywordState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                self.tokenState = tokenizationState.beforeDoctypeSystemIDState
            elif self.nextChar == "\u0022":  # Quotation mark (")
                self.throwError(parseError.missingWhitespaceAfterDoctypeSystemKeyword, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.throwError(parseError.missingWhitespaceAfterDoctypeSystemKeyword, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDSingleQuotedState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingDoctypeSystemId, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.throwError(parseError.missingQuoteBeforeDoctypeSystemIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseBeforeDoctypeSystemIDState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u0022":  # Quotation mark (")
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDDoubleQuotedState
            elif self.nextChar == "\u0027":  # Apostrophe (')
                self.token: doctypeToken = self.token
                self.token.systemID = istr("", self.parseIndex)
                self.tokenState = tokenizationState.doctypeSystemIDSingleQuotedState
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.missingDoctypeSystemId, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.throwError(parseError.missingQuoteBeforeDoctypeSystemIdentifier, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseDoctypeSystemIDDoubleQuotedState(self):
            if self.nextChar == "\u0022":  # Quotation mark (")
                self.tokenState = tokenizationState.afterDoctypeSystemIDState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.systemID.append("\uFFFD")  # Replacement character
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.abruptDoctypeSystemId, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.token: doctypeToken = self.token
                self.token.systemID.append(self.nextChar)

        def parseDoctypeSystemIDSingleQuotedState(self):
            if self.nextChar == "\u0027":  # Apostrohpe (')
                self.tokenState = tokenizationState.afterDoctypeSystemIDState
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.systemID.append("\uFFFD")  # Replacement character
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.throwError(parseError.abruptDoctypeSystemId, self.parseIndex, 1)
                self.token: doctypeToken = self.token
                self.token.forceQuirks = True
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.token: doctypeToken = self.token
                self.token.systemID.append(self.nextChar)

        def parseAfterDoctypeSystemIDState(self):
            if self.nextChar in ["\u0009", "\u000A", "\u000C", "\u0020"]:  # Whitespace
                None
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            else:
                self.throwError(parseError.unexpectedCharacterAfterDoctypeSystemId, self.parseIndex, 1)
                self.reconsume = True
                self.tokenState = tokenizationState.bogusDoctypeState

        def parseBogusDoctypeState(self):
            if self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
                self.emitToken(self.token)
            elif self.nextChar == "\u0000":  # Null
                self.throwError(parseError.unexpectedNullCharacter, self.parseIndex, 1)
            else:
                None

        def parseCDATASectionState(self):
            if self.nextChar == "\u005D":  # Right square bracket (])
                self.tokenState = tokenizationState.CDATASectionBracketState
            else:
                self.emitCharacter(self.nextChar, self.parseIndex)

        def parseCDATASectionBracketState(self):
            if self.nextChar == "\u005D":  # Right square bracket (])
                self.tokenState = tokenizationState.CDATASectionEndState
            else:
                self.emitCharacter("\u005D", self.parseIndex)  # Right square bracket (])
                self.reconsume = True
                self.tokenState = tokenizationState.CDATASectionState

        def parseCDATASectionEndState(self):
            if self.nextChar == "\u005D":  # Right square bracket (])
                self.emitCharacter("\u005D", self.parseIndex)  # Right square bracket (])
            elif self.nextChar == "\u003E":  # Greater than sign (>)
                self.tokenState = tokenizationState.dataState
            else:
                self.emitCharacter("\u005D", self.parseIndex)  # Right square bracket (])
                self.emitCharacter("\u005D", self.parseIndex)  # Right square bracket (])
                self.reconsume = True
                self.tokenState = tokenizationState.CDATASectionState

        def parseCharacterReferenceState(self):
            self.tempBuffer = "\u0026"  # Ampersand (&)
            if isASCIIAlphaNumeric(self.nextChar):
                self.reconsume = True
                self.tokenState = tokenizationState.namedCharacterReferenceState
            elif self.nextChar == "\u0023":  # Number sign (#)
                self.tempBuffer += self.nextChar
                self.tokenState = tokenizationState.numericCharacterReferenceState
            else:
                self.flushCodePoints(self.tempBuffer, self.parseIndex)

                self.reconsume = True
                self.tokenState = self.returnState
                self.returnState = None

        def parseNamedCharacterReferenceState(self):
            if self.tempBuffer in namedCharacters:
                if ((self.consumedAsPartOfAttribute() and self.tempBuffer[-1] == "\u003B") and # Semicolon (;)
                        (isASCIIAlphaNumeric(self.nextChar) or self.nextChar == "\u003D")): # Equals sign (=)
                    self.flushCodePoints(self.tempBuffer, self.parseIndex)
                    self.tokenState = self.returnState
                else:
                    if self.tempBuffer[-1] != "\u003B": # Semicolon (;)
                        self.throwError(parseError.missingSemicolonAfterCharacterReference, self.parseIndex, 1)
                    self.tempBuffer = namedCharacters[self.tempBuffer]
                    self.flushCodePoints(self.tempBuffer, self.parseIndex)
                    self.tokenState = self.returnState
            elif isASCIIAlphaNumeric(self.nextChar) or self.nextChar == "\u003B": # Semicolon (;)
                self.tempBuffer += self.nextChar
            else:
                self.flushCodePoints(self.tempBuffer, self.parseIndex)
                self.tokenState = tokenizationState.ambiguousAmpersandState

        def parseAmbiguousAmpersandState(self):
            if isASCIIAlphaNumeric(self.nextChar):
                if self.consumedAsPartOfAttribute():
                    self.token:tagToken = self.token
                    self.token.currentAttribute.value.append(self.nextChar)
                else:
                    self.emitCharacter(self.nextChar, self.parseIndex)
            elif self.nextChar == "\u003B": # Semicolon (;)
                self.throwError(parseError.unknownNamedCharacterReference)
                self.tokenState = self.returnState
                self.reconsume = True
            else:
                self.tokenState = self.returnState
                self.reconsume = True

        def parseNumericCharacterReferenceState(self):
            self.characterReferenceCode = 0
            if self.nextChar.lower == "\u0078": # Ambiguous letter x (x or X)
                self.tempBuffer += self.nextChar
                self.tokenState = tokenizationState.hexCharacterReferenceStartState
            else:
                self.reconsume = True
                self.tokenState = tokenizationState.decCharacterReferenceStartState

        def parseHexCharacterReferenceStartState(self):
            if isASCIIHexDigit(self.nextChar):
                self.reconsume = True
                self.tokenState = tokenizationState.hexCharacterReferenceState
            else:
                self.throwError(parseError.absenceOfDigitsInNumericCharacterReference, self.parseIndex, 1)
                self.flushCodePoints(self.tempBuffer, self.parseIndex)
                self.reconsume = True
                self.tokenState = self.returnState
                
        def parseDecCharacterReferenceStartState(self):
            if isASCIIDigit(self.nextChar):
                self.reconsume = True
                self.tokenState = tokenizationState.decCharacterReferenceState
            else:
                self.throwError(parseError.absenceOfDigitsInNumericCharacterReference, self.parseIndex, 1)
                self.flushCodePoints(self.tempBuffer, self.parseIndex)
                self.reconsume = True
                self.tokenState = self.returnState
            
        def parseHexCharacterReferenceState(self):
            if isASCIIDigit(self.nextChar):
                self.characterReferenceCode *= 16
                self.characterReferenceCode += ord(self.nextChar) - 0x0030
            elif isASCIIUpperHex(self.nextChar):
                self.characterReferenceCode *= 16
                self.characterReferenceCode += ord(self.nextChar) - 0x0037
            elif isASCIILowerHex(self.nextChar):
                self.characterReferenceCode *= 16
                self.characterReferenceCode += ord(self.nextChar) - 0x0057
            elif self.nextChar == "\u003B": # Semicolon (;)
                self.tokenState = tokenizationState.numericCharacterReferenceEndState
            else:
                self.throwError(parseError.missingSemicolonAfterCharacterReference, self.parseIndex, 1)
                self.reconsume = True
                self.tokenState = tokenizationState.numericCharacterReferenceEndState

        def parseDecCharacterReferenceState(self):
            if isASCIIDigit(self.nextChar):
                self.characterReferenceCode *= 10
                self.characterReferenceCode += ord(self.nextChar) - 0x0030
            elif self.nextChar == "\u003B": # Semicolon (;)
                self.tokenState = tokenizationState.numericCharacterReferenceEndState
            else:
                self.throwError(parseError.missingSemicolonAfterCharacterReference, self.parseIndex, 1)
                self.reconsume = True
                self.tokenState = tokenizationState.numericCharacterReferenceEndState

        def parseNumericCharacterReferenceEndState(self):
            if self.characterReferenceCode == 0x00: # Null
                self.throwError(parseError.nullCharacterReference, self.parseIndex, 1)
                self.characterReferenceCode = 0xFFFD # Replacement character
            elif self.characterReferenceCode > 0x10FFFF: 
                self.throwError(parseError.characterReferenceOutsideUnicodeRange)
                self.characterReferenceCode = 0xFFFD # Replacement character
            elif isSurrogate(self.characterReferenceCode):
                self.throwError(parseError.surrogateCharacterReference, self.parseIndex, 1)
                self.characterReferenceCode = 0xFFFD # Replacement character
            elif isNonCharacter(self.characterReferenceCode):
                self.throwError(parseError.noncharactercharacterReference, self.parseIndex, 1)
            elif self.characterReferenceCode == 0x0D or (isControl(self.characterReferenceCode) and 
                    not isASCIIWhiteSpace(self.characterReferenceCode)):
                self.throwError(parseError.controlCharacterReference, self.parseIndex, 1)
            elif self.characterReferenceCode in numberCharacterReferences:
                self.characterReferenceCode = numberCharacterReferences[self.characterReferenceCode]
            
            self.tempBuffer = chr(self.characterReferenceCode)
            self.flushCodePoints(self.tempBuffer, self.parseIndex)
            self.tokenState = self.returnState

    def highlightComment(self, token:commentToken):
        cursor:QTextCursor = QTextCursor(self.document)
        cursor.setPosition(token.startIndex, QTextCursor.MoveMode(0))
        
        cursor.setPosition(token.endIndex, QTextCursor.MoveMode(1))
        cursor.setCharFormat(self.htmlFormats["comment"])

    def highlightDoctype(self, token:doctypeToken):
        ...

    def highlightTag(self, token:tagToken):
        ...

    def parseText(self) -> None:
        "Parses the text according to the W3 HTML standard, then "\
            "applying highliting as specified in the addon config"

        # Prevent an infinite recursion loop where every time the
        # text is edited the qconnect in __init__.py is triggered
        # causing the text to be edited in this funciton, triggering
        # the qconnect
        # TODO: Create a less janky way of preventing self-triggered parsing
        if(self.isParsing == 1):
            return

        self.reset()
        self.isParsing = 1

        while self.parseIndex < self.raw.__len__():
            self.nextChar = self.raw[self.parseIndex]
            if self.nextChar == "\n":
                self.lineCount += 1
                self.lineIndex = 0
            else:
                self.lineIndex += 1

            {
                tokenizationState.dataState: self.tokenizer.parseDataState,
                tokenizationState.RCDataState: self.tokenizer.parseRCDataState,
                tokenizationState.rawTextState: self.tokenizer.parseRawTextState,
                tokenizationState.scriptDataState: self.tokenizer.parseScriptDataState,
                tokenizationState.plainTextState: self.tokenizer.parsePlainTextState,
                tokenizationState.tagOpenState: self.tokenizer.parseTagOpenState,
                tokenizationState.endTagOpenState: self.tokenizer.parseEndTagOpenState,
                tokenizationState.tagNameState: self.tokenizer.parseTagNameState,
                tokenizationState.RCDataLessThanSignState: self.tokenizer.parseRCDataLessThanSignState,
                tokenizationState.RCDATAEndTagOpenState: self.tokenizer.parseRCDATAEndTagOpenState,
                tokenizationState.RCDATAEndTagNameState: self.tokenizer.parseRCDATAEndTagNameState,
                tokenizationState.rawTextLessThanSignState: self.tokenizer.parseRawTextLessThanSignState,
                tokenizationState.rawTextEndTagOpenState: self.tokenizer.parseRawTextEndTagOpenState,
                tokenizationState.rawTextEndTagNameState: self.tokenizer.parseRawTextEndTagNameState,
                tokenizationState.scriptDataLessThanSignState: self.tokenizer.parseScriptDataLessThanSignState,
                tokenizationState.scriptDataEndTagOpenState: self.tokenizer.parseScriptDataEndTagOpenState,
                tokenizationState.scriptDataEndTagNameState: self.tokenizer.parseScriptDataEndTagNameState,
                tokenizationState.scriptDataEscapeStartState: self.tokenizer.parseScriptDataEscapeStartState,
                tokenizationState.scriptDataEscapeStartDashState: self.tokenizer.parseScriptDataEscapeStartDashState,
                tokenizationState.scriptDataEscapedState: self.tokenizer.parseScriptDataEscapedState,
                tokenizationState.scriptDataEscapedDashState: self.tokenizer.parseScriptDataEscapedDashState,
                tokenizationState.scriptDataEscapedDashDashState: self.tokenizer.parseScriptDataEscapedDashDashState,
                tokenizationState.scriptDataEscapedLessThanSignState: self.tokenizer.parseScriptDataEscapedLessThanSignState,
                tokenizationState.scriptDataEscapedEndTagOpenState: self.tokenizer.parseScriptDataEscapedEndTagOpenState,
                tokenizationState.scriptDataEscapedEndTagNameState: self.tokenizer.parseScriptDataEscapedEndTagNameState,
                tokenizationState.scriptDataDoubleEscapeStartState: self.tokenizer.parseScriptDataDoubleEscapeStartState,
                tokenizationState.scriptDataDoubleEscapedState: self.tokenizer.parseScriptDataDoubleEscapedState,
                tokenizationState.scriptDataDoubleEscapedDashState: self.tokenizer.parseScriptDataDoubleEscapedDashState,
                tokenizationState.scriptDataDoubleEscapedDashDashState: self.tokenizer.parseScriptDataDoubleEscapedDashDashState,
                tokenizationState.scriptDataDoubleEscapedLessThanSignState: self.tokenizer.parseScriptDataDoubleEscapedLessThanSignState,
                tokenizationState.scriptDataDoubleEscapeEndState: self.tokenizer.parseScriptDataDoubleEscapeEndState,
                tokenizationState.beforeAttributeNameState: self.tokenizer.parseBeforeAttributeNameState,
                tokenizationState.attributeNameState: self.tokenizer.parseAttributeNameState,
                tokenizationState.afterAttributeNameState: self.tokenizer.parseAfterAttributeNameState,
                tokenizationState.beforeAttributeValueState: self.tokenizer.parseBeforeAttributeValueState,
                tokenizationState.attributeValueDoubleQuotedState: self.tokenizer.parseAttributeValueDoubleQuotedState,
                tokenizationState.attributeValueSingleQuotedState: self.tokenizer.parseAttributeValueSingleQuotedState,
                tokenizationState.attributeValueUnquotedState: self.tokenizer.parseAttributeValueUnquotedState,
                tokenizationState.afterAttributValueQuotedState: self.tokenizer.parseAfterAttributValueQuotedState,
                tokenizationState.selfClosingStartTagState: self.tokenizer.parseSelfClosingStartTagState,
                tokenizationState.bogusCommentState: self.tokenizer.parseBogusCommentState,
                tokenizationState.markupDeclarationOpenState: self.tokenizer.parseMarkupDeclarationOpenState,
                tokenizationState.commentStartState: self.tokenizer.parseCommentStartState,
                tokenizationState.commentStartDashState: self.tokenizer.parseCommentStartDashState,
                tokenizationState.commentState: self.tokenizer.parseCommentState,
                tokenizationState.commentLessThanSignState: self.tokenizer.parseCommentLessThanSignState,
                tokenizationState.commentLessThanSignBangState: self.tokenizer.parseCommentLessThanSignBangState,
                tokenizationState.commentLessThanSignBangDashState: self.tokenizer.parseCommentLessThanSignBangDashState,
                tokenizationState.commentLessThanSignBangDashDashState: self.tokenizer.parseCommentLessThanSignBangDashDashState,
                tokenizationState.commentEndDashState: self.tokenizer.parseCommentEndDashState,
                tokenizationState.commentEndState: self.tokenizer.parseCommentEndState,
                tokenizationState.commentEndBangState: self.tokenizer.parseCommentEndBangState,
                tokenizationState.doctypeState: self.tokenizer.parseDoctypeState,
                tokenizationState.beforeDoctypeNameState: self.tokenizer.parseBeforeDoctypeNameState,
                tokenizationState.doctypeNameState: self.tokenizer.parseDoctypeNameState,
                tokenizationState.afterDoctypeNameState: self.tokenizer.parseAfterDoctypeNameState,
                tokenizationState.afterDoctypePublicKeywordState: self.tokenizer.parseAfterDoctypePublicKeywordState,
                tokenizationState.beforeDoctypePublicIDState: self.tokenizer.parseBeforeDoctypePublicIDState,
                tokenizationState.doctypePublicIDDoubleQuotedState: self.tokenizer.parseDoctypePublicIDDoubleQuotedState,
                tokenizationState.doctypePublicIDSingleQuotedState: self.tokenizer.parseDoctypePublicIDSingleQuotedState,
                tokenizationState.afterDoctypePublicIDState: self.tokenizer.parseAfterDoctypePublicIDState,
                tokenizationState.betweenDoctypePublicSystemIDsState: self.tokenizer.parseBetweenDoctypePublicSystemIDsState,
                tokenizationState.afterDoctypeSystemKeywordState: self.tokenizer.parseAfterDoctypeSystemKeywordState,
                tokenizationState.beforeDoctypeSystemIDState: self.tokenizer.parseBeforeDoctypeSystemIDState,
                tokenizationState.doctypeSystemIDDoubleQuotedState: self.tokenizer.parseDoctypeSystemIDDoubleQuotedState,
                tokenizationState.doctypeSystemIDSingleQuotedState: self.tokenizer.parseDoctypeSystemIDSingleQuotedState,
                tokenizationState.afterDoctypeSystemIDState: self.tokenizer.parseAfterDoctypeSystemIDState,
                tokenizationState.bogusDoctypeState: self.tokenizer.parseBogusDoctypeState,
                tokenizationState.CDATASectionState: self.tokenizer.parseCDATASectionState,
                tokenizationState.CDATASectionBracketState: self.tokenizer.parseCDATASectionBracketState,
                tokenizationState.CDATASectionEndState: self.tokenizer.parseCDATASectionEndState,
                tokenizationState.characterReferenceState: self.tokenizer.parseCharacterReferenceState,
                tokenizationState.namedCharacterReferenceState: self.tokenizer.parseNamedCharacterReferenceState,
                tokenizationState.ambiguousAmpersandState: self.tokenizer.parseAmbiguousAmpersandState,
                tokenizationState.numericCharacterReferenceState: self.tokenizer.parseNumericCharacterReferenceState,
                tokenizationState.hexCharacterReferenceStartState: self.tokenizer.parseHexCharacterReferenceStartState,
                tokenizationState.decCharacterReferenceStartState: self.tokenizer.parseDecCharacterReferenceStartState,
                tokenizationState.hexCharacterReferenceState: self.tokenizer.parseHexCharacterReferenceState,
                tokenizationState.decCharacterReferenceState: self.tokenizer.parseDecCharacterReferenceState,
                tokenizationState.numericCharacterReferenceEndState: self.tokenizer.parseNumericCharacterReferenceEndState
            }[self.tokenState](self)

            if(not self.reconsume):
                # curChar = self.nextChar
                self.parseIndex += 1
            else:
                self.reconsume = False

        self.flushCharacterTokenBuffer()
        # Enable parsing on edits
        self.isParsing = 0