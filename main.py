import pygame
import random
import math
import copy

# CLASS DEFINITION

class Map:
  """
  size: area of map
  edges: list containing tuples, where each tuple contains points corresponding to the corners of each edge
  area_remaining: uncaptured area left in the map
  complete: True if required percentage of area is captured, False otherwise
  """
  def __init__(self, size, init_edges, init_player, init_enemies):
    self.size = size
    self.edges = [init_edges]
    self.area_remaining = size*size
    self.init_player = init_player
    self.enemies = init_enemies
    self.complete = False

  def draw(self, surface):
    pygame.draw.polygon(surface, "beige", self.edges[0], 0)
    pygame.draw.lines(surface, "black", True, self.edges[0], 2)
    for edge in self.edges[1:]:
      pygame.draw.polygon(surface, "white", edge, 0)
      pygame.draw.lines(surface, "black", False, edge, 2)
    return

  def add_edge(self, edge):
    self.edges.append(edge)

class Player:
  """
  edge_type: which segment the player is on. 0 -> bottom, 1 -> left, 2 -> top, 3 -> right
  """
  def __init__(self, lives, x, y, vel_x, vel_y, starting_segment):
    self.lives = lives
    self.x = x
    self.y = y
    self.radius = 10
    self.vel_x = vel_x
    self.vel_y = vel_y
    self.incursion = False
    self.path = []
    self.segment = starting_segment
    self.horizontal = True if starting_segment in [0, 2] else False
    self.hitbox = pygame.Rect(x-10, y-10, 2*self.radius, 2*self.radius)

  def move(self, map_edges):
    current_edge = map_edges[0]
    min_x, max_x = 200, 400
    min_y, max_y = 200, 400

    #apply vel of 5 with bounds
    if self.incursion:
      #free movement
      self.x += self.vel_x * 5
      self.y += self.vel_y * 5
      self.path.append((self.x, self.y))  # Add position to path
      self.x = max(min_x, min(max_x, self.x))
      self.y = max(min_y, min(max_y, self.y))

      # Check if touching an edge
      for i in range(len(current_edge)):
        segment = (current_edge[i], current_edge[(i + 1) % len(current_edge)])
        if is_between((self.x, self.y), segment) and (self.x, self.y) != self.path[0]:  # Not the start point
          #print(f"Hit edge at {self.x, self.y} on segment {segment}")
          self.end_incursion(map_edges, segment)
          break
                
    else:
      if self.segment == 0 or self.segment == 2:  #Bottom or Top (horizontal)
        self.x += self.vel_x * 5
        if not is_between((self.x, self.y), (current_edge[self.segment], current_edge[(self.segment + 1) % 4])):
          self.y = max_y if self.segment == 0 else min_y
        if self.x <= min_x:
          self.x = min_x
          self.handle_corner(map_edges)
        elif self.x >= max_x:
          self.x = max_x
          self.handle_corner(map_edges)
      elif self.segment == 1 or self.segment == 3:  #Left or Right (vertical)
        self.y += self.vel_y * 5
        if not is_between((self.x, self.y), (current_edge[self.segment], current_edge[(self.segment + 1) % 4])):
          self.x = min_x if self.segment == 1 else max_x
        if self.y <= min_y:
          self.y = min_y
          self.handle_corner(map_edges)
        elif self.y >= max_y:
          self.y = max_y
          self.handle_corner(map_edges)
    self.hitbox = pygame.Rect(self.x-10, self.y-10, 2*self.radius, 2*self.radius)

  def handle_corner(self, map_edges):
    current_edge = map_edges[0]
    corners = current_edge

    #check which corner we're at and transition
    if self.x == corners[0][0] and self.y == corners[0][1]:  # (200, 400) - Bottom left or Left bottom
      if self.segment == 0 and self.vel_x < 0:  # Bottom to Left
        self.segment = 1
        self.horizontal = False
        self.vel_x = 0
        self.vel_y = 0
      if self.segment == 1 and self.vel_y > 0:  # Left to Bottom
        self.segment = 0
        self.horizontal = True
        self.vel_x = 0
        self.vel_y = 0
    if self.x == corners[3][0] and self.y == corners[3][1]:  # (400, 400) - Bottom right or Right bottom
        if self.segment == 0 and self.vel_x > 0:  # Bottom to Right
          self.segment = 3
          self.horizontal = False
          self.vel_x = 0
          self.vel_y = 0
        if self.segment == 3 and self.vel_y > 0:  # Right to Bottom
          self.segment = 0
          self.horizontal = True
          self.vel_x = 0
          self.vel_y = 0
    if self.x == corners[2][0] and self.y == corners[2][1]:  # (400, 200) - Right top or Top right
        if self.segment == 3 and self.vel_y < 0:  # Right to Top
          self.segment = 2
          self.horizontal = True
          self.vel_x = 0
          self.vel_y = 0
        if self.segment == 2 and self.vel_y > 0:  # Top to Right
          self.segment = 3
          self.horizontal = False
          self.vel_x = 0
          self.vel_y = 0
    if self.x == corners[1][0] and self.y == corners[1][1]:  # (200, 200) - Top left or Left top
        if self.segment == 2 and self.vel_x < 0:  # Top to Left
          self.segment = 1
          self.horizontal = False
          self.vel_x = 0
          self.vel_y = 0
        if self.segment == 1 and self.vel_y < 0:  # Left to Top
          self.segment = 2
          self.horizontal = True
          self.vel_x = 0
          self.vel_y = 0

  def end_incursion(self, map_edges, hit_segment):
    start_point = self.path[0]
    end_point = (self.x, self.y)
    self.incursion = False
    self.vel_x = 0
    self.vel_y = 0

    # Update segment based on hit edge
    current_edge = map_edges[0]
    for i in range(len(current_edge)):
      segment = (current_edge[i], current_edge[(i + 1) % len(current_edge)])
      if segment == hit_segment:
        self.segment = i
        self.horizontal = True if self.segment in [0, 2] else False
        break

    # Form new polygon
    new_edge = self.path.copy()
    start_idx = None
    end_idx = None
    for i, point in enumerate(current_edge):
      if point == start_point:
        start_idx = i
      if point == end_point:
        end_idx = i

    if start_idx is not None and end_idx is not None:
      if start_idx < end_idx:
          edge_points = current_edge[start_idx:end_idx + 1]
      else:
          edge_points = current_edge[start_idx:] + current_edge[:end_idx + 1]
      new_edge.extend(edge_points[1:])
    else:
      new_edge.append(start_point)

    map.add_edge(new_edge)
    self.path = []

  def draw(self, surface):
    pygame.draw.circle(surface, "forestgreen", (self.x, self.y), self.radius)

    if self.incursion and len(self.path) > 1:
      pygame.draw.lines(surface, "red", False, self.path, 2)

  def update(self, surface, map: Map, enemies):
    self.move(map.edges)
    if self.is_touching_enemy(enemies):
      self.lose_life()
    self.draw(surface)

  def start_incursion(self):
    pass
  
  def is_touching_enemy(self, enemies):
    if self.hitbox.collideobjects([enemy.hitbox for enemy in enemies]) == None:
      return False
    else: return True

  def is_touching_corner(self, corners):
    # Should check if the player has reach an intersection
    pass
  
  def lose_life(self):
    if self.lives > 0:
      self.lives -= 1


class Qix:
  def __init__(self, x, y, starting_segment):
    self.x = x
    self.y = y
    self.vel_x = 0
    self.vel_y = 0
    self.radius = 10
    self.segment = starting_segment
    self.horizontal = True if starting_segment in [0, 2] else False
    self.hitbox = pygame.Rect(x-self.radius, y-self.radius, 2*self.radius, 2*self.radius)

  def move(self):
    min_x, max_x = 200, 400
    min_y, max_y = 200, 400
    distance = 0

    if distance > 0:
      self.x += self.vel_x
      self.y += self.vel_y
    elif distance == 0:
      distance = int((random.random() + 1) * 60)
      direction = random.randint(1, 4)
      if direction == 1:
        self.vel_x = 1
      elif direction == 2:
        self.vel_x = -1
      elif direction == 3:
        self.vel_y = 1
      else: self.vel_y = -1
    self.hitbox = pygame.Rect(self.x-self.radius, self.y-self.radius, 2*self.radius, 2*self.radius)

  def draw(self, surface, player):
    self.move()
    pygame.draw.rect(surface, 'red', self.hitbox, 0)


class Sparc:
  def __init__(self, x, y, starting_segment):
    self.x = x
    self.y = y
    self.vel_x = 0
    self.vel_y = 0
    self.radius = 10
    self.segment = starting_segment
    self.horizontal = True if starting_segment in [0, 2] else False
    self.hitbox = pygame.Rect(x-self.radius, y-self.radius, 2*self.radius, 2*self.radius)
    self._speed = 1

  # Which direction to move (towards player or not)
  def is_chasing(self, player: Player):
    range = 100
    if math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2) <= range:
      if (player.x - self.x) == 0 and (player.y - self.y) == 0:
        return (0, 0)
      elif (player.x - self.x) == 0:
        return (0, (player.y - self.y) / abs(player.y - self.y))
      elif (player.y - self.y) == 0:
        return ((player.x - self.x) / abs(player.x - self.x), 0)
      else:
        return ((player.x - self.x) / abs(player.x - self.x), (player.y - self.y) / abs(player.y - self.y))
    else: return None

  def move(self, map_edges, player: Player):
    current_edge = map_edges[0]
    min_x, max_x = 200, 400
    min_y, max_y = 200, 400
    direction = self.is_chasing(player)

    if direction != None:
      self.vel_x = self._speed * direction[0]
      self.vel_y = self._speed * direction[1]

    if self.segment == 0 or self.segment == 2:  #Bottom or Top (horizontal)
      self.x += self.vel_x * self._speed
      if not is_between((self.x, self.y), (current_edge[self.segment], current_edge[(self.segment + 1) % 4])):
        self.y = max_y if self.segment == 0 else min_y
      if self.x <= min_x:
        self.x = min_x
        handle_corner(self, map_edges)
      elif self.x >= max_x:
        self.x = max_x
        handle_corner(self, map_edges)
    elif self.segment == 1 or self.segment == 3:  #Left or Right (vertical)
      self.y += self.vel_y * self._speed
      if not is_between((self.x, self.y), (current_edge[self.segment], current_edge[(self.segment + 1) % 4])):
        self.x = min_x if self.segment == 1 else max_x
      if self.y <= min_y:
        self.y = min_y
        handle_corner(self, map_edges)
      elif self.y >= max_y:
        self.y = max_y
        handle_corner(self, map_edges)
    self.hitbox = pygame.Rect(self.x-self.radius, self.y-self.radius, 2*self.radius, 2*self.radius)

  def draw(self, surface, player):
    self.move(map.edges, player)
    pygame.draw.rect(surface, 'purple', self.hitbox, 0)


# HELPER FUNCTIONS

def is_between(point, segment):
  # Sorry for the messy logic, the first if statements check if the x coords are all equal (lined up)
  # and the nested if, checks to see if the y coord of point is between that of the endpoints of segment
  # Similar thing except the other way around for the elif statement
  if point[0] == segment[0][0] and point[0] == segment[1][0]: 
    if point[1] <= max(segment[0][1], segment[1][1]) and point[1] >= min(segment[0][1], segment[1][1]):
      return True
    else: return False
  elif point[1] == segment[0][1] and point[1] == segment[1][1]: 
    if point[0] <= max(segment[0][0], segment[1][0]) and point[0] >= min(segment[0][0], segment[1][0]):
      return True
    else: return False
  else: return False


def handle_corner(player: Player, map_edges):
  current_edge = map_edges[0]
  corners = current_edge

  #check which corner we're at and transition
  if player.x == corners[0][0] and player.y == corners[0][1]:  # (200, 400) - Bottom left or Left bottom
    if player.segment == 0 and player.vel_x < 0:  # Bottom to Left
      player.segment = 1
      player.horizontal = False
      player.vel_x = 0
      player.vel_y = -1
    if player.segment == 1 and player.vel_y > 0:  # Left to Bottom
      player.segment = 0
      player.horizontal = True
      player.vel_x = 1
      player.vel_y = 0
  if player.x == corners[3][0] and player.y == corners[3][1]:  # (400, 400) - Bottom right or Right bottom
      if player.segment == 0 and player.vel_x > 0:  # Bottom to Right
        player.segment = 3
        player.horizontal = False
        player.vel_x = 0
        player.vel_y = -1
      if player.segment == 3 and player.vel_y > 0:  # Right to Bottom
        player.segment = 0
        player.horizontal = True
        player.vel_x = -1
        player.vel_y = 0
  if player.x == corners[2][0] and player.y == corners[2][1]:  # (400, 200) - Right top or Top right
      if player.segment == 3 and player.vel_y < 0:  # Right to Top
        player.segment = 2
        player.horizontal = True
        player.vel_x = -1
        player.vel_y = 0
      if player.segment == 2 and player.vel_y > 0:  # Top to Right
        player.segment = 3
        player.horizontal = False
        player.vel_x = 0
        player.vel_y = 1
  if player.x == corners[1][0] and player.y == corners[1][1]:  # (200, 200) - Top left or Left top
      if player.segment == 2 and player.vel_x < 0:  # Top to Left
        player.segment = 1
        player.horizontal = False
        player.vel_x = 0
        player.vel_y = 1
      if player.segment == 1 and player.vel_y < 0:  # Left to Top
        player.segment = 2
        player.horizontal = True
        player.vel_x = 1
        player.vel_y = 0

#---------------------------------------------------------------
def draw_start_screen(surface):
  surface.fill("white")
  title = font.render("Qix Game", True, "black")
  surface.blit(title, (600 // 2 - title.get_width() // 2, 100))
  instructions = [
      font.render("Use Arrow Keys to move", True, "black"),
      font.render("Press Spacebar to start incursion", True, "black"),
      font.render("Claim 50% of the field to win", True, "black")
  ]
  for i, line in enumerate(instructions):
      surface.blit(line, (600 // 2 - line.get_width() // 2, 200 + i * 40))

  button_rect = pygame.Rect(250, 400, 100, 50)
  pygame.draw.rect(surface, "forestgreen", button_rect)
  button_text = font.render("Start", True, "white")
  text_rect = button_text.get_rect(center=button_rect.center)
  surface.blit(button_text, text_rect)

  return button_rect

def draw_end_screen(surface):
  surface.fill("white")
  title = font.render("Game Over", True, "black")
  surface.blit(title, (600 // 2 - title.get_width() // 2, 100))

  button_rect = pygame.Rect(250, 400, 100, 50)
  pygame.draw.rect(surface, "forestgreen", button_rect)
  button_text = font.render("Play Again", True, "white")
  text_rect = button_text.get_rect(center=button_rect.center)
  surface.blit(button_text, text_rect)

  return button_rect

def draw_lives(surface, player):
  heart_icon = font.render("♥", True, "red")
  lives_text = font.render(f" {player.lives}", True, "black")
  surface.blit(heart_icon, (10, 10))
  surface.blit(lives_text, (30, 10))

def reset_level(level: int):
  map = copy.deepcopy(level_maps[level])
  player = map.init_player
  enemies = map.enemies
  return (map, player, enemies)

#--------------------------------------------------------------

# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True
game_state = "start"
# player = Player(300, 400, 0, 0, 0)
# enemies = [Qix(300, 300, 0), Sparc(300, 200, 2)]
# qix = Qix(300, 300, 0)
# sparc = Sparc(300, 200, 2)
level = 0
level_maps = [Map(100, ((200, 400), (200, 200), (400, 200), (400, 400)), Player(3, 300, 400, 0, 0, 0), [Qix(300, 300, 0), Sparc(300, 200, 2)]),
              Map(100, ((150, 450), (150, 150), (450, 150), (450, 450)), Player(3, 300, 450, 0, 0, 0), [Qix(300, 300, 0), Qix(200, 200, 0), Sparc(300, 150, 2)]),
              Map(100, ((100, 500), (100, 500), (500, 100), (500, 500)), Player(5, 300, 500, 0, 0, 0), [Qix(300, 300, 0), Qix(200, 200, 0), Sparc(300, 100, 2), Sparc(500, 300, 3)])]
map = copy.deepcopy(level_maps[level])
player = map.init_player
enemies = map.enemies
#map.add_edge(((250, 400), (250, 300), (350, 300), (350, 400)))
font = pygame.font.SysFont("Arial", 30)

while running:

  if player.lives <= 0:
    game_state = "over"
  # poll for events
  # pygame.QUIT event means the user clicked X to close your window
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "start":
      if start_button.collidepoint(event.pos):
        game_state = "playing"
    elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "over":
      if play_again_button.collidepoint(event.pos):
        map, player, enemies = reset_level(level)
        game_state = "playing"
    elif event.type == pygame.KEYDOWN and game_state == "playing": # if a key is pressed
      if player.incursion:
        if event.key == pygame.K_LEFT:
          player.vel_x = -1
        elif event.key == pygame.K_RIGHT:
          player.vel_x = 1
        elif event.key == pygame.K_UP:
          player.vel_y = -1
        elif event.key == pygame.K_DOWN:
          player.vel_y = 1
      else:
        if event.key == pygame.K_LEFT:
          player.vel_x = -1
        elif event.key == pygame.K_RIGHT:
          player.vel_x = 1
        elif event.key == pygame.K_UP:
          player.vel_y = -1
        elif event.key == pygame.K_DOWN:
          player.vel_y = 1
      if event.key == pygame.K_SPACE and not player.incursion:
        player.incursion = True
        player.path = [(player.x, player.y)]  # Start path at current position
      #test case for when player gets hit (press l)
      # elif event.type == pygame.KEYDOWN and game_state == "playing" and event.key == pygame.K_l:
      #   player.lose_life()
    elif event.type == pygame.KEYUP and game_state == "playing": 
      player.vel_x = 0
      player.vel_y = 0
    

  #----------------------------------------------------------
  # RENDER YOUR GAME HERE
  if game_state == "start":
    start_button = draw_start_screen(screen)
  elif game_state == "playing":
    screen.fill("white")
    map.draw(screen)
    player.update(screen, map, enemies)
    # print(player.is_touching_enemy(enemies))
    for enemy in enemies:
      enemy.draw(screen, player)
    draw_lives(screen, player)
  elif game_state == "over":
    play_again_button = draw_end_screen(screen)

#------------------------------------------------------------
  # pygame.draw.circle(screen, "red", (100, 100), 40)

  # flip() the display to put your work on screen
  pygame.display.flip()
  clock.tick(60)  # limits FPS to 60

pygame.quit()