from ._anvil_designer import LoadPageFormTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class LoadPageForm(LoadPageFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.


  def load_game(self, **event_args):
    from ..GameForm import GameForm
    # Retrieve and strip any whitespace from the entered password
    password = self.password_txt.text.strip()
    
    # Attempt to create a GameForm instance with the provided password
    if password:
        try:
            game_frm = GameForm(password=password)
            open_form(game_frm)
        except ValueError as e:
            Notification(str(e)).show()
    else:
        Notification("Please enter a valid password.").show()

  def back(self, **event_args):
    """This method is called when the button is clicked"""
    from ..StartPageForm import StartPageForm
    open_form(StartPageForm())
    pass

