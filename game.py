import random
from colorama import Fore, Back
from merchants import merchant_interaction
from replit import clear
from blessed import Terminal
import time


grass = f"{Fore.LIGHTGREEN_EX}~ {Fore.WHITE}"
wall = f"{Fore.BLACK}x {Fore.WHITE}"
placed_wall = f"{Fore.BLACK}X {Fore.WHITE}"
broken_wall = f"{Fore.BLACK}- {Fore.WHITE}"
spike = f"{Fore.RED}ㅅ{Fore.WHITE}"
flat_spike = f"{Fore.RED}ㅡ{Fore.WHITE}"
chest = f"{Fore.YELLOW}[]{Fore.WHITE}"
looted_chest = f"{Fore.YELLOW}[ {Fore.WHITE}"
heart = f"{Fore.RED}♡ {Fore.WHITE}"
merchant = f"{Fore.YELLOW}ㅠ{Fore.WHITE}"
mineshaft = f"{Fore.YELLOW}⊓ {Fore.WHITE}"

loot = ["hammer", "pickaxe", "block", "gold"]
loot_weights = [1, 1, 1, 5]


class World:

  def __init__(self, choices, weights, radius):
    self.board = {
        (0, 0): grass,
        (-5, random.choice([5, -5])): merchant,
        (5, random.choice([5, -5])): mineshaft
    }
    self.radius = radius
    self.choices = choices
    self.weights = weights

  def get_visible_window(self, x, y):
    visible = []
    for i in range(y - self.radius, y + self.radius + 1):
      row = []
      for j in range(x - self.radius, x + self.radius + 1):
        if (i, j) not in self.board:
          block = random.choices(self.choices, weights=self.weights)[0]
          self.board[i, j] = block
        row.append(self.board[i, j])
      visible.append(row)
    return visible

  def get_board_value(self, coord):
    return self.board.get((coord[1], coord[0]), None)

  def print_board(self, x, y):
    visible = self.get_visible_window(x, y)
    for row in visible:
      print("|" + Back.LIGHTGREEN_EX + "".join(row) + Back.RESET + "|")

  def set_board_value(self, coord, value):
    self.board[(coord[1], coord[0])] = value


class Player:

  def __init__(self, icon, coordinates, max_health=3, hammers=1, pickaxes=1):
    self.icon = icon
    self.coordinates = coordinates
    self.direction = "N"
    self.max_health = max_health
    self.health = max_health
    self.hammers = hammers
    self.pickaxes = pickaxes
    self.blocks = 0
    self.gold = 0


def display(board, boardrange, players):
  # board is a list of lists containing the environment that the current player can see
  # boardrange is a tuple of the rectangular range of the board that the player can see - i.e., ((-4,-4), (4,4)) for a board whose coordinates in both directions range from -4 to 4
  # players is a list of the active players
  for player in players:
    if boardrange[0][0] <= player.coordinates[0] <= boardrange[1][
        0] and boardrange[0][1] <= player.coordinates[1] <= boardrange[1][1]:
      board[player.coordinates[0] -
            boardrange[0][0]][player.coordinates[1] -
                              boardrange[0][1]] = player.icon
  for row in board:
    print("|" + Back.LIGHTGREEN_EX + "".join(row) + Back.RESET + "|")


def center_to_range(center, radius):
  return ((center[0] - radius, center[1] - radius), (center[0] + radius,
                                                     center[1] + radius))

def death(p, w):
  clear()
  print(f"({p.coordinates[0]}, {p.coordinates[1] * -1})")
  print("HEALTH: " + heart * p.health + "X " * (p.max_health - p.health))
  print(f"BLOCKS: {p.blocks}  GOLD: {p.gold}")
  print(f"HAMMERS: {p.hammers}  PICKAXES: {p.pickaxes}")
  print("-" * 32)
  display(board, center_to_range(p.coordinates, w.radius), [p])
  print("-" * 32)
  print("you died (x_x)")
  input("press enter to respawn")










def game():
  p = Player('ツ', coordinates=[0, 0])
  w=World([grass,wall,spike,chest,merchant,mineshaft],[20,5,1,0.1,0.01,0.01],7)

  input("press enter to start")
  
  while True:  #game loop
    time.sleep(0.2)
    clear()
    board = w.get_visible_window(p.coordinates[0], p.coordinates[1])

    #prints out the full display
    print(f"({p.coordinates[0]}, {p.coordinates[1] * -1}) {p.direction}")
    print("HEALTH: " + heart * p.health + "X " * (p.max_health - p.health))
    print(f"BLOCKS: {p.blocks}  GOLD: {p.gold}")
    print(f"HAMMERS: {p.hammers}  PICKAXES: {p.pickaxes}")
    print("-" * 32)
    display(board, center_to_range(p.coordinates, w.radius), [p])
    print("-" * 32)

    with Terminal().cbreak():  #input detection and player movement
      print("controls:")
      print("wasd to move")
      print("q to break blocks")
      print("e to place")
      print("")
      move = Terminal().inkey(timeout=60)
      candidate_move = p.coordinates.copy()

      if move == "w":
        p.direction = "N"
        candidate_move[1] -= 1
      elif move == "s":
        p.direction = "S"
        candidate_move[1] += 1
      elif move == "a":
        p.direction = "W"
        candidate_move[0] -= 1
      elif move == "d":
        p.direction = "E"
        candidate_move[0] += 1

      elif move == "e":  #placing
        if p.direction == "N":
          candidate_move[1] -= 1
        elif p.direction == "S":
          candidate_move[1] += 1
        elif p.direction == "W":
          candidate_move[0] -= 1
        elif p.direction == "E":
          candidate_move[0] += 1
        if w.get_board_value(candidate_move) == grass and p.blocks > 0:
          w.set_board_value(candidate_move, placed_wall)
          p.blocks -= 1
        candidate_move = p.coordinates

      elif move == "q":  #breaking
        if p.direction == "N":
          candidate_move[1] -= 1
        elif p.direction == "S":
          candidate_move[1] += 1
        elif p.direction == "W":
          candidate_move[0] -= 1
        elif p.direction == "E":
          candidate_move[0] += 1

        if w.get_board_value(candidate_move) == placed_wall:
          w.set_board_value(candidate_move, grass)
          p.blocks += 1

        if w.get_board_value(candidate_move) == wall and p.pickaxes > 0:
          p.pickaxes -= 1
          p.blocks += random.randint(1, 5)
          w.set_board_value(candidate_move, broken_wall)

        candidate_move = p.coordinates

      #move validation
      if w.get_board_value(candidate_move) == broken_wall:
        w.set_board_value(candidate_move, grass)

      if w.get_board_value(candidate_move) == wall:
        candidate_move = p.coordinates

      if w.get_board_value(candidate_move) == placed_wall:
        candidate_move = p.coordinates

      if w.get_board_value(candidate_move) == flat_spike:
        w.set_board_value(candidate_move, grass)

      if w.get_board_value(candidate_move) == spike:
        if p.hammers > 0:
          p.hammers -= 1
          w.set_board_value(candidate_move, flat_spike)
          candidate_move = p.coordinates
        else:
          p.health -= 1

      if w.get_board_value(candidate_move) == chest:
        chest_loot = random.choices(loot, weights=loot_weights, k=1)
        if chest_loot == ["hammer"]:
          p.hammers += random.randint(1, 3)
        elif chest_loot == ["pickaxe"]:
          p.pickaxes += random.randint(1, 3)
        elif chest_loot == ["block"]:
          p.blocks += random.randint(1, 3)
        elif chest_loot == ["gold"]:
          p.gold += random.randint(1, 5)

        w.set_board_value(candidate_move, looted_chest)

      if w.get_board_value(candidate_move) == merchant:
        merchant_interaction(p)

      p.coordinates = candidate_move

    if p.health == 0:  #Death
      death(p, w)