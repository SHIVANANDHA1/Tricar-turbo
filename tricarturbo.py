import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("TriCar-Turbo")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
VIBGYOR_COLORS = [
    (148, 0, 211),   # Violet
    (75, 0, 130),    # Indigo
    (0, 0, 255),     # Blue
    (0, 255, 0),     # Green
    (255, 255, 0),   # Yellow
    (255, 165, 0),   # Orange
    (255, 0, 0)      # Red
]

# Triangle properties
triangle_size = 20
triangle_speed = 10

# Initial triangle position
triangle_pos = [width // 2, height // 2]

# Create an AVL tree for the triangle vertices
class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.height = 1
        self.left = None
        self.right = None

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, root, key, value):
        if not root:
            return AVLNode(key, value)
        elif key < root.key:
            root.left = self.insert(root.left, key, value)
        else:
            root.right = self.insert(root.right, key, value)

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right))
        balance = self.get_balance(root)

        if balance > 1 and key < root.left.key:
            return self.right_rotate(root)
        if balance < -1 and key > root.right.key:
            return self.left_rotate(root)
        if balance > 1 and key > root.left.key:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and key < root.right.key:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def get_height(self, root):
        if not root:
            return 0
        return root.height

    def get_balance(self, root):
        if not root:
            return 0
        return self.get_height(root.left) - self.get_height(root.right)

    def search(self, root, key):
        if root is None or root.key == key:
            return root
        if key < root.key:
            return self.search(root.left, key)
        return self.search(root.right, key)

    def update(self, root, key, value):
        node = self.search(root, key)
        if node:
            node.value = value

# Create and initialize the triangle vertices in AVL tree
avl_tree = AVLTree()
initial_vertices = [
    (triangle_pos[0], triangle_pos[1] - triangle_size),  # Top
    (triangle_pos[0] - triangle_size, triangle_pos[1] + triangle_size),  # Bottom Left
    (triangle_pos[0] + triangle_size, triangle_pos[1] + triangle_size)  # Bottom Right
]

for i, vertex in enumerate(initial_vertices):
    avl_tree.root = avl_tree.insert(avl_tree.root, i, vertex)

# Function to update the position of the triangle and ensure it stays within screen boundaries
def update_triangle_position(vertices, dx, dy):
    # Calculate the bounding box of the triangle
    min_x = min(v[0] for v in vertices)
    max_x = max(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_y = max(v[1] for v in vertices)

    # Ensure triangle stays within the screen boundaries
    if min_x + dx < 0:
        dx = -min_x
    if max_x + dx > width:
        dx = width - max_x
    if min_y + dy < 0:
        dy = -min_y
    if max_y + dy > height:
        dy = height - max_y

    for i in range(len(vertices)):
        x, y = vertices[i]
        vertices[i] = (x + dx, y + dy)
        avl_tree.update(avl_tree.root, i, vertices[i])

# Obstacles
obstacle_size = 30
initial_obstacle_speed = 2
obstacles = []

def create_obstacle():
    x = random.randint(0, width - obstacle_size)
    y = 0
    color = generate_random_color()
    obstacles.append({'rect': pygame.Rect(x, y, obstacle_size, obstacle_size), 'color': color})

def move_obstacles():
    global obstacle_speed
    for obstacle in obstacles:
        obstacle['rect'].y += obstacle_speed

def draw_obstacles():
    for obstacle in obstacles:
        pygame.draw.rect(window, obstacle['color'], obstacle['rect'])

def check_collision(triangle_vertices, obstacle_rect):
    for vertex in triangle_vertices:
        if obstacle_rect.collidepoint(vertex):
            return True
    return False

# Scoring system
score = 0
highest_score = 0
font = pygame.font.SysFont(None, 36)

def display_scores(final_score, high_score):
    window.fill(BLACK)
    game_over_text = font.render('Game Over!', True, WHITE)
    score_text = font.render(f'Score: {final_score}', True, WHITE)
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    window.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 60))
    window.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2))
    window.blit(high_score_text, (width // 2 - high_score_text.get_width() // 2, height // 2 + 60))
    pygame.display.flip()
    pygame.time.wait(2000)

# Leaderboard integration
leaderboard_file = "leaderboard.txt"

def save_leaderboard(score):
    with open(leaderboard_file, "a") as file:
        file.write(f"{score}\n")

def load_leaderboard():
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as file:
            scores = file.readlines()
            scores = [int(s.strip()) for s in scores]
            return sorted(scores, reverse=True)[:5]  # Top 5 scores
    return []

def display_leaderboard():
    leaderboard = load_leaderboard()
    window.fill(BLACK)
    leaderboard_text = font.render('Leaderboard', True, WHITE)
    window.blit(leaderboard_text, (width // 2 - leaderboard_text.get_width() // 2, 100))

    for i, score in enumerate(leaderboard):
        score_text = font.render(f"{i + 1}. {score}", True, WHITE)
        window.blit(score_text, (width // 2 - score_text.get_width() // 2, 150 + i * 40))

    pygame.display.flip()
    pygame.time.wait(3000)

# Function to generate a random color
def generate_random_color():
    while True:
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        if color not in VIBGYOR_COLORS and color != BLACK:
            return color

# Skins based on score
skins = {
    0: WHITE,         # Default
    100: (255, 0, 0),  # Red
    200: (0, 255, 0),  # Green
    300: (0, 0, 255),  # Blue
    400: (255, 255, 0) # Yellow
}

def get_active_skin(score):
    # Get the highest skin unlocked based on the player's score
    unlocked_skins = [color for s, color in skins.items() if score >= s]
    return unlocked_skins[-1]  # Return the last (highest) unlocked skin

# Function to draw the triangle as a car with the active skin
def draw_triangle_as_car(vertices, score):
    # Get active skin based on score
    active_skin = get_active_skin(score)

    # Draw the triangular body
    pygame.draw.polygon(window, active_skin, vertices)

    # Draw wheels (circles) at the base corners
    wheel_radius = 5
    wheel_offset = 10
    wheel_color = BLACK

    pygame.draw.circle(window, wheel_color, (vertices[1][0], vertices[1][1] + wheel_offset), wheel_radius)
    pygame.draw.circle(window, wheel_color, (vertices[2][0], vertices[2][1] + wheel_offset), wheel_radius)

    # Draw a roof on top of the triangle
    base_center_x = (vertices[1][0] + vertices[2][0]) // 2
    base_center_y = (vertices[1][1] + vertices[2][1]) // 2
    roof_width = triangle_size
    roof_height = 10
    roof = [
        (base_center_x - roof_width // 2, base_center_y - triangle_size),
        (base_center_x + roof_width // 2, base_center_y - triangle_size),
        (base_center_x + roof_width // 2, base_center_y - triangle_size - roof_height),
        (base_center_x - roof_width // 2, base_center_y - triangle_size - roof_height)
    ]
    pygame.draw.polygon(window, BLACK, roof)

    # Draw car windows on the roof
    window_width = roof_width // 2
    window_height = roof_height // 2
    window_rect = pygame.Rect(
        base_center_x - window_width // 2,
        base_center_y - triangle_size - window_height,
        window_width,
        window_height
    )
    pygame.draw.rect(window, BLUE, window_rect)

# Game variables
running = True
clock = pygame.time.Clock()
obstacle_speed = initial_obstacle_speed
game_active = True
background_color_index = 0  # Index for VIBGYOR cycling
color_change_interval = 30  # Frame interval to change color

# Game loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not game_active:
                game_active = True
                score = 0
                obstacle_speed = initial_obstacle_speed
                obstacles.clear()

    if game_active:
        keys = pygame.key.get_pressed()

        # Update triangle position
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -triangle_speed
        if keys[pygame.K_RIGHT]:
            dx = triangle_speed
        if keys[pygame.K_UP]:
            dy = -triangle_speed
        if keys[pygame.K_DOWN]:
            dy = triangle_speed

        vertices = [
            avl_tree.root.left.value,
            avl_tree.root.value,
            avl_tree.root.right.value
        ]
        update_triangle_position(vertices, dx, dy)

        # Draw background with dynamic color
        window.fill(VIBGYOR_COLORS[background_color_index])

        # Draw triangle as car with active skin
        draw_triangle_as_car(vertices, score)

        # Create and move obstacles
        if random.randint(0, 30) == 0:
            create_obstacle()

        move_obstacles()
        draw_obstacles()

        # Check for collision
        collision = any(check_collision(vertices, obstacle['rect']) for obstacle in obstacles)
        if collision:
            game_active = False
            highest_score = max(highest_score, score)
            display_scores(score, highest_score)
            save_leaderboard(score)

        # Increase score as time passes
        score += 1

        # Increase obstacle speed over time
        obstacle_speed = initial_obstacle_speed + score // 100  # Speed increases every 100 points

        # Change background color based on the frame count
        if score % color_change_interval == 0:
            background_color_index = (background_color_index + 1) % len(VIBGYOR_COLORS)

        # Draw live score
        score_text = font.render(f'Score: {score}', True, WHITE)
        window.blit(score_text, (10, 10))

    else:
        display_leaderboard()

    # Update display
    pygame.display.update()

    # Frame rate
    clock.tick(30)

# Quit Pygame
pygame.quit()
