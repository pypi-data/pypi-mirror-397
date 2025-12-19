import random
import sys
from typing import List, Dict

class systemRPS:
    def __init__(self, options: List[str], win_rules: Dict[str, str]):
        self.options = options
        self.win_rules = win_rules

    def get_computer_choice(self) -> str:
        return random.choice(self.options)
    
    def determine_winner(self, user_choice: str, computer_choice: str) -> str:
        user_choice = user_choice.lower()

        if user_choice not in self.options:
            print(f"Invalid choice. Use on of: {', '.join(self.options)}")
            sys.exit(1)
        
        if user_choice == computer_choice:
            return "tie"
        elif self.win_rules[user_choice] == computer_choice:
            return "user"
        else:
            return "computer"
        
    def play_round(self, user_choice: str):
        computer_choice = self.get_computer_choice()
        result = self.determine_winner(user_choice, computer_choice)
        return computer_choice, result
    
DEFAULT_OPTIONS = ["stone", "paper", "scissors"]
DEFAULT_WIN_RULES = {
    "stone": "scissors",
    "scissors": "paper",
    "paper": "stone",
}

def create_default_game() -> systemRPS:
    return systemRPS(DEFAULT_OPTIONS, DEFAULT_WIN_RULES)