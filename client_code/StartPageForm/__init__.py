from ._anvil_designer import StartPageFormTemplate
from anvil import *
import anvil.server
class StartPageForm(StartPageFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.

    def start_game_click(self, **event_args):
        """This method is called when the button is clicked"""
        from ..GameForm import GameForm
        game_frm = GameForm()
        open_form(game_frm)

    def load_game_click(self, **event_args):
      """This method is called when the button is clicked"""
      from ..LoadPageForm import LoadPageForm
      game_frm = LoadPageForm()
      open_form(game_frm)
