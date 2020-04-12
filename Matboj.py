"""Ranking system for individual Matboj-style competition."""
import json
import os
import re
import sys


class Person(object):

  def __init__(self, name, rank=1000.0, old_ranks=None):
    self.name = name
    self.rank = rank
    self.old_ranks = old_ranks if old_ranks else []

  def __lt__(self, other):
    return self.rank - other.rank

  def update_rank(self, new_rank):
    self.old_ranks.append(self.rank)
    self.rank = new_rank

  def undo(self):
    if self.old_ranks:
      self.rank = self.old_ranks[-1]
      del self.old_ranks[-1]

  def to_dict(self):
    return {'name': self.name, 'rank': self.rank, 'old_ranks': self.old_ranks}

  @classmethod
  def from_dict(cls, d):
    return Person(name=d['name'], rank=d['rank'], old_ranks=d['old_ranks'])


def load_people(path):
  """Loads a list of people from the path and assigns each default score."""
  people = []
  with open(path, 'r') as people_file:
    for line in people_file.readlines():
      people.append(Person(line.strip()))
  return people


def print_list(lst, cols=3):
  # Make sure the length of the list is an exact multiple of cols.
  lst.extend([''] * (-len(lst) % cols))
  num_rows = len(lst) // cols
  for elements in [lst[i::num_rows] for i in range(num_rows)]:
    print(' │ '.join(elements))


def new_ranks(winner, loser):
  new_winner_rank = winner.rank + 100 - (winner.rank - loser.rank) / 3
  new_loser_rank = loser.rank - 100 - (loser.rank - winner.rank) / 3
  return new_winner_rank, new_loser_rank


class Matboj(object):

  def __init__(self, people, match_list=None):
    self._people = people
    self._names_to_people = {p.name: p for p in self._people}
    self._match_list = match_list or []

  def save_game_state(self):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'Game_state.json'), 'w') as output:
      game_state = {
          'people': [p.to_dict() for p in
                     sorted(self._people, key=lambda e: -e.rank)],
          'match_list': self._match_list}
      output.write(json.dumps(game_state, indent='  '))

  def load_game_state(self):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'Game_state.json'), 'r') as game_state:
      game_state = json.loads(game_state.read())
      self._people = [Person.from_dict(p) for p in game_state['people']]
      self._names_to_people = {p.name: p for p in self._people}
      self._match_list = game_state['match_list']

  def print_ranking(self):
    name_len = max(len(p.name) for p in self._people)
    print_list([
        '%2d. %s: %4d' % (i + 1, p.name.ljust(name_len + 1).title(), p.rank)
        for i, p in enumerate(sorted(self._people, key=lambda e: -e.rank))])
    print()

  def _undo_match(self, match):
    self._names_to_people[match[0]].undo()
    self._names_to_people[match[1]].undo()

  def undo(self, position):
    if not self._match_list:
      print('Nothing to undo.')
      return

    if position > len(self._match_list):
      print('Not enough matches (%d) to undo position match at position -%d'
            % (len(self._match_list), position))
      return

    undo_winner_name, undo_loser_name = self._match_list[-position]
    print('Undo %s:%s? [y/n] ' % (undo_winner_name, undo_loser_name), end='')
    answer = input().strip()
    if answer == 'y':
      # Undo all the matches up to the bad one, then redo them since somebody
      # has maybe already played with the players whose match we are undoing.
      redo_buffer = []
      for _ in range(position - 1):
        current_match = self._match_list.pop()
        redo_buffer.append(current_match)
        self._undo_match(current_match)
      # Undo the actual bad match.
      bad_match = self._match_list.pop()
      self._undo_match(bad_match)
      # Redo the matches.
      for redo_match in redo_buffer:
        self.rerank(*redo_match)
      print('Undo done for %s:%s' % (undo_winner_name, undo_loser_name))
      self.print_ranking()


  def rerank(self, name1, name2):
    if name1 in self._names_to_people and name2 in self._names_to_people:
      winner = self._names_to_people[name1.lower()]
      loser = self._names_to_people[name2.lower()]
      new_winner_rank, new_loser_rank = new_ranks(
          winner=winner, loser=loser)
      winner.update_rank(new_winner_rank)
      loser.update_rank(new_loser_rank)
      self._match_list.append((winner.name, loser.name))
      self.save_game_state()
    else:
      print('Unknown winner or loser name.')

  def run(self):
    self.print_ranking()

    print('Welcome to Matboj! Type "help" to show available commands.')
    while True:
      print('\033[94m$\033[0m\033[92m ', end='')
      command = input().strip()
      print('\033[0m', end='')

      if command == '':
        continue
      if command == 'about':
        print('Written by Augustin Zidek in 2020.')
      elif command in ['quit', 'exit']:
        self.save_game_state()
        exit()
      elif command in ['status', 'print']:
        self.print_ranking()
      elif command == 'matches':
        print(', '.join(['%s:%s' % (w, l) for w, l in self._match_list]))
      elif command == 'save':
        self.save_game_state()
        print('Game state saved.')
      elif command == 'load':
        self.load_game_state()
        print('Game state loaded.')
        self.print_ranking()
      elif command == 'help':
        print('Commands: about, quit, print, matches, save, load, undo [num], '
              '<winner name>:<loser name>')
      elif command == 'undo':
        self.undo(position=1)
      elif re.match('undo [0-9]+', command):
        undo_position = int(re.match('undo ([0-9]+)', command).group(1))
        self.undo(position=undo_position)
      elif re.match(r'\w+:\w+', command):
        name1, name2 = command.split(':')
        self.rerank(name1, name2)
        self.print_ranking()
      else:
        print('Unknown command.')


def main(unused_args):
  dirname = os.path.dirname(__file__)
  people = load_people(os.path.join(dirname, 'People.txt'))

  matboj = Matboj(people)
  matboj.run()


if __name__ == "__main__":
  main(sys.argv)
