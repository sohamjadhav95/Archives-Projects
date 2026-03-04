import random
import time

# Constants for the simulation
GRID_SIZE = 10
INITIAL_PREDATORS = 3
INITIAL_SURVIVORS = 5
INITIAL_PLANTS = 10
ENERGY_LOSS_PER_TURN = 1
PLANT_GROWTH_RATE = 3  # Turns for plants to grow back

# Classes for entities
class LivingBeing:
    def __init__(self, x, y, energy, entity_type):
        self.x = x
        self.y = y
        self.energy = energy
        self.type = entity_type

    def move(self):
        self.x = (self.x + random.choice([-1, 0, 1])) % GRID_SIZE
        self.y = (self.y + random.choice([-1, 0, 1])) % GRID_SIZE

class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Initialize the grid and entities
def initialize_simulation():
    predators = [LivingBeing(random.randint(0, GRID_SIZE - 1),
                             random.randint(0, GRID_SIZE - 1), 10, "Predator")
                 for _ in range(INITIAL_PREDATORS)]
    survivors = [LivingBeing(random.randint(0, GRID_SIZE - 1),
                             random.randint(0, GRID_SIZE - 1), 10, "Survivor")
                 for _ in range(INITIAL_SURVIVORS)]
    plants = [Plant(random.randint(0, GRID_SIZE - 1),
                    random.randint(0, GRID_SIZE - 1))
              for _ in range(INITIAL_PLANTS)]
    return predators, survivors, plants

# Simulation logic
def simulate_turn(predators, survivors, plants):
    # Move predators and survivors
    for being in predators + survivors:
        being.move()
        being.energy -= ENERGY_LOSS_PER_TURN

    # Predators hunt survivors
    for predator in predators:
        for survivor in survivors:
            if predator.x == survivor.x and predator.y == survivor.y:
                predator.energy += survivor.energy
                survivors.remove(survivor)
                break

    # Survivors eat plants
    for survivor in survivors:
        for plant in plants:
            if survivor.x == plant.x and survivor.y == plant.y:
                survivor.energy += 5
                plants.remove(plant)
                break

    # Plants regrow
    if random.randint(1, PLANT_GROWTH_RATE) == 1:
        plants.append(Plant(random.randint(0, GRID_SIZE - 1),
                            random.randint(0, GRID_SIZE - 1)))

    # Remove entities with no energy
    predators = [p for p in predators if p.energy > 0]
    survivors = [s for s in survivors if s.energy > 0]

    return predators, survivors, plants

# Display the grid
def display_grid(predators, survivors, plants):
    grid = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for plant in plants:
        grid[plant.x][plant.y] = "P"
    for survivor in survivors:
        grid[survivor.x][survivor.y] = "S"
    for predator in predators:
        grid[predator.x][predator.y] = "X"
    for row in grid:
        print(" ".join(row))
    print()

# Main loop
def main():
    predators, survivors, plants = initialize_simulation()
    turn = 0

    while predators and survivors:
        print(f"Turn {turn}")
        display_grid(predators, survivors, plants)
        predators, survivors, plants = simulate_turn(predators, survivors, plants)
        time.sleep(1)  # Slow down the simulation for better viewing
        turn += 1

    print("Simulation ended!")
    if not predators:
        print("All predators have died.")
    if not survivors:
        print("All survivors have died.")

if __name__ == "__main__":
    main()
