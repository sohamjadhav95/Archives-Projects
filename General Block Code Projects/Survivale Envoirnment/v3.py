import pygame
import numpy as np
import random
import math
from pygame import gfxdraw

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
COLORS = {
    'background': (40, 45, 52),
    'panel': (55, 62, 71),
    'text': (238, 238, 238),
    'prey': (76, 175, 80),
    'predator': (244, 67, 54),
    'plant': (46, 125, 50),
    'food': (255, 193, 7)
}

class EnhancedNeuralNetwork:
    def __init__(self, input_size=7, hidden_size=8, output_size=2, parent=None):
        if parent:
            self.weights1 = parent.weights1 + np.random.normal(0, 0.1, (input_size, hidden_size))
            self.weights2 = parent.weights2 + np.random.normal(0, 0.1, (hidden_size, output_size))
        else:
            self.weights1 = np.random.randn(input_size, hidden_size) * 0.1
            self.weights2 = np.random.randn(hidden_size, output_size) * 0.1
            
    def predict(self, inputs):
        hidden = np.tanh(np.dot(inputs, self.weights1))
        outputs = np.tanh(np.dot(hidden, self.weights2))
        return outputs * 2  # Increase movement range

class Creature:
    def __init__(self, x, y, color, energy=150):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.energy = energy
        self.max_energy = 200
        self.vision_range = 150
        self.speed = 1.5
        self.age = 0
        
    def draw_vision(self, screen):
        for angle in np.linspace(-np.pi/2, np.pi/2, 5):
            end = self.pos + pygame.Vector2(math.cos(angle) * self.vision_range, 
                                          math.sin(angle) * self.vision_range)
            gfxdraw.line(screen, int(self.pos.x), int(self.pos.y), 
                        int(end.x), int(end.y), (255, 255, 255, 50))

class Predator(Creature):
    def __init__(self, x, y, nn=None):
        super().__init__(x, y, COLORS['predator'], 200)
        self.nn = nn if nn else EnhancedNeuralNetwork()
        self.attack_strength = 0.8
        self.energy_cost = 0.4
        
    def update(self, dt, entities):
        inputs = self.get_senses(entities)
        outputs = self.nn.predict(inputs)
        
        # Movement
        direction = pygame.Vector2(outputs[0], outputs[1]).normalize()
        self.pos += direction * self.speed * dt
        self.energy -= self.energy_cost * dt
        
        # Aging
        self.age += dt
        if self.age > 30 and self.energy > self.max_energy * 0.8:
            self.reproduce(entities)
        
        self.check_bounds()
        
    def get_senses(self, entities):
        # [Nearest prey distance, nearest food distance, energy level, ...]
        senses = []
        # Vision implementation here
        return np.array(senses)

class Prey(Creature):
    def __init__(self, x, y, nn=None):
        super().__init__(x, y, COLORS['prey'], 100)
        self.nn = nn if nn else EnhancedNeuralNetwork()
        self.energy_cost = 0.2
        
    def update(self, dt, entities):
        # Similar update logic with plant sensing
        pass

class Ecosystem:
    def __init__(self):
        self.predators = [Predator(random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
                         for _ in range(15)]
        self.preys = [Prey(random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
                     for _ in range(50)]
        self.plants = [Plant(random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
                      for _ in range(100)]
        self.foods = []
        
        # Statistics
        self.stats = {
            'prey_population': [],
            'predator_population': [],
            'food_quantity': [],
            'plant_count': []
        }

class SimulationUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.ecosystem = Ecosystem()
        self.font = pygame.font.Font(None, 24)
        self.smoothing = 0.9  # UI animation smoothing factor
        
        # UI State
        self.ui_elements = {
            'prey_population': {'value': 0, 'target': 0},
            'predator_population': {'value': 0, 'target': 0},
            'food_quantity': {'value': 0, 'target': 0},
            'plant_count': {'value': 0, 'target': 0}
        }
        
    def draw_panel(self):
        panel_rect = pygame.Rect(20, 20, 300, 160)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect, 0, 10)
        
        # Title
        title = self.font.render("Ecosystem Dashboard", True, COLORS['text'])
        self.screen.blit(title, (panel_rect.x + 15, panel_rect.y + 15))
        
        # Statistics Grid
        stats = [
            ("Prey Population", self.ui_elements['prey_population']['value']),
            ("Predator Population", self.ui_elements['predator_population']['value']),
            ("Food Quantity", self.ui_elements['food_quantity']['value']),
            ("Plant Count", self.ui_elements['plant_count']['value'])
        ]
        
        y_offset = 60
        for label, value in stats:
            text = self.font.render(f"{label}: {int(value)}", True, COLORS['text'])
            self.screen.blit(text, (panel_rect.x + 20, panel_rect.y + y_offset))
            y_offset += 30
            
    def update_ui_elements(self):
        # Smooth transitions for UI values
        for key in self.ui_elements:
            current = self.ui_elements[key]['value']
            target = self.ui_elements[key]['target']
            self.ui_elements[key]['value'] = current * self.smoothing + target * (1 - self.smoothing)
            
    def run(self):
        running = True
        dt = 0
        
        while running:
            # Update targets for UI
            self.ui_elements['prey_population']['target'] = len(self.ecosystem.preys)
            self.ui_elements['predator_population']['target'] = len(self.ecosystem.predators)
            self.ui_elements['food_quantity']['target'] = len(self.ecosystem.foods)
            self.ui_elements['plant_count']['target'] = len(self.ecosystem.plants)
            
            # Update UI elements with smoothing
            self.update_ui_elements()
            
            # Drawing
            self.screen.fill(COLORS['background'])
            
            # Draw entities
            for plant in self.ecosystem.plants:
                plant.draw(self.screen)
                
            for food in self.ecosystem.foods:
                food.draw(self.screen)
                
            for prey in self.ecosystem.preys:
                prey.draw(self.screen)
                if pygame.time.get_ticks() % 5 == 0:
                    prey.draw_vision(self.screen)
                    
            for predator in self.ecosystem.predators:
                predator.draw(self.screen)
                if pygame.time.get_ticks() % 5 == 0:
                    predator.draw_vision(self.screen)
            
            # Draw UI panel
            self.draw_panel()
            
            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

if __name__ == "__main__":
    ui = SimulationUI()
    ui.run()