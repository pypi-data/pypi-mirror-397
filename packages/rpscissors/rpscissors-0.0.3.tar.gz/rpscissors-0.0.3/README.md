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
```
## Advanced example

```python
import RPScissors

options = ["fire", "water", "plant"]
win_rules = {
    "fire": "plant",
    "plant": "water",
    "water": "fire",
}

game = RPScissors.systemRPS(options, win_rules)

user = input("Choose fire, water or plant: ")
computer, result = game.play_round(user)

print("Computer chose:", computer)
print("Result:", result)
```
You can now specify the names of the options yourself.
And adjust the winning rules.