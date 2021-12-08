from PyQt5.QtCore import QCollator, QRegularExpression, QRegularExpressionMatch, Qt
from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        tagFormat = QTextCharFormat()
        tagFormat.setForeground(QColor(0xF9, 0x26, 0x72))
        self.highlightingRules = [(QRegularExpression(r"(?:(?<=<)|(?<=<\/))[A-Za-z]+\b"),
                                   tagFormat)]

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor(0x75, 0x71, 0x5E))

        attributeFormat = QTextCharFormat()
        attributeFormat.setForeground(QColor(0xA6, 0xE2, 0x2E))
        self.highlightingRules.append(
            (QRegularExpression(r"(?<=\s)[A-Za-z0-9_-]*[\s*]*(?=[=>])"), attributeFormat))

        moustacheFormat = QTextCharFormat()
        moustacheFormat.setForeground(QColor(0x66, 0xD9, 0xEF))
        self.highlightingRules.append(
            (QRegularExpression(r"\{\{.*\}\}"), moustacheFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor(0xE6, 0xDB, 0x74))
        self.highlightingRules.append(
            (QRegularExpression("\".*\""), quotationFormat))
        self.highlightingRules.append(
            (QRegularExpression("\'.*\'"), quotationFormat))

        self.commentStartExpression = QRegularExpression("<!--*")
        self.commentEndExpression = QRegularExpression("-->")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegularExpression(pattern)
            index: QRegularExpressionMatch = expression.match(text)
            while index.capturedStart() >= 0:
                length = index.capturedLength()
                self.setFormat(index.capturedStart(), length, format)
                index = expression.match(text, index.capturedStart() + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.match(
                text).capturedStart()

        while startIndex >= 0:
            endMatch = self.commentEndExpression.match(text, startIndex)
            endIndex = endMatch.capturedStart()

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + endMatch.capturedLength()

            self.setFormat(startIndex, commentLength,
                           self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.match(
                text, startIndex + commentLength).capturedStart()


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
