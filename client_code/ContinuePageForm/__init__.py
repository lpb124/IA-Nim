from ._anvil_designer import ContinuePageFormTemplate
from anvil import *
import anvil.server

class ContinuePageForm(ContinuePageFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Store the next difficulty level, defaulting to 'Easy' if not provided
        self.next_difficulty_level = properties.get('next_difficulty_level', 'Easy')
        #Embedding of the youtube tutorial 
        self.youtube_video_1.youtube_id="C-KqmBMyv4s"
        self.youtube_video_1.autoplay = True
        

    def continue_game_click(self, **event_args):
        from ..GameForm import GameForm
        """This method is called when the continue button is clicked"""
        # Start a new game with the next difficulty level
        game_frm = GameForm(difficulty_level=self.next_difficulty_level)
        open_form(game_frm)

    def youtube_video_1_state_change(self, state, **event_args):
      
      """This method is called when the video changes state (eg PAUSED to PLAYING)"""
      pass
