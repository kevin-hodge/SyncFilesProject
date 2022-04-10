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
        super().__init__(parent, title=title, size=(250, 100))
        button_text = ["Continue", "Exit"]
        self.message_panel = ExitPromptPanel(parent=self, message="Check Again?", button_text=button_text)
        self.Center()


class ExitPromptPanel(wx.Panel):
    """

    """
    def __init__(self, parent, message, button_text):
        super().__init__(parent)

        self.label = wx.StaticText(self, label=message, style=wx.ALIGN_CENTER)

        # This code puts the label in the middle of the Panel
        vbox_message = wx.BoxSizer(wx.VERTICAL)
        hbox_message = wx.BoxSizer(wx.HORIZONTAL)
        vbox_message.Add(self.label, 0, wx.ALIGN_CENTER)
        hbox_message.Add(vbox_message, -1, wx.ALIGN_CENTER)
        gridsizer = wx.GridSizer(2, 1, 5, 5)
        gridsizer.Add(hbox_message, -1, wx.EXPAND)

        self.buttons = [wx.Button]
        vbox_buttons = wx.BoxSizer(wx.VERTICAL)
        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
        for button_label in button_text:
            self.buttons.append(wx.Button(self, -1, label=button_label))
            hbox_buttons.Add(self.buttons[-1], 0, wx.ALIGN_BOTTOM | wx.TOP | wx.BOTTOM | wx.RIGHT | wx.LEFT, 2)
        vbox_buttons.Add(hbox_buttons, -1, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        gridsizer.Add(vbox_buttons, 0, wx.EXPAND)

        self.SetSizer(gridsizer)


# noinspection PyAttributeOutsideInit
class ExitPromptApp(wx.App):
    """

    """
    def __init__(self, message):
        self.message = message
        self.response = "Exit"  # Default to exit if window closes without response
        super().__init__()

    def OnInit(self):
        self.frame = ExitPromptFrame(parent=None, title="Sync Files Project")
        self.frame.Bind(wx.EVT_BUTTON, self.set_response)
        self.frame.Show()
        return True

    def set_response(self, event):
        clicked_button = event.GetEventObject().GetLabel()
        if clicked_button == "Continue":
            self.response = "Continue"
        self.frame.Close()


class SyncGUI:
    """
    Class that handles all GUI interactions.
    """

    def __init__(self):
        pass

    def exit_prompt(self):
        """
        Open a window to ask the user a question and get a response, then close the window.
        """
        app = ExitPromptApp(message="Check Again?")
        app.MainLoop()
        return app.response

