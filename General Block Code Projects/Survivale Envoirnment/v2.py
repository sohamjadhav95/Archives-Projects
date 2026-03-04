import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Survival AI Simulation")

# Colors
BACKGROUND_COLOR = (30, 30, 30)
PREDATOR_COLOR = (255, 50, 50)
PREY_COLOR = (50, 150, 255)
FOOD_COLOR = (50, 255, 50)
STAT_TEXT_COLOR = (255, 255, 255)
MINIMAP_COLOR = (50, 50, 50)

# Fonts
font = pygame.font.SysFont("Arial", 20)

# FPS
CLOCK = pygame.time.Clock()
FPS = 60

# Entity class
class Entity:
    def __init__(self, x, y, color, speed):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.color = color
        self.speed = speed

    def set_target(self, target_x, target_y):
        """Set a new target position for the entity."""
        self.target_x = target_x
        self.target_y = target_y

    def move(self):
        """Smoothly move towards the target position."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance > 1:
            # Normalize direction and move by speed
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, screen):
        """Draw the entity on the screen."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 8)

# Create entities
def create_entities(count, color, speed):
    return [
        Entity(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), color, speed)
        for _ in range(count)
    ]

# Draw population stats
def draw_stats(screen, prey_count, predator_count, food_count):
    stats = [
        f"Prey Population: {prey_count}",
        f"Predator Population: {predator_count}",
        f"Food Quantity: {food_count}",
    ]
    for i, stat in enumerate(stats):
        text_surface = font.render(stat, True, STAT_TEXT_COLOR)
        screen.blit(text_surface, (SCREEN_WIDTH - 200, 20 + i * 30))

# Draw mini-map
def draw_mini_map(screen, entities, width=200, height=150):
    mini_map_x = SCREEN_WIDTH - width - 10
    mini_map_y = 10
    pygame.draw.rect(screen, MINIMAP_COLOR, (mini_map_x, mini_map_y, width, height))

    for entity in entities:
        mini_x = int((entity.x / SCREEN_WIDTH) * width)
        mini_y = int((entity.y / SCREEN_HEIGHT) * height)
        pygame.draw.circle(screen, entity.color, (mini_map_x + mini_x, mini_map_y + mini_y), 3)

# Update entity targets
def update_targets(entities):
    for entity in entities:
        if random.random() < 0.01:  # Occasionally set a new target
            entity.set_target(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

# Main simulation function
def main():
    # Initialize entities
    predators = create_entities(10, PREDATOR_COLOR, 2)
    prey = create_entities(20, PREY_COLOR, 1.5)
    food = create_entities(30, FOOD_COLOR, 0)  # Food doesn't move

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update targets and move entities
        update_targets(predators + prey)
        for entity in predators + prey:
            entity.move()

        # Draw entities
        for entity in predators + prey + food:
            entity.draw(screen)

        # Draw stats and mini-map
        draw_stats(screen, len(prey), len(predators), len(food))
        draw_mini_map(screen, predators + prey + food)

        # Update display and clock
        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
