from PyQt5.QtCore import QCollator, QRegularExpression, QRegularExpressionMatch, Qt
from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        # HMTL Highlighting rules
        # Tags such as <p> or <div>, not inlcluding the 
        # angle brackets
        tagFormat = QTextCharFormat()
        tagFormat.setForeground(QColor(0xF9, 0x26, 0x72))
        self.htmlHighlightingRules = [(QRegularExpression(r"(?:(?<=<)|(?<=<\/))[A-Za-z0-9_-]+"),
                                   tagFormat)]

        # Attributes that go inside tags such as id or class
        attributeFormat = QTextCharFormat()
        attributeFormat.setForeground(QColor(0xA6, 0xE2, 0x2E))
        self.htmlHighlightingRules.append(
            (QRegularExpression(r"(?<=\s)[A-Za-z0-9_-]+\s*(?=[\=>])"), attributeFormat))

        # Moustache is the Anki specific "{{field}}" notation,
        # I'm not sure what the technical term for it is. 
        moustacheFormat = QTextCharFormat()
        moustacheFormat.setForeground(QColor(0x66, 0xD9, 0xEF))
        self.htmlHighlightingRules.append(
            (QRegularExpression(r"\{\{.*\}\}"), moustacheFormat))

        # String literals that fall inside of single or double quotes
        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor(0xE6, 0xDB, 0x74))
        self.htmlHighlightingRules.append(
            (QRegularExpression("\".*?\""), quotationFormat))
        self.htmlHighlightingRules.append(
            (QRegularExpression("\'.*?\'"), quotationFormat))

        # HTML single and multiline comments use the same escape sequence
        # Comment format
        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor(0x75, 0x71, 0x5E))
        # Comment regex, because comments can be multiline, a different
        # method of matching is used
        self.commentStartExpression = QRegularExpression("<!--")
        self.commentEndExpression = QRegularExpression("-->")


        # Script tags can contain js dirrectly and therefore require a 
        # special case for highlighting
        self.scriptStartExpression = QRegularExpression(r"\<script\>")
        self.scriptEndExpression = QRegularExpression(r"\<\/script\>")


        # JS Highlighting rules
        self.scriptHighlightingRules = [(QRegularExpression(r".*"),
                                   tagFormat)]
    def highlightBlock(self, text: str):
        NoState = 0
        CommentState = 1
        ScriptState = 2

        CommentIndex = 0
        ScriptIndex = 0
        
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
        elif(self.previousBlockState() is ScriptState or 
        (self.previousBlockState() is NoState and (CommentIndex < 0 or ScriptIndex < CommentIndex))):
            # Highlight JS
            while ScriptIndex >= 0:
                endMatch = self.scriptEndExpression.match(text, ScriptIndex)
                endIndex = endMatch.capturedStart()

                if endIndex == -1:
                    self.setCurrentBlockState(ScriptState)
                    scriptLength = len(text) - ScriptIndex
                else:
                    scriptLength = endIndex - ScriptIndex + endMatch.capturedLength()
                
                if(ScriptIndex >= 0):
                    ScriptIndex += self.scriptStartExpression.match(
                        text).capturedLength()

                # Format the script tag according to the JS rules in __init__
                for pattern, format in self.scriptHighlightingRules:
                    expression = QRegularExpression(pattern)

                    # Get the first match
                    match: QRegularExpressionMatch = expression.match(text, ScriptIndex)
                    while match.capturedStart() >= 0 and match.capturedLength() > 0:
                        # Format the current match, making sure to stay inside of script tags
                        if(endIndex == -1 or match.capturedStart() + match.capturedLength() <= endIndex):
                            self.setFormat(match.capturedStart(), match.capturedLength(), format)
                            match = expression.match(text, match.capturedStart() + match.capturedLength())
                        elif(match.capturedStart() < endIndex):
                            self.setFormat(match.capturedStart(), endIndex - match.capturedStart(), format)
                            match = expression.match(text, endIndex)
                            break;
                        else:
                            match = expression.match(text, endIndex)
                            break;

                # self.setFormat(ScriptIndex, scriptLength,
                #             self.multiLineCommentFormat)
                ScriptIndex = self.scriptStartExpression.match(
                    text, ScriptIndex + scriptLength).capturedStart()

            # endMatch = self.commentEndExpression.match(text, CommentIndex)
            # endIndex = endMatch.capturedStart()
            # ofset = 0 

            # if(endIndex == -1):
            #     ofset = text.__len__()
            # else:
            #     ofset = expression.match(text.substr )
                
            # for pattern, format in self.scriptHighlightingRules:
            #     expression = QRegularExpression(pattern)

            #     # Get the first match
            #     match: QRegularExpressionMatch = expression.match(text)
            #     while match.capturedStart() >= 0:
            #         # Format the current match
            #         self.setFormat(match.capturedStart(), match.capturedLength(), format)
            #         # Get the next match
            #         match = expression.match(text, match.capturedStart() + length)

            # while ScriptIndex >= 0:
            #     endMatch = self.commentEndExpression.match(text, CommentIndex)
            #     endIndex = endMatch.capturedStart()

            #     if endIndex == -1:
            #         self.setCurrentBlockState(1)
            #         commentLength = len(text) - CommentIndex
            #     else:
            #         commentLength = endIndex - CommentIndex + endMatch.capturedLength()

            #     self.setFormat(CommentIndex, commentLength,
            #                 self.multiLineCommentFormat)
            #     CommentIndex = self.commentStartExpression.match(
            #         text, CommentIndex + commentLength).capturedStart()

# from typing import Match, Pattern
# from aqt.qt import *
# import re

# def format(color, style=''):
#     """Return a QTextCharFormat with the given attributes.
#     """
#     _color = QColor()
#     _color.setNamedColor(color)

#     _format = QTextCharFormat()
#     _format.setForeground(_color)
#     if 'bold' in style:
#         _format.setFontWeight(QFont.Weight.Bold)
#     if 'italic' in style:
#         _format.setFontItalic(True)

#     return _format


# TOKENS = ('tag',
#           'element',
#           'attribute',
#           'equals',
#           'value',
#           'moustache',
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


# class HtmlHighlighter(QSyntaxHighlighter):
#     """Syntax highlighter for the Python language.
#     """

#     def __init__(self, document, style_config):
#         QSyntaxHighlighter.__init__(self, document)
#         styles = create_styles(style_config)


#         self.rules = []
#         # Each rule has three parts:
#         # 1: The regular expression to match in the document
#         # 2: An array of integers that represent which capture groups from 1
#         #     need to have their style changed
#         # 3: The actual style that needs to be applied

#         self.rules += [[r'<\/?|\/?>',
#             [0],
#             styles['tag']]]

#         self.rules += [[r'<\/?([A-Za-z0-9_]+)>?',
#             [1],
#             styles['element']]]

#         self.rules += [[r'\b([A-Za-z0-9_]+) *(=) *([\"\'])((?:\\\3|(?:(?!\3)[^\1\0])*)*)(\3)?',
#             [1],
#             styles['attribute']]]

#         self.rules += [[r'\b([A-Za-z0-9_]+) *(=) *([\"\'])((?:\\\3|(?:(?!\3)[^\1\0])*)*)(\3)?',
#             [2],
#             styles['equals']]]

#         self.rules += [[r'\{\{[#^\/]?\w+:?\w+\}\}',
#             [0],
#             styles['moustache']]]

#         self.rules += [[r'\b([A-Za-z0-9_]+) *(=) *([\"\'])((?:\\\3|(?:(?!\3)[^\1\0])*)*)(\3)?',
#             [3, 4, 5],
#             styles['value']]]

#         self.rules += [[r'<!--.*-->',
#             [],
#             styles['comment']]]


#         # Build a QRegularExpression from the python regex for each rule
#         for x in range(len(self.rules)):
#             expression:Pattern = re.compile(self.rules[x][0])
#             self.rules[x][0] = expression

#     def highlightBlock(self, text:str):
#         """Apply syntax highlighting to the given block of text.
#         """

#         # -------
#         # Highligh HTML
#         # -------
#         expression:Pattern
#         # print("\"" + text + "\"")
#         print("Text Length: " + str(text.__len__()))
#         for expression, capGroups, format in self.rules:
#             # print(expression.pattern())
#             index:index = 0

#             while True:
#                 match:Match = expression.search(text, index)
#                 if(match is None):
#                     break;
#                 print(match.group())
#                 print("start: " + str(match.start()))
#                 print("end: " + str(match.end()))
#                 print("Match count: ", end="")
#                 print(str(expression.findall(text, index)))
#                 index = match.group().__len__() + match.start()
#                 capIndex:int = 0
#                 for capIndex in capGroups:
#                     self.setFormat(match.start(capIndex), match.group(capIndex).__len__(), format)

#                 # print("    ", end="")
#                 # print(match.capturedTexts())
#                 # index += length

#         self.setCurrentBlockState(0)
#         # print()

#     def match_multiline(self, text, delimiter, in_state, style):
#         """Do highlighting of multi-line strings. ``delimiter`` should be a
#         ``QRegularExpression`` for triple-single-quotes or triple-double-quotes, and
#         ``in_state`` should be a unique integer to represent the corresponding
#         state changes when inside those strings. Returns True if we're still
#         inside a multi-line string when this function is finished.
#         """
#         pass
