import random
import time

from menu import menu
from blessed import Terminal
from colorama import Back, Fore
from replit import clear

from merchants import merchant

grave = f"{Fore.BLACK}☗ {Fore.WHITE}"
pyramid = f"{Fore.BLACK}╱╲{Fore.WHITE}"
home = f"{Fore.MAGENTA}⌂ {Fore.WHITE}"


chest = f"{Fore.YELLOW}[]{Fore.WHITE}"
shop = f"{Fore.YELLOW}ㅠ{Fore.WHITE}"

mineshaft = f"{Fore.YELLOW}⊓ {Fore.WHITE}"
exit = f"{Fore.YELLOW}⊔ {Fore.WHITE}"

door = f"{Fore.BLACK}∎ {Fore.WHITE}"
grass = f"{Fore.LIGHTGREEN_EX}~ {Fore.WHITE}"
stone_floor = f"{Fore.LIGHTBLACK_EX}~ {Fore.WHITE}"
house_floor = f"{Fore.LIGHTBLACK_EX}ㅡ{Fore.WHITE}"
x_block = f"{Fore.BLACK}x {Fore.WHITE}"
placed_x = f"{Fore.BLACK}X {Fore.WHITE}"
rock = f"{Fore.LIGHTBLACK_EX}▃ {Fore.WHITE}"
placed_rock = f"{Fore.LIGHTBLACK_EX}▄ {Fore.WHITE}"
broken_block = f"{Fore.BLACK}- {Fore.WHITE}"
spike = f"{Fore.RED}ㅅ{Fore.WHITE}"
flat_spike = f"{Fore.RED}ㅡ{Fore.WHITE}"
looted_chest = f"{Fore.YELLOW}[ {Fore.WHITE}"
heart = f"{Fore.RED}♡ {Fore.WHITE}"
ore = f"{Fore.YELLOW}◈ {Fore.WHITE}"
empty = "  "

loot = ["block", "gold", "hammer", "pickaxe", "heart"]
loot_weights = [1, 5, 1, 1, 0.5]

biomes = [
  [grass, empty, x_block, spike, chest, shop, grave, pyramid],#plains
  [grass, x_block, spike, chest, shop, grave],#dense forest
  [grass, spike, x_block, grave, empty],#graveyard
  [0,1,2]#all biomes
]

biome_weights = [
  [18, 2, 5, 1, 0.1, 0.01, 0.01, 0.005],#plains
  [1, 1, 1, 0.5, 0.005, 0.005],#dense forest
  [1, 0.5, 0.5, 0.5, 1],#graveyard
  [1, 0.5, 0.1]#all biomes
]

class Item:
  def __init__(self, name, number, value):
    self.name = name
    self.number = number
    self.value = value

class Inventory:
  def __init__(self, capacity):
    self._bag = [Item(None, 0, 0)] * capacity
    self._available = list(range(0, capacity))
    self._lookup = dict()


  def add_item(self, item):
    if item.name in self._lookup:
      self._bag[self._lookup[item.name]].number += item.number
    elif self._available:
      index = self._available.pop(0)
      self._bag[index] = item
      self._lookup[item.name] = index
    else:
      return False
    return True

  def remove_item(self, index):
    if self._bag[index].name is None:
      return None
    item = self._bag[index]
    if item.number > 0:
      self._bag[index].number -= 1
    if item.number == 0:
      self._bag[index] = Item(None, 0, 0)
      self._available.append(index)
      self._available.sort()
      self._lookup.pop(item.name)
    return item.name


class World:

  def __init__(self, choices, weights, radius, ground, mine_block, border):
    self.board = {
        (0, 0): mine_block,
        (random.choice([5, -5]), random.choice([5, -5])): shop,
    }
    self.radius = radius
    self.choices = choices
    self.weights = weights
    self.ground = ground
    self.border = border

  def get_visible_window(self, x, y, biome):
    visible = []
    for i in range(y - self.radius, y + self.radius + 1):
      row = []
      for j in range(x - self.radius, x + self.radius + 1):
        if self.border == 0 and self.ground == grass:
          biome_location = (round(i/20), round(j/20))
          if biome_location not in biome:
            
            biome[biome_location] = random.choices(biomes[-1], weights=biome_weights[-1], k=1)[0]
            
          self.choices = biomes[biome[biome_location]]
          self.weights = biome_weights[biome[biome_location]]


        if (i, j) not in self.board:
          if max(abs(i), abs(j)) > self.border and self.border != 0:
            block = x_block
          else:
            block = random.choices(self.choices, weights = self.weights, k=1)[0]
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

  def __init__(self, icon, coordinates, max_health=3, hammers=1, pickaxes=1, shovels=1):
    self.icon = icon
    self.coordinates = coordinates
    self.candidate_move = [0,0,0]
    self.direction = "N"
    self.max_health = max_health
    self.health = max_health
    self.hammers = hammers
    self.pickaxes = pickaxes
    self.shovels = shovels
    self.gold = 0
    self.home_coords = "NA"
    self.house = None
    self.structures = dict()
    self.struct_coords = None


def display(board, boardrange, players, layer):
  # board is a list of lists containing the environment that the current player can see
  # boardrange is a tuple of the rectangular range of the board that the player can see - i.e., ((-4,-4), (4,4)) for a board whose coordinates in both directions range from -4 to 4
  # players is a list of the active players
  for player in players:
    if boardrange[0][0] <= player.coordinates[0] <= boardrange[1][
        0] and boardrange[0][1] <= player.coordinates[1] <= boardrange[1][1]:
      board[player.coordinates[0] - 
            boardrange[0][0]][player.coordinates[1] -
                              boardrange[0][1]] = player.icon
  if layer == 0:
    for row in board:
      print("|" + Back.BLACK + "".join(row) + Back.RESET + "|")
  elif layer == 1:
    for row in board:
      print("|" + Back.LIGHTGREEN_EX + "".join(row) + Back.RESET + "|")


def center_to_range(center, radius):
  return ((center[0] - radius, center[1] - radius), (center[0] + radius,
                                                     center[1] + radius))


def death(p, w, board, g):
  clear()
  print(f"({p.coordinates[0]}, {p.coordinates[1] * -1})")
  print(f"GOLD: {p.gold}")
  print("HEALTH: " + heart * p.health + "X " * (p.max_health - p.health))
  print(f"SHOVELS: {p.shovels}")
  print(f"HAMMERS: {p.hammers}  PICKAXES: {p.pickaxes}")
  print("-" * (4 * w.radius + 4))
  display(board, center_to_range(p.coordinates, w.radius), [p], p.coordinates[2])
  print("-" * (4 * w.radius + 4))
  w = p.house if p.house is not None else g
  print("you died (x_x)")
  input("press enter to respawn")
  if p.house is None:
    w = p.house
    p.coordinates = [6,0]
  else:
    w = g
    p.coordinates = [0,0]
  p.health = p.max_health
  p.gold = 0
  p.direction = "N"
  p.pickaxes = round(p.pickaxes * 0.5) + 1
  p.hammers = round(p.hammers * 0.5) + 1



def game():
  i = Inventory(5)
  p = Player('ツ', coordinates=[0, 0, 1])
  u = World([x_block, empty, stone_floor, spike, ore, chest, shop, exit, rock],
            [4, 0.5, 1.5, 0.5, 0.5, 0.01, 0.005, 0.005, 1], 5, stone_floor, exit, 0)
  g = World(biomes[0], biome_weights[0], 7, grass, mineshaft, 0)
  w = g

  b = dict()
  b[(0,0)] = 0

  menu(p)

  while True:  #game loop      
    clear()

    board = w.get_visible_window(p.coordinates[0], p.coordinates[1], b)

    #prints out the full display
    print(f"({p.coordinates[0]},{p.coordinates[1]*-1}) {p.direction}")
    print(f"GOLD: {p.gold}")
    print("HEALTH: " + heart * p.health + "X " * (p.max_health - p.health))
    print(f"SHOVELS: {p.shovels}")
    print(f"HAMMERS: {p.hammers}  PICKAXES: {p.pickaxes}")
    print("-" * (4 * w.radius + 4))
    if board is not None:
      display(board, center_to_range(p.coordinates, w.radius), [p], p.coordinates[2])
    print("-" * (4 * w.radius + 4))
    print(f"{i._bag[0].name} {i._bag[1].name} {i._bag[2].name} {i._bag[3].name} {i._bag[4].name}")
    print(f"{i._bag[0].number} {i._bag[1].number} {i._bag[2].number} {i._bag[3].number} {i._bag[4].number}")

    time.sleep(0.2)

    with Terminal().cbreak():  #input detection and player movement

      print("")
      move = Terminal().inkey(timeout=60)
      p.candidate_move = p.coordinates.copy()

      if move == "w":
        p.direction = "N"
        p.candidate_move[1] -= 1
      elif move == "s":
        p.direction = "S"
        p.candidate_move[1] += 1
      elif move == "a":
        p.direction = "W"
        p.candidate_move[0] -= 1
      elif move == "d":
        p.direction = "E"
        p.candidate_move[0] += 1

      elif move == "1" or move == "2" or move == "3" or move == "4" or move == "5":

        if p.direction == "N":
          p.candidate_move[1] -= 1
        elif p.direction == "S":
          p.candidate_move[1] += 1
        elif p.direction == "W":
          p.candidate_move[0] -= 1
        elif p.direction == "E":
          p.candidate_move[0] += 1

        if w.get_board_value(p.candidate_move) == w.ground or w.get_board_value(p.candidate_move) == empty:


          if i._bag[int(move) - 1].name == "X-BLOCK":
            w.set_board_value(p.candidate_move, placed_x)

          if i._bag[int(move) - 1].name == "HOUSE":
            p.home_coords = p.candidate_move
            w.set_board_value(p.candidate_move, home)
            p.house = World([house_floor], [1], 6, house_floor, house_floor, 5)
            p.house.set_board_value([6,0], door)

          if i._bag[int(move) - 1].name == "ROCK":
            w.set_board_value(p.candidate_move, placed_rock)

          i.remove_item(int(move) - 1)


      elif move == "e":
        if w.get_board_value(p.candidate_move) == shop:
          merchant(p, i)

        elif w.get_board_value(p.candidate_move) == mineshaft:
          w = u
          p.candidate_move[2] = 0
          p.candidate_move[0] = round(p.coordinates[0] / 2)
          p.candidate_move[1] = round(p.coordinates[1] / 2)

          p.coordinates = p.candidate_move

        elif w.get_board_value(p.candidate_move) == exit:
          p.candidate_move[2] = 1
          p.candidate_move[0] *= 2
          p.candidate_move[1] *= 2
          p.coordinates = p.candidate_move
          g.set_board_value(p.candidate_move, mineshaft)
          w = g
          w.set_board_value([p.candidate_move[0], p.candidate_move[1] - 1], w.ground)
          w.set_board_value([p.candidate_move[0], p.candidate_move[1] + 1], w.ground)
          w.set_board_value([p.candidate_move[0] - 1, p.candidate_move[1]], w.ground)
          w.set_board_value([p.candidate_move[0] + 1, p.candidate_move[1]], w.ground)

        elif w.get_board_value(p.candidate_move) == chest:
          chest_loot = random.choices(loot, weights=loot_weights, k=1)
          if chest_loot == ["hammer"]:
            p.hammers += random.randint(1, 3)
          elif chest_loot == ["pickaxe"]:
            p.pickaxes += random.randint(1, 3)
          elif chest_loot == ["block"]:
            i.add_item(Item("X-BLOCK", random.randint(1, 3), 1))
          elif chest_loot == ["gold"]:
            p.gold += random.randint(1, 5)
          w.set_board_value(p.candidate_move, looted_chest)

        elif w.get_board_value(p.candidate_move) == grave and p.shovels > 0:
          p.shovels -= 1
          w.set_board_value(p.candidate_move, broken_block)
          if random.randint(1,100) > 80:
            i.add_item(Item("ARTIFACT", 1, 100))
          p.gold += random.randint(1,10)

        elif p.candidate_move == p.home_coords:
          w = p.house
          p.candidate_move = [6,0,1]
          p.coordinates = [6,0,1]
          p.struct_coords = p.home_coords

        elif w.get_board_value(p.candidate_move) == door:
          w = g
          p.candidate_move = p.struct_coords
          p.coordinates = p.struct_coords

        elif w.get_board_value(p.candidate_move) == pyramid:
          if tuple(p.candidate_move) in p.structures:
            w = p.structures[tuple(p.candidate_move)]
          else:
            p.structures[tuple(p.candidate_move)] = World([stone_floor, chest, x_block, placed_x, spike], [1, 0.5, 0.4, 0.1, 0.25], 6, stone_floor, stone_floor, 5)
            p.structures[tuple(p.candidate_move)].set_board_value([0,6], door)
            p.structures[tuple(p.candidate_move)].set_board_value([0,5], stone_floor)
          p.struct_coords = p.coordinates
          w = p.structures[tuple(p.candidate_move)]
          p.coordinates = [0,6,1]


      elif move == "q":  #breaking
        if p.direction == "N":
          p.candidate_move[1] -= 1
        elif p.direction == "S":
          p.candidate_move[1] += 1
        elif p.direction == "W":
          p.candidate_move[0] -= 1
        elif p.direction == "E":
          p.candidate_move[0] += 1

        if w.get_board_value(p.candidate_move) == placed_x:
          w.set_board_value(p.candidate_move, w.ground)
          i.add_item(Item("X-BLOCK", 1, 1))

        if w.get_board_value(p.candidate_move) == x_block and p.pickaxes > 0:
          p.pickaxes -= 1
          i.add_item(Item("X-BLOCK", random.randint(1, 5), 1))
          w.set_board_value(p.candidate_move, broken_block)

        if w.get_board_value(p.candidate_move) == ore:
          if p.pickaxes > 0:
            p.pickaxes -= 1
            p.gold += random.randint(1, 10)
          else:
            p.gold += 1
          w.set_board_value(p.candidate_move, w.ground)

        if w.get_board_value(p.candidate_move) == placed_rock:
          i.add_item(Item("ROCK", 1, 2))
          w.set_board_value(p.candidate_move, broken_block)

        if w.get_board_value(p.candidate_move) == rock and p.pickaxes > 0:
          p.pickaxes -= 1
          i.add_item(Item("ROCK", random.randint(1, 5), 2))
          w.set_board_value(p.candidate_move, broken_block)

        p.candidate_move = p.coordinates

      #move validation
      if move == "w" or move == "a" or move == "s" or move == "d":

        if w.get_board_value(p.candidate_move) == broken_block:
          w.set_board_value(p.candidate_move, w.ground)

        elif w.get_board_value(p.candidate_move) == x_block:
          p.candidate_move = p.coordinates

        elif w.get_board_value(p.candidate_move) == ore:
          p.candidate_move = p.coordinates
          w.set_board_value(p.candidate_move, w.ground)

        elif w.get_board_value(p.candidate_move) == placed_x:
          p.candidate_move = p.coordinates

        elif w.get_board_value(p.candidate_move) == flat_spike:
          w.set_board_value(p.candidate_move, w.ground)

        elif w.get_board_value(p.candidate_move) == spike:
          if p.hammers > 0:
            p.hammers -= 1
            w.set_board_value(p.candidate_move, flat_spike)
            p.candidate_move = p.coordinates
          else:
            p.health -= 1


        p.coordinates = p.candidate_move

    if p.health == 0:
      death(p, w, board, g)
      i._bag = [Item(None, 0, 0)] * 5
