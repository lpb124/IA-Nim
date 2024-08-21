from ._anvil_designer import GameFormTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import string
import random
import time

from ..ContinuePageForm import ContinuePageForm
from ..StartPageForm import StartPageForm

#
# This is the Python code that makes this feedback form work.
# It's a Python class, with a method that runs when the user
# clicks the SUBMIT button.
#
# When the button is clicked, we send the contents of the
# text boxes to our Server Module. The Server Module records
# the feedback in the database, and sends an email to the
# app's owner (that's you!).
#
# To find the Server Module, look under "Server Code" on the
# left.
#
# Initialize a Pile object with a given count of stones.
class Pile:
    def __init__(self, count=0):
        self.count_stones = count

class PileCollection:
    def __init__(self, difficulty='Easy', custom_stones=None):
        # Initialize a PileCollection object with a difficulty level and optional custom stone counts.
        self.difficulty = difficulty
        if custom_stones:
            # If custom_stones is provided, initialize each pile with the corresponding number of stones.
            self.piles = [Pile(count=stone) for stone in custom_stones]
        else:
            # If custom_stones is not provided, initialize each pile with a random number of stones.
            # Here, 3 piles are created with stone counts ranging between 5 and 15.
            self.piles = [Pile(count=random.randint(5, 15)) for _ in range(3)]

    #Displays the number of stones in each pile
    def display(self):
        print('1st pile ({} stones)'.format(self.piles[0].count_stones))
        print('2nd pile ({} stones)'.format(self.piles[1].count_stones))
        print('3rd pile ({} stones)'.format(self.piles[2].count_stones))
    #Removes stones from a specified pile
    def take_stones(self, which_pile, many_stones):
        pile_index = which_pile - 1
        self.piles[pile_index].count_stones = max(0, self.piles[pile_index].count_stones - many_stones)
    #Checks if game is over
    def is_game_over(self):
        if (self.piles[0].count_stones == 0
            and self.piles[1].count_stones == 0
            and self.piles[2].count_stones == 0):
            return True
        
        return False
    #assigns probability of CPU using the algorithm to each level
    def do_AI(self):
            if self.difficulty == 'Easy':
              if random.randint(1, 100) <= 25:
                self.ai_strategic()
              else:
                    self.ai_easy()
            elif self.difficulty == 'Normal':
                if random.randint(1, 100) <= 50:
                    self.ai_strategic()
                else:
                    self.ai_easy()
            elif self.difficulty == 'Hard':
                if random.randint(1, 100) <= 75:
                    self.ai_strategic()
                else:
                    self.ai_easy()
            elif self.difficulty == 'Insane':
                self.ai_strategic()

    def ai_easy(self):
      # Choose a non-empty pile randomly
      non_empty_piles = [(index, pile) for index, pile in enumerate(self.piles) if pile.count_stones > 0]
      if not non_empty_piles:
          print("No moves possible.")
          return  # No non-empty piles to choose from
  
      pile_index, chosen_pile = random.choice(non_empty_piles)
      # Ensure we only try to remove a number of stones that exists in the pile, max 3
      max_stones_to_remove = min(chosen_pile.count_stones, 3)
      if max_stones_to_remove > 0:  # Check to ensure there is at least one stone to remove
          stones_to_remove = random.randint(1, max_stones_to_remove)
          chosen_pile.count_stones -= stones_to_remove
      self.response = (f"CPU took {stones_to_remove} stones from pile {pile_index + 1}")
      
    # Calculate the Nim sum (bitwise XOR of all pile stone counts)
    def calculate_nim_sum(self):
        nim_sum = 0
        for pile in self.piles:
            nim_sum ^= pile.count_stones
        return nim_sum

    def ai_strategic(self):
      nim_sum = self.calculate_nim_sum()
      if nim_sum == 0:
          self.ai_easy()  # If in a losing position, revert to easy mode
      else:
          for i, pile in enumerate(self.piles):
              target = pile.count_stones ^ nim_sum
              if target < pile.count_stones:
                  stones_to_remove = min(pile.count_stones - target, 3)
                  if stones_to_remove > 0:
                      pile.count_stones -= stones_to_remove
                      self.response = (f"CPU took {stones_to_remove} stones from pile {i + 1}")
                      break


class GameForm(GameFormTemplate):
    def __init__(self, **properties):
      self.init_components(**properties)
  
      password = properties.get('password')
      if password:
          try:
              self.difficulty_level, stone_counts, self.step = self.parse_password(password)
              self.headline_1.text = self.headline_1.text + " - " + self.difficulty_level
            
              # Pass the stone counts and difficulty to PileCollection
              self.piles_collection = PileCollection(custom_stones=stone_counts, difficulty=self.difficulty_level)

              # Set the button text based on whose turn it is
              if self.step % 2 == 0:  # Even step, player's turn
                  self.submit_btn.text = 'ENTER'
              else:  # Odd step, CPU's turn
                  self.submit_btn.text = 'CPU\'s Turn!'
                  self.which_pile_txt.enabled = False
                  self.many_stones_txt.enabled = False
                
          except ValueError as e:
              Notification(str(e)).show()
              return  # Stop initialization on error
      else:
          self.difficulty_level = properties.get('difficulty_level', 'Easy')
          self.headline_1.text = self.headline_1.text + " - " + self.difficulty_level
          self.piles_collection = PileCollection(difficulty=self.difficulty_level)  # Default initialization
          self.step = 0  # Default step
  
      self.update_piles_text()
      self.first_pile_cnv_reset()
      self.second_pile_cnv_reset()
      self.third_pile_cnv_reset()


    def parse_password(self, password):
      # Assume password format is "difficulty-random_string-stone1-stone2-stone3-step"
      parts = password.split('-')
      if len(parts) < 6:
          raise ValueError("Invalid password format.")
  
      difficulty = self.decode_difficulty(parts[0])
      stone_counts = list(map(int, parts[2:5]))
      step = int(parts[5])  # Get the step number from the password
      
      return difficulty, stone_counts, step

    #Decodes difficulty level from password
    def decode_difficulty(self, encoded):
        difficulty_codes = {
            'EZX10': 'Easy',
            'NRM20': 'Normal',
            'HRD30': 'Hard',
            'INS40': 'Insane'
        }
        return difficulty_codes.get(encoded, 'Easy')  # Default to 'Easy'

    def update_piles_text(self):
        # Assuming there are text labels or text fields in your form for each pile
        self.first_pile_txt.text = str(self.piles_collection.piles[0].count_stones)
        self.second_pile_txt.text = str(self.piles_collection.piles[1].count_stones)
        self.third_pile_txt.text = str(self.piles_collection.piles[2].count_stones)

    def clear_inputs(self):
      # Assuming 'which_pile_txt' and 'many_stones_txt' are the text fields you want to clear
      self.which_pile_txt.text = ""
      self.many_stones_txt.text = ""

    def update_pile_texts(self):
        # This function updates the text boxes with the current number of stones
        self.first_pile_txt.text = str(self.piles_collection.piles[0].count_stones)
        self.second_pile_txt.text = str(self.piles_collection.piles[1].count_stones)
        self.third_pile_txt.text = str(self.piles_collection.piles[2].count_stones)

    def reset_pile_canvases(self):
        # Resets the visual representation of the piles
        self.first_pile_cnv_reset()
        self.second_pile_cnv_reset()
        self.third_pile_cnv_reset()

    def first_pile_cnv_reset(self, sender=None, **event_args):
        stone_img = anvil.URLMedia('_/theme/stone.png')
        x = 0
        self.first_pile_cnv.clear_rect(0, 0, 10000, 20)
        for i in range(self.piles_collection.piles[0].count_stones):
            self.first_pile_cnv.draw_image(stone_img, x, 0)
            x += 15

    def second_pile_cnv_reset(self, sender=None, **event_args):
        stone_img = anvil.URLMedia('_/theme/stone.png')
        x = 0
        self.second_pile_cnv.clear_rect(0, 0, 10000, 20)
        for i in range(self.piles_collection.piles[1].count_stones):
            self.second_pile_cnv.draw_image(stone_img, x, 0)
            x += 15

    def third_pile_cnv_reset(self, sender=None, **event_args):
        stone_img = anvil.URLMedia('_/theme/stone.png')
        x = 0
        self.third_pile_cnv.clear_rect(0, 0, 10000, 20)
        for i in range(self.piles_collection.piles[2].count_stones):
            self.third_pile_cnv.draw_image(stone_img, x, 0)
            x += 15
    #checks if the user's input for the pile number and the number of stones to remove are numeric values.
    def validate_input(self):
      try:
          if not (self.which_pile_txt.text.isnumeric()) or not (self.many_stones_txt.text.isnumeric()):
            raise ValueError("The pile number and number of stones should be numeric values!")

          which_pile = int(self.which_pile_txt.text)  # Assuming you have a text input for the pile number
          many_stones = int(self.many_stones_txt.text)  # Assuming you have a text input for the number of stones
          
          if not (1 <= which_pile <= 3):
              raise ValueError("Pile number must be between 1 and 3!")
          if not (1 <= many_stones <= 3):
              raise ValueError("The number of stones must be between 1 and 3!")
          if many_stones > self.piles_collection.piles[which_pile - 1].count_stones:
              raise ValueError("Not enough stones in the selected pile!")
  
          return which_pile, many_stones  # Returning a tuple of two integers
  
      except ValueError as e:
          Notification(str(e)).show()
          return None, None  # Returning a tuple so it can still be unpacked

    def submit_btn_click(self, **event_args):
      # Check whose turn it is based on the step counter
      if self.step % 2 == 0:  # Player's turn

          self.which_pile_txt.enabled = False
          self.many_stones_txt.enabled = False
          self.submit_btn.enabled = False
        
          which_pile, many_stones = self.validate_input()
          
          if which_pile is None or many_stones is None:
            self.which_pile_txt.enabled = True
            self.many_stones_txt.enabled = True
            self.submit_btn.text = 'ENTER'
            time.sleep(1)
            self.submit_btn.enabled = True
            return
  
          self.piles_collection.take_stones(which_pile, many_stones)
          self.update_piles_text()
          self.reset_pile_canvases()


          
          # Check if the game is over after the player's move
          if self.piles_collection.is_game_over():
             next_difficulty = self.get_next_difficulty()
             if next_difficulty == "End":
                Notification("Congratulations you win the game!!! Returning to the main menu").show()
                time.sleep(3)
                open_form(StartPageForm())
             else:  
              Notification("Congratulations you win this round! Ready for the " + next_difficulty + " level?").show()
              time.sleep(2)
              open_form(ContinuePageForm(next_difficulty_level=next_difficulty))
             return
          
          # Update the step for the CPU's turn
          self.step += 1
          self.which_pile_txt.text = ""
          self.many_stones_txt.text = ""
          self.submit_btn.text = 'CPU\'s Turn!'
          time.sleep(1)
          self.submit_btn.enabled = True
  
      else:  # CPU's turn        
          self.cpu_play()  # Call a separate method to handle CPU's turn
          self.update_piles_text()
          self.reset_pile_canvases()
  
          # Check if the game is over after the CPU's move
          if self.piles_collection.is_game_over():
              Notification("Too bad, CPU wins!").show()
              time.sleep(2)
              open_form(StartPageForm())
              return
  
          # Update the step for the player's turn
          self.step += 1
          self.which_pile_txt.enabled = True
          self.many_stones_txt.enabled = True
          self.submit_btn.text = 'ENTER'
          time.sleep(1)
          self.submit_btn.enabled = True
    

    def cpu_play(self):
        # Logic for the CPU's move
        self.piles_collection.do_AI()
        Notification(self.piles_collection.response).show()
  
    def get_next_difficulty(self):
        difficulty_levels = ['Easy', 'Normal', 'Hard', 'Insane', 'End']
        current_index = difficulty_levels.index(self.difficulty_level)
        next_index = min(current_index + 1, len(difficulty_levels) - 1)
        return difficulty_levels[next_index]  # Return the next difficulty level

    def encode_difficulty(self, difficulty):
      # Simple mapping of difficulty to a coded string
      difficulty_codes = {
          'Easy': 'EZX10',
          'Normal': 'NRM20',
          'Hard': 'HRD30',
          'Insane': 'INS40'
      }
      return difficulty_codes.get(difficulty, 'UNK')  # 'UNK' for Unknown if no match

    def save_btn_click(self, **event_args):
      # Generates a password for saving current game state
      random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
      
      # Encode the current difficulty level
      encoded_difficulty = self.encode_difficulty(self.difficulty_level)
      
      # Retrieve the number of stones in each pile
      stones = [pile.count_stones for pile in self.piles_collection.piles]
      
      # Include the current step in the password
      password = f"{encoded_difficulty}-{random_str}-{stones[0]}-{stones[1]}-{stones[2]}-{self.step}"
      
      # Display the password to the user
      Notification(f"Your game password is: {password}").show()








