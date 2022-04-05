from PyQt5 import QtWidgets
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.clayout import CardLayout
from aqt.utils import showWarning

from .addon import parser
from .addon import default_config

#region Debugpy Initialization
import importlib.util as importUtil
debugpySpec = importUtil.find_spec("debugpy")
foundDebugpy = debugpySpec is not None

if(foundDebugpy):
    import debugpy
    print("Awaiting debug on port 5678...")
    debugpy.listen(("localhost", 5678))
    debugpy.wait_for_client()
else:
    print("Unable to load debugpy, continuing execution")
#endregion

def setUp(clayout: CardLayout) -> None:
    mw.IDEwidgets = []
    editor:QtWidgets.QTextEdit = clayout.tform.edit_area

    try:
        config = mw.addonManager.getConfig(__name__)
    except AttributeError:
        config = default_config.DEFAULT_CONFIG
        showWarning("Unable to lcoate config, using default config")

    
    HTMLParse = parser.IDE(config, editor)
    mw.IDEwidgets.append(HTMLParse)
    
gui_hooks.card_layout_will_show.append(setUp)