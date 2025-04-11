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
    self.path = []
    self.segment = starting_segment
    self.horizontal = True if starting_segment in [0, 2] else False

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

    map1.add_edge(new_edge)
    self.path = []

  def draw(self, surface):
    self.move(map1.edges)
    pygame.draw.circle(surface, "forestgreen", (self.x, self.y), 10)

    if self.incursion and len(self.path) > 1:
      pygame.draw.lines(surface, "red", False, self.path, 2)

  def start_incursion(self):
    pass
  
  def is_touching_enemy(self, enemies):
    pass

  def is_touching_corner(self, corners):
    # Should check if the player has reach an intersection
    pass
  
  def lose_life(self):
    if self.lives > 0:
      self.lives -= 1


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

def draw_lives(surface, player):
  heart_icon = font.render("♥", True, "red")
  lives_text = font.render(f" {player.lives}", True, "black")
  surface.blit(heart_icon, (10, 10))
  surface.blit(lives_text, (30, 10))

#--------------------------------------------------------------

# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True
game_state = "start"
player1 = Player(300, 400, 0, 0, 0)
map1 = Map(100, ((200, 400), (200, 200), (400, 200), (400, 400)))
#map1.add_edge(((250, 400), (250, 300), (350, 300), (350, 400)))
font = pygame.font.SysFont("Arial", 30)

while running:
  # poll for events
  # pygame.QUIT event means the user clicked X to close your window
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "start":
      if start_button.collidepoint(event.pos):
        game_state = "playing"
    elif event.type == pygame.KEYDOWN and game_state == "playing": # if a key is pressed
      if player1.incursion:
        if event.key == pygame.K_LEFT:
          player1.vel_x = -1
        elif event.key == pygame.K_RIGHT:
          player1.vel_x = 1
        elif event.key == pygame.K_UP:
          player1.vel_y = -1
        elif event.key == pygame.K_DOWN:
          player1.vel_y = 1
      else:
        if event.key == pygame.K_LEFT:
          player1.vel_x = -1
        elif event.key == pygame.K_RIGHT:
          player1.vel_x = 1
        elif event.key == pygame.K_UP:
          player1.vel_y = -1
        elif event.key == pygame.K_DOWN:
          player1.vel_y = 1
      if event.key == pygame.K_SPACE and not player1.incursion:
        player1.incursion = True
        player1.path = [(player1.x, player1.y)]  # Start path at current position
      #test case for when player gets hit (press l)
      elif event.type == pygame.KEYDOWN and game_state == "playing" and event.key == pygame.K_l:
        player1.lose_life()
    elif event.type == pygame.KEYUP and game_state == "playing": 
      player1.vel_x = 0
      player1.vel_y = 0
    

  #----------------------------------------------------------
  # RENDER YOUR GAME HERE
  if game_state == "start":
    start_button = draw_start_screen(screen)
  elif game_state == "playing":
    screen.fill("white")
    map1.draw(screen)
    player1.draw(screen)
    draw_lives(screen, player1)

#------------------------------------------------------------
  # pygame.draw.circle(screen, "red", (100, 100), 40)

  # flip() the display to put your work on screen
  pygame.display.flip()
  clock.tick(60)  # limits FPS to 60

pygame.quit()