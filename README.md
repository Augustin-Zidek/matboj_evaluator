# Matboj evaluator

Used at math camps like Pikomat or KMS for keeping score when all participants
in the camp play a board game and need to compute individual ranks periodically.

## Features

* Print the current score or matches that have been played so far.
* Undo any match that has been played and recorded incorrectly.
* Save the game state in a JSON file and restore from it at any other time.
* Written as a command-line app which makes it extremely ergonomic to use and
  the user can handle 40+ kids playing at the same time.
* No setup and dependencies needed, only a Python 3 installation.
* Short (< 300 lines of code), so easy to hack and customize.
* Permissive MIT license.

## Using the evaluator

Put names of all the contestants in the `People.txt` file, one name per line.
All the names have to be unique and they are case-sensitive.

Then launch the application from the terminal:

```bash
python Matboj.py
```

Note that the app is Python 3+, so you might have to use the `python3` binary if
the `python` binary still points to to Python 2 on your system.

If you are using the app interactively, increase the text size in your terminal
and use an overhead projector to show the players what their scores are.
