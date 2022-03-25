"""
Sync GUI
"""

import wx


class ExitPromptFrame(wx.Frame):
    """

    """
    def __init__(self, parent, title):
        """
        Overwrites __init__() of wx.Frame, so need to call wx.Frame.__init__() within new __init__().
        """
        super(ExitPromptFrame, self).__init__(parent, title=title, size=(300, 200))
        self.panel = ExitPromptPanel(self)
        self.Center()



class ExitPromptPanel(wx.Panel):
    def __init__(self, parent):
        super(ExitPromptPanel, self).__init__(parent)

        self.label = wx.StaticText(self, label="Check Again?", style=wx.ALIGN_CENTER)
        self.label.SetBackgroundColour(wx.RED)
        self.SetBackgroundColour(wx.BLUE)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.label)
        self.SetSizer(hbox)


# noinspection PyAttributeOutsideInit
class ExitPromptApp(wx.App):
    def OnInit(self):
        self.frame = ExitPromptFrame(parent=None,
                                     title="Test Window")
        self.frame.Show()
        return True


class SyncGUI:
    """
    Class that handles all GUI interactions.
    """

    def __init__(self):
        self.exit_command = False

    def exit_prompt(self):
        """
        Open a window to ask the user a question and get a response, then close the window.
        """
        app = ExitPromptApp()
        app.MainLoop()

