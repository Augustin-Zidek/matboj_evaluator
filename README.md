# Matboj evaluator

Used at math camps like Pikomat or KMS for keeping score when all participants
in the camp play a board game and need to compute individual ranks periodically.

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
