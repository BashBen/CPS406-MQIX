import pygame


# CLASS DEFINITION

class Map:
  """
  size: area of map
  edges: list containing tuples, where each tuple contains points corresponding to the corners of each edge
  area_remaining: uncaptured area left in the map
  complete: True if required percentage of area is captured, False otherwise
  """
  def __init__(self, size, init_edges):
    self.size = size
    self.edges = [init_edges]
    self.area_remaining = size*size
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
  def __init__(self, x, y, vel_x, vel_y, starting_segment):
    self.lives = 3
    self.x = x
    self.y = y
    self.vel_x = vel_x
    self.vel_y = vel_y
    self.incursion = False
    self.segment = starting_segment
    self.horizontal = True

  def move(self):
    if self.horizontal:
      self.x += self.vel_x
    else: self.y += self.vel_y

  def draw(self, surface):
    self.move()
    pygame.draw.circle(surface, "forestgreen", (self.x, self.y), 10)

  def start_incursion(self):
    pass
  
  def is_touching_enemy(self, enemies):
    pass

  def is_touching_corner(self, corners):
    # Should check if the player has reach an intersection
    pass



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

player1 = Player(300, 400, 0, 0, 5)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True

while running:
  # poll for events
  # pygame.QUIT event means the user clicked X to close your window
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN and player1.vel_x == 0 and player1.vel_y == 0: # if a key is pressed, and velocity is already 0
      if event.key == pygame.K_LEFT:
        player1.vel_x = -1
      elif event.key == pygame.K_RIGHT:
        player1.vel_x = 1
      if event.key == pygame.K_UP:
        player1.vel_y = -1
      elif event.key == pygame.K_DOWN:
        player1.vel_y = 1
    else: 
      player1.vel_x = 0
      player1.vel_y = 0

  # fill the screen with a color to wipe away anything from last frame
  screen.fill("white")

  # RENDER YOUR GAME HERE
  map1 = Map(100, ((200, 400), (200, 200), (400, 200), (400, 400)))
  map1.add_edge(((250, 400), (250, 300), (350, 300), (350, 400)))

  map1.draw(screen)

  player1.draw(screen)
  # pygame.draw.circle(screen, "red", (100, 100), 40)

  # flip() the display to put your work on screen
  pygame.display.flip()

  clock.tick(60)  # limits FPS to 60

pygame.quit()