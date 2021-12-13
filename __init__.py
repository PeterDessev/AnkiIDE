from aqt import mw, gui_hooks, QTextEdit
from aqt.qt import *
from aqt.clayout import CardLayout

from .addon import highlighter
from .addon import default_config

import importlib.util as importUtil
debugpySpec = importUtil.find_spec("debugpy")
foundDebugpy = debugpySpec is not None

if(foundDebugpy):
    import debugpy
    debugpy.listen(("localhost", 5678))

def setUp(clayout: CardLayout) -> None:
    if(foundDebugpy):
        debugpy.wait_for_client()
    mw.my_widgets = []
    editor = clayout.tform.edit_area

    try:
        config = mw.addonManager.getConfig(__name__)
    except AttributeError:
        config = default_config.DEFAULT_CONFIG
        print("Unable to lcoate config, using default config")

    highlighter_widget = highlighter.Highlighter(config, editor.document())
    mw.my_widgets.append(highlighter_widget)
    editor.setTabChangesFocus(False)
    editor.setLineWrapMode(QTextEdit.NoWrap)
    # editor.setLineWrapColumnOrWidth(0)

gui_hooks.card_layout_will_show.append(setUp)