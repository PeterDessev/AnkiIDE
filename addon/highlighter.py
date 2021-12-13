from PyQt5.QtCore import QRegularExpression, QRegularExpressionMatch
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat
from . import default_config

defConfig = default_config.DEFAULT_CONFIG


class Highlighter(QSyntaxHighlighter):
    def __init__(self, config, parent=None):
        super(Highlighter, self).__init__(parent)
        self.html = []
        self.js = []
        self.css = []

        try:
            self.html = config["html"][config["profile"]["html"]]["format"]
        except:
            print("AnkiIDE ERROR: Error accessing profile %s for html, check addon config",
                  config["profile"]["html"])
            self.html = defConfig["html"][config["profile"]["html"]]["format"]

        try:
            self.js = config["javascript"][config["profile"]
                                      ["javascript"]]["format"]
        except:
            print("AnkiIDE ERROR: Error accessing profile %s for javascript, check addon config",
                  config["profile"]["javascript"])
            self.js = defConfig["javascript"][config["profile"]
                                         ["javascript"]]["format"]

        try:
            self.css = config["css"][config["profile"]["css"]]["format"]
        except:
            print("AnkiIDE ERROR: Error accessing profile %s for css, check addon config",
                  config["profile"]["css"])
            self.css = defConfig["css"][config["profile"]["css"]]["format"]

        # HMTL Highlighting rules
        # Tags such as <p> or <div>, not inlcluding the
        # angle brackets
        tagFormat = QTextCharFormat()
        tagFormat.setForeground(QColor(self.html["tag"]["color"]))
        self.htmlHighlightingRules = [(QRegularExpression(r"(?:(?<=<)|(?<=<\/))[A-Za-z0-9_-]+"),
                                       tagFormat)]

        # Attributes that go inside tags such as id or class
        attributeFormat = QTextCharFormat()
        attributeFormat.setForeground(QColor(self.html["attribute"]["color"]))
        self.htmlHighlightingRules.append(
            (QRegularExpression(r"(?<=\s)[A-Za-z0-9_-]+\s*(?=[\=>])"), attributeFormat))

        # This is the Anki specific "{{field}}" notation,
        # I'm not sure what the technical term for it is.
        ankiFieldFormat = QTextCharFormat()
        ankiFieldFormat.setForeground(QColor(self.html["ankiField"]["color"]))
        self.htmlHighlightingRules.append(
            (QRegularExpression(r"\{\{.*\}\}"), ankiFieldFormat))

        # String literals that fall inside of single or double quotes
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor(self.html["keyword"]["color"]))
        self.htmlHighlightingRules.append(
            (QRegularExpression(r"(?:\"[^\"\\]*(?:\\.[^\"\\]*)*\")"), keywordFormat))
        self.htmlHighlightingRules.append(
            (QRegularExpression(r"(?:'[^'\\]*(?:\\.[^'\\]*)*')"), keywordFormat))

        # HTML single and multiline comments use the same escape sequence
        # Comment format
        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor(self.html["comment"]["color"]))
        # Comment regex, because comments can be multiline, a different
        # method for highlighting is used
        self.commentStartExpression = QRegularExpression("<!--")
        self.commentEndExpression = QRegularExpression("-->")

        # Script tags can contain js dirrectly and therefore require a
        # special case for highlighting
        self.scriptStartExpression = QRegularExpression(r"\<script\>")
        self.scriptEndExpression = QRegularExpression(r"\<\/script\>")

        # JS Highlighting rules
        functionName = [r"\w*\s*(?=\()", r"(?<=var)\s*\w*\s*=\s*function\s*(?=\()",
                        r"(?<=\W)\w*\s*:\s*function\s*(?=\()"]
        functionNameFormat = QTextCharFormat()
        functionNameFormat.setForeground(QColor(self.js["functionName"]["color"]))
        self.scriptHighlightingRules = [(QRegularExpression(word), functionNameFormat)
                                        for word in functionName]

        keywords = [r"(?<!\w)abstract(?!\w)", r"(?<!\w)arguments(?!\w)", r"(?<!\w)oolean(?!\w)", r"(?<!\w)break(?!\w)", r"(?<!\w)byte(?!\w)",
                    r"(?<!\w)case(?!\w)", r"(?<!\w)catch(?!\w)", r"(?<!\w)char(?!\w)", r"(?<!\w)const(?!\w)", r"(?<!\w)continue(?!\w)",
                    r"(?<!\w)debugger(?!\w)", r"(?<!\w)default(?!\w)", r"(?<!\w)delete(?!\w)", r"(?<!\w)do(?!\w)", r"(?<!\w)double(?!\w)",
                    r"(?<!\w)else(?!\w)", r"(?<!\w)eval(?!\w)", r"(?<!\w)false(?!\w)", r"(?<!\w)final(?!\w)", r"(?<!\w)finally(?!\w)",
                    r"(?<!\w)float(?!\w)", r"(?<!\w)for(?!\w)", r"(?<!\w)goto(?!\w)", r"(?<!\w)if(?!\w)",
                    r"(?<!\w)implements(?!\w)", r"(?<!\w)in(?!\w)", r"(?<!\w)instanceof(?!\w)", r"(?<!\w)int(?!\w)", r"(?<!\w)interface(?!\w)",
                    r"(?<!\w)long(?!\w)", r"(?<!\w)native(?!\w)", r"(?<!\w)new(?!\w)", r"(?<!\w)null(?!\w)", r"(?<!\w)package(?!\w)",
                    r"(?<!\w)private(?!\w)", r"(?<!\w)protected(?!\w)", r"(?<!\w)public(?!\w)", r"(?<!\w)return(?!\w)", r"(?<!\w)short(?!\w)",
                    r"(?<!\w)static(?!\w)", r"(?<!\w)switch(?!\w)", r"(?<!\w)synchronized(?!\w)", r"(?<!\w)this(?!\w)", r"(?<!\w)throw(?!\w)",
                    r"(?<!\w)throws(?!\w)", r"(?<!\w)transient(?!\w)", r"(?<!\w)true(?!\w)", r"(?<!\w)try(?!\w)", r"(?<!\w)typeof(?!\w)",
                    r"(?<!\w)void(?!\w)", r"(?<!\w)volatile(?!\w)", r"(?<!\w)while(?!\w)", r"(?<!\w)with(?!\w)", r"(?<!\w)yield(?!\w)"]
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor(self.js["keyword"]["color"]))
        for word in keywords:
            self.scriptHighlightingRules.append(
                (QRegularExpression(word), keywordFormat))

        operators = [r"\!", r"\|", r"\=", r"\&", r"\-", r"\*", r"\/", r"\^", r"\%", r"\+",
                     r"\<", r"\>", r"(?<!\w)typeof(?!\w)",  r"(?<!\w)instanceof(?!\w)",
                     r"\~"]
        operatorFormat = QTextCharFormat()
        operatorFormat.setForeground(QColor(self.js["operator"]["color"]))
        for word in operators:
            self.scriptHighlightingRules.append(
                (QRegularExpression(word), operatorFormat))

        declarations = [r"(?<!\w)var(?!\w)",
                        r"(?<!\w)function(?!\w)", r"(?<!\w)let(?!\w)"]
        declarationFormat = QTextCharFormat()
        declarationFormat.setForeground(QColor(self.js["declaration"]["color"]))
        for word in declarations:
            self.scriptHighlightingRules.append(
                (QRegularExpression(word), declarationFormat))

        numbers = [r"(?<!\w)null(?!\w)", r"(?<!\w)\-?[0-9]+\.?[0-9]*(?:[eE]\-?[0-9]*)?(?!\w)",
                   r"(?<!\w)\-?[0-9]*\.?[0-9]+(?:[eE]\-?[0-9]*)?(?!\w)", r"(?<!\w)0b[0-1]*(?!\w)", r"(?<!\w)0x[0-9a-fA-F]*(?!\w)"]
        numberFormat = QTextCharFormat()
        numberFormat.setForeground(QColor(self.js["number"]["color"]))
        for word in numbers:
            self.scriptHighlightingRules.append(
                (QRegularExpression(word), numberFormat))

        jsThis = [r"(?<!\w)void(?!\w)"]
        jsThisFormat = QTextCharFormat()
        jsThisFormat.setForeground(QColor(self.js["this"]["color"]))
        for word in jsThis:
            self.scriptHighlightingRules.append(
                (QRegularExpression(word), jsThisFormat))

        # comment = [r"\/\/[^\n]*"]
        # commentFormat = QTextCharFormat()
        # commentFormat.setForeground(QColor(self.js["comment"]["color"]))
        # for word in comment:
        #     self.scriptHighlightingRules.append(
        #         (QRegularExpression(word), commentFormat))

        strings = [r"(?:\"[^\"\\]*(?:\\.[^\"\\]*)*\")",
                   r"(?:'[^'\\]*(?:\\.[^'\\]*)*')"]
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor(self.js["string"]["color"]))
        for word in strings:
            self.scriptHighlightingRules.append(
                (QRegularExpression(word), stringFormat))
                
        self.jsCommentFormat = QTextCharFormat()
        self.jsCommentFormat.setForeground(QColor(self.js["comment"]["color"]))


        # Regex Highlighting rules
        # Regex has so many highlighting rules that it is easier to treat
        # it like a script or comment tag, despite being only allowed on one line
        self.regexStartExpression = QRegularExpression(r"(?<!\\)\/")
        self.regexCapture = QRegularExpression(r"(?<!\\)/.*?[^\\]/")

        regexClass = [r"(?:\[[^\[\\]*(?:\\.[^\[\\]*)*\])"]
        regexClassFormat = QTextCharFormat()
        regexClassFormat.setForeground(QColor(0xAE, 0x81, 0xFF))
        for word in regexClass:
            self.regexHighlightingRules = [
                (QRegularExpression(word), regexClassFormat)]

    def highlightBlock(self, text: str):
        NoState = 0
        CommentState = 1
        ScriptState = 2

        CommentIndex = 0
        ScriptIndex = 0

        clearedFormat = QTextCharFormat()
        clearedFormat.setForeground(QColor(0xFF, 0xFF, 0xFF))
        clearedFormat.setFontItalic(False)

        # Highlight all of the basic HTML rules such as:
        # Tags, Attributes, and string literals
        for pattern, format in self.htmlHighlightingRules:
            expression = QRegularExpression(pattern)
            match: QRegularExpressionMatch = expression.match(text)
            while match.capturedStart() >= 0:
                length = match.capturedLength()
                self.setFormat(match.capturedStart(), length, format)
                match = expression.match(text, match.capturedStart() + length)

        # Reset current block's state
        self.setCurrentBlockState(NoState)

        # If there is no previous state, we check if there is
        # a comment, a script tag, or both in the block
        if self.previousBlockState() == NoState:
            CommentIndex = self.commentStartExpression.match(
                text).capturedStart()
            ScriptIndex = self.scriptStartExpression.match(
                text).capturedStart()

        # If there is a previous comment state that means we keep highlighting like a comment
        # If there is no previous state, we check if there is no script tag in the block
        # or if the comment tag comes before the script tag in the block,
        # an highlight as a comment
        if(self.previousBlockState() is CommentState or (CommentIndex >= 0 and
            (self.previousBlockState() is NoState and (ScriptIndex < 0 or CommentIndex < ScriptIndex)))):
            # Not sure why this is in a loop, it was in the example,
            # and it works without the loop, however, I don't want to
            # remove it yet....
            while CommentIndex >= 0:
                endMatch = self.commentEndExpression.match(text, CommentIndex)
                endIndex = endMatch.capturedStart()

                if endIndex == -1:
                    self.setCurrentBlockState(CommentState)
                    commentLength = len(text) - CommentIndex
                else:
                    commentLength = endIndex - CommentIndex + endMatch.capturedLength()

                self.setFormat(CommentIndex, commentLength,
                               self.multiLineCommentFormat)
                CommentIndex = self.commentStartExpression.match(
                    text, CommentIndex + commentLength).capturedStart()

        # If there is a previous script state that means we keep highlighting like a script
        # If there is no previous state, we check if there is no comment tag in the block
        # or if the script tag comes before the comment tag in the block,
        # an highlight as a script
        elif(self.previousBlockState() is ScriptState or (ScriptIndex >= 0 and 
             (self.previousBlockState() is NoState and (CommentIndex < 0 or ScriptIndex < CommentIndex)))):
            # Highlight JS
            endMatch = self.scriptEndExpression.match(text, ScriptIndex)
            endIndex = endMatch.capturedStart()

            while ScriptIndex >= 0:
                
                if endIndex == -1:
                    self.setCurrentBlockState(ScriptState)
                    scriptLength = len(text) - ScriptIndex
                else:
                    scriptLength = endIndex - ScriptIndex + endMatch.capturedLength()

                if(ScriptIndex >= 0):
                    ScriptIndex += self.scriptStartExpression.match(
                        text).capturedLength()

                if endIndex == -1:
                    self.setFormat(ScriptIndex, scriptLength, clearedFormat)
                else:
                    self.setFormat(ScriptIndex, endIndex -
                                   ScriptIndex, clearedFormat)

                # Format the script tag according to the JS rules in __init__
                for pattern, format in self.scriptHighlightingRules:
                    expression = QRegularExpression(pattern)

                    # Get the first match
                    match: QRegularExpressionMatch = expression.match(
                        text, ScriptIndex)
                    while match.capturedStart() >= 0 and match.capturedLength() > 0:
                        # Format the current match, making sure to stay inside of script tags
                        if(endIndex == -1 or match.capturedStart() + match.capturedLength() <= endIndex):
                            self.setFormat(match.capturedStart(),
                                           match.capturedLength(), format)
                            match = expression.match(
                                text, match.capturedStart() + match.capturedLength())
                        elif(match.capturedStart() < endIndex):
                            self.setFormat(match.capturedStart(
                            ), endIndex - match.capturedStart(), format)
                            match = expression.match(text, endIndex)
                            break
                        else:
                            match = expression.match(text, endIndex)
                            break

                ScriptIndex = self.scriptStartExpression.match(
                    text, ScriptIndex + scriptLength).capturedStart()
       
            # Special highlighting for comments and regex in JS to make sure they aren't
            # in strings     
            start = 0;
            end = text.__len__() - 1
            inString = '\0'

            if ScriptIndex != -1:
                start = ScriptIndex
            if endIndex != -1:
                end = endIndex
            for i in range(start, end):
                if(i != end):
                    # Found valid comment token
                    if(inString == '\0' and text[i] == '/' and text[i + 1] == '/'):
                        self.setFormat(i, end, self.jsCommentFormat)
                        # Break because the rest of the line will be commented, and not anything else
                        break

                    elif(inString == '\0' and text[i] == '/'):
                        regexMatch = self.regexStartExpression.match(text, offset=i, matchOptions=QRegularExpression.MatchOption(1))
                        # No regex end token found
                        if(regexMatch.capturedStart() < 0):
                            # Continue because there could be other formating requirements later in the line
                            continue;

                        # TEMP
                        regexFormat = QTextCharFormat()
                        regexFormat.setForeground(QColor("#0000FF"))
                        # /TEMP

                        self.setFormat(i, regexMatch.capturedLength(), regexFormat)
                        i += regexMatch.capturedLength()

                    # Found valid string token, toggle starting or ending 
                    elif((i == 0 or text[i - 1] != '\\') and (text[i] == '\'' or text[i] == '\"' or text[i] == '/')):
                        if(inString == '\0'):
                            inString = text[i]
                        elif(inString == text[i]):
                            inString = '\0'


    def addHTMLFormat(self, rules, color, style):
        return

    def addJSFormat(self, rules, color, style):
        return

    def addCSSFormat(self, rules, color, style):
        return

# TOKENS = ('tag',
#           'element',
#           'attribute',
#           'equals',
#           'value',
#           'ankiField',
#           'comment')

# PROPERTIES = ('color', 'style')

# DEFAULT_PROPERTIES = {'color': 'black',
#                       'style': ''}

# def create_styles(style_config):
#     styles = {}
#     for token in TOKENS:
#         style = {}
#         for property in PROPERTIES:
#             try:
#                 style[property] = style_config['{}_{}'.format(token, property)]
#             except KeyError:
#                 style[property] = DEFAULT_PROPERTIES[property]
#         styles[token] = format(**style)
#     return styles
