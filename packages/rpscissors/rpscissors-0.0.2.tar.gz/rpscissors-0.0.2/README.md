# RPScissors

This module makes it easy to create a Rock Paper Scissors game in Python.

## Basic example

```python
import RPScissors

game = RPScissors.create_default_game()

user = input("Choose stone, paper or scissors: ")
computer, result = game.play_round(user)

print("Computer chose:", computer)
print("Result:", result)
