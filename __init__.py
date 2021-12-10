# # import the main window object (mw) from aqt
from aqt import mw
# # import the "show info" tool from utils.py
# # import entire Qt GUI library
from aqt.qt import *

from anki.hooks import wrap
from aqt.clayout import CardLayout

from . import css
from . import html
from .default_config import DEFAULT_CONFIG
import json

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from aqt.clayout import CardLayout
from aqt import gui_hooks
from aqt import QTextEdit
from aqt.utils import showInfo

# import debugpy
# debugpy.listen(("localhost", 5678))

def setUp(clayout: CardLayout) -> None:
    mw.my_widgets = []
    editor = clayout.tform.edit_area
    # languages = ('html', 'css')

    # try:
    #     config = mw.addonManager.getConfig(__name__)
    # except AttributeError:
    #     config = DEFAULT_CONFIG

    # profiles = {}
    # for language in languages:
    #     try:
    #         profile_name = config['user'][language]
    #     except KeyError:
    #         profile_name = 'default'
    #     profiles[language] = config[language][profile_name]

    # TODO: Implement Font choice
    # if config['font'] is not 'default':
        # monospace = QFont('Areal')
        # monospace.setStyleHint(QFont.TypeWriter)
        # mw.my_widgets.append(monospace)
        # editor.setFont(monospace)

    highlighter_widget = html.Highlighter(editor.document())
    mw.my_widgets.append(highlighter_widget)
    editor.setLineWrapMode(QTextEdit.NoWrap)
    # editor.setLineWrapColumnOrWidth(0)
    return

gui_hooks.card_layout_will_show.append(setUp)
# print('Now is a good time to attach your debugger: Run: Python: Attach')
# debugpy.wait_for_client()

# highlighters = {'html': html.HtmlHighlighter,
#                 'css': css.CssHighlighter}


# def wrap_key(text_edit):
#     original_key_press = text_edit.keyPressEvent

#     def key_press(event):
#         if event.key() == Qt.Key_Tab:
#             text_edit.insertPlainText('  ')
#         else:
#             original_key_press(event)

#     text_edit.keyPressEvent = key_press


# def attach_highlighter(self):
#     mw.my_widgets = []
#     editors = {'html': [self.tform.front, self.tform.back],
#                'css':  [self.tform.css]}
#     languages = ('html', 'css')

#     try:
#         config = mw.addonManager.getConfig(__name__)
#     except AttributeError:
#         config = DEFAULT_CONFIG

#     profiles = {}
#     for language in languages:
#         try:
#             profile_name = config['user'][language]
#         except KeyError:
#             profile_name = 'default'
#         profiles[language] = config[language][profile_name]

#     # TODO: test this on other platforms besides Linux
#     monospace = QFont('Monospace')
#     monospace.setStyleHint(QFont.TypeWriter)
#     mw.my_widgets.append(monospace)

#     for language, text_edits in editors.items():
#         for text_edit in text_edits:
#             text_edit.setFont(monospace)
#             # wrap_key(text_edit)
#             highlighter = highlighters[language]
#             highlighter_widget = highlighter(text_edit.document(), profiles[language]['style'])
#             mw.my_widgets.append(highlighter_widget)

#     CardLayout.readCard = wrap(CardLayout.readCard, attach_highlighter)

