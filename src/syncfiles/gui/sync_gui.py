"""Handles the Graphical User Interface for the program.


Author: Kevin Hodge
"""

import wx


# noinspection PyAttributeOutsideInit
class YesNoPromptApp(wx.App):
    """

    """
    def __init__(self, message, button_text):
        self.message = message
        self.button_text = button_text
        self.response = "Exit"  # Default to exit if window closes without response
        super().__init__()

    def OnInit(self):
        self.frame = YesNoPromptFrame(parent=None, title="Sync Files Project", message=self.message,
                                      button_text=self.button_text)
        self.frame.Bind(wx.EVT_BUTTON, self.set_response)
        self.frame.Show()
        return True

    def set_response(self, event):
        self.response = event.GetEventObject().GetLabel()
        self.frame.Close()


class YesNoPromptFrame(wx.Frame):
    """

    """
    def __init__(self, parent, title, message, button_text):
        """
        Overwrites __init__() of wx.Frame, so need to call wx.Frame.__init__() within new __init__().
        """
        super().__init__(parent, title=title, size=(300, 200))
        self.message_panel = YesNoPromptPanel(parent=self, message=message, button_text=button_text)
        self.Center()


class YesNoPromptPanel(wx.Panel):
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
class EntryPromptApp(wx.App):
    """

    """
    def __init__(self, message):
        self.message = message
        self.response = ""
        super().__init__()

    def OnInit(self):
        self.frame = EntryPromptFrame(parent=None, title="Sync Files Project", message=self.message)
        return True

    def get_response(self):
        return self.frame.get_response()


class EntryPromptFrame(wx.Frame):
    """

    """

    def __init__(self, parent, title, message):
        """
        Overwrites __init__() of wx.Frame, so need to call wx.Frame.__init__() within new __init__().
        """
        super().__init__(parent, title=title, size=(250, 100))
        self.message_panel = EntryPromptPanel(parent=self, message=message)
        self.Close()

    def get_response(self):
        return self.message_panel.get_response()


class EntryPromptPanel(wx.Panel):
    """

    """
    def __init__(self, parent, message):
        super().__init__(parent)

        self.dialog = wx.TextEntryDialog(self, message, "Directory: ", "", style=wx.OK)
        self.dialog.Center()
        self.dialog.ShowModal()
        self.entry = self.dialog.GetValue()
        self.dialog.Destroy()

    def get_response(self):
        return self.entry


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
        button_text = ["Continue", "Exit"]
        app = YesNoPromptApp(message="Check Again?", button_text=button_text)
        app.MainLoop()
        return app.response

    def directory_prompt(self, valid_dir=None, min_dir=2):
        """
        Asks user to enter a valid directory
        invalid_dir: string
            string containing
        """
        if valid_dir is None:
            valid_dir = []
        message = f"""Only {str(len(valid_dir))} valid, unique directories. Must have {str(min_dir)}.
        Please enter directory to sync below."""
        app = EntryPromptApp(message=message)
        app.MainLoop()
        return app.get_response()

