"""Handles the Graphical User Interface for the program.


Author: Kevin Hodge
"""

from typing import Any, List
import wx


class YesNoPromptPanel(wx.Panel):
    """Inherits from wx.Panel, displays message and buttons

    Attributes:
        label (wx.StaticText): Message displayed to user.
        buttons (list[wx.Button]): Buttons for user to click.

    """
    def __init__(self, parent: Any, message: str, button_text: List[str]) -> None:
        """Creates layout of panel for YesNoPromptApp when initialized.

        Args:
            parent (Any): Identifies what the panel is contained within.
            message (str): Message displayed to user.
            button_text (list[str]): Contains messages displayed on each button.

        """
        super().__init__(parent)

        self.label: wx.StaticText = wx.StaticText(self, label=message, style=wx.ALIGN_CENTER)

        # This code puts the label in the middle of the Panel
        vbox_message: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        hbox_message: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        vbox_message.Add(self.label, 0, wx.ALIGN_CENTER)
        hbox_message.Add(vbox_message, -1, wx.ALIGN_CENTER)
        gridsizer: wx.GridSizer = wx.GridSizer(2, 1, 5, 5)
        gridsizer.Add(hbox_message, -1, wx.EXPAND)

        self.buttons: List[wx.Button] = [wx.Button]
        vbox_buttons: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        hbox_buttons: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        for button_label in button_text:
            self.buttons.append(wx.Button(self, -1, label=button_label))
            hbox_buttons.Add(self.buttons[-1], 0, wx.ALIGN_BOTTOM | wx.TOP | wx.BOTTOM | wx.RIGHT | wx.LEFT, 2)
        vbox_buttons.Add(hbox_buttons, -1, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        gridsizer.Add(vbox_buttons, 0, wx.EXPAND)

        self.SetSizer(gridsizer)


class YesNoPromptFrame(wx.Frame):
    """Inherits from wx.Frame, frame draws window and contains panel.

    Attributes:
        message_panel (YesNoPromptPanel): Panel on which the message and buttons are displayed.

    """
    def __init__(self, parent: Any, title: str, message: str, button_text: List[str]) -> None:
        """Overwrites __init__() of wx.Frame, so need to call wx.Frame.__init__() within new __init__()."""
        super().__init__(parent, title=title, size=(300, 200))
        self.message_panel = YesNoPromptPanel(parent=self, message=message, button_text=button_text)
        self.Center()


# noinspection PyAttributeOutsideInit
class YesNoPromptApp(wx.App):
    """Inherits from wx.App, prompts user for yes/no response.

    Attributes:
        message (str): Question posed to user.
        button_text (list[str]): Button responses available to user.
        response (str): Records response. Defaults to "Exit".

    """
    def __init__(self, message: str, button_text: List[str]) -> None:
        self.message: str = message
        self.button_text: List[str] = button_text
        self.response: str = "Exit"  # Default to exit if window closes without response
        super().__init__()

    def OnInit(self) -> bool:
        self.frame: YesNoPromptFrame = YesNoPromptFrame(parent=None, title="Sync Files Project",
                                                        message=self.message, button_text=self.button_text)
        self.frame.Bind(wx.EVT_BUTTON, self.set_response)
        self.frame.Show()
        return True

    def set_response(self, event: wx.Event) -> None:
        self.response = str(event.GetEventObject().GetLabel())
        self.frame.Close()


class EntryPromptPanel(wx.Panel):
    """Inherits from wx.Panel, displays dialog for user to enter reponse.

    Attributes:
        dialog (wx.TextEntryDialog):
        entry (str):

    """
    def __init__(self, parent: Any, message: str) -> None:
        super().__init__(parent)
        self.dialog: wx.TextEntryDialog = wx.TextEntryDialog(self, message, "Exit Prompt", "", style=wx.OK)
        self.dialog.Center()
        self.dialog.ShowModal()
        self.entry: str = str(self.dialog.GetValue())
        self.dialog.Destroy()

    def get_response(self) -> str:
        return self.entry


class EntryPromptFrame(wx.Frame):
    """Inherits from wx.Frame, draws window and contains panel for EntryPromptApp

    Attributes:
        message_panel (EntryPromptPanel): Panel containing dialog for user entry.

    """

    def __init__(self, parent: Any, title: str, message: str) -> None:
        """Overwrites __init__() of wx.Frame, so need to call wx.Frame.__init__() within new __init__().

        Args:
            parent (Any): Identifies what the panel is contained within.
            title (str): Title of the frame.
            message (str): Message displayed to the user.

        """
        super().__init__(parent, title=title, size=(250, 100))
        self.message_panel: EntryPromptPanel = EntryPromptPanel(parent=self, message=message)
        self.Close()

    def get_response(self) -> str:
        return self.message_panel.get_response()


# noinspection PyAttributeOutsideInit
class EntryPromptApp(wx.App):
    """Inherits from wx.App, prompts user for text response.

    Attributes:
        message (str): Message displayed to user.
        response (str): Response from user.

    """
    def __init__(self, message: str) -> None:
        """Inherits from wx.App, prompts user for entry.

        Args:
            message (str): Message displayed to user.

        """
        self.message: str = message
        self.response: str = ""
        super().__init__()

    def OnInit(self) -> bool:
        self.frame: EntryPromptFrame = EntryPromptFrame(parent=None, title="Sync Files Project", message=self.message)
        return True

    def get_response(self) -> str:
        return self.frame.get_response()


class SyncGUI:
    """Class that handles all GUI interactions.

    Attributes:
        None

    """
    def __init__(self) -> None:
        pass

    def exit_prompt(self) -> str:
        """Open a window to ask the user a question and get a response, then close the window."""
        app: YesNoPromptApp = YesNoPromptApp(message="Check Again?", button_text=["Continue", "Exit"])
        app.MainLoop()
        return app.response

    def directory_prompt(self, num_valid_dir: int, min_dir: int = 2) -> str:
        """Asks user to enter a valid directory

        Args:
            invalid_dir (list): list initialized to [] on each function call.
            min_dir (int): number of directories required.
        """
        message: str = f"""Only {num_valid_dir} valid, unique directories. Must have {str(min_dir)}.
        Please enter directory to sync below."""
        app: EntryPromptApp = EntryPromptApp(message=message)
        app.MainLoop()
        return app.get_response()
