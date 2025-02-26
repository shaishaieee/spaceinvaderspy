import pygame
import random

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Set up screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load assets
player_img = pygame.image.load("player.jpg")
enemy_img = pygame.image.load("enemy.jpg")
bullet_img = pygame.image.load("bullet.png")
master_enemy_img = pygame.image.load("master_enemy.jpg")

# Clock for frame rate
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


# Player Class
class Player:
    def __init__(self):
        self.image = pygame.transform.scale(player_img, (50, 50))
        self.x = WIDTH // 2 - 25
        self.y = HEIGHT - 70
        self.speed = 5
        self.health = 50

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - 50:
            self.x += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        health_text = font.render(f"Player HP: {self.health}", True, GREEN)
        screen.blit(health_text, (10, 40))

    def take_damage(self):
        self.health -= 1


# Enemy Class
class Enemy:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(enemy_img, (40, 40))
        self.x = x
        self.y = y
        self.speed = 3
        self.direction = 1

    def move(self):
        self.x += self.speed * self.direction
        if self.x >= WIDTH - 40 or self.x <= 0:
            self.direction *= -1
            self.y += 40

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


# Bullet Class
class Bullet:
    def __init__(self, x, y, speed=-7):
        self.image = pygame.transform.scale(bullet_img, (10, 20))
        self.x = x + 20
        self.y = y
        self.speed = speed
        self.active = True

    def move(self):
        self.y += self.speed
        if self.y < 0 or self.y > HEIGHT:
            self.active = False

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


# Master Enemy (Boss) Class
class MasterEnemy:
    def __init__(self):
        self.image = pygame.transform.scale(master_enemy_img, (100, 100))
        self.x = WIDTH // 2 - 50
        self.y = 50
        self.speed = 2
        self.health = 500
        self.direction = 1
        self.bullets = []

    def move(self):
        self.x += self.speed * self.direction
        if self.x >= WIDTH - 100 or self.x <= 0:
            self.direction *= -1

    def fire(self):
        if random.randint(1, 15) == 1:  # Boss fires randomly
            self.bullets.append(Bullet(self.x + 45, self.y + 90, speed=5))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        health_text = font.render(f"Boss HP: {self.health}", True, RED)
        screen.blit(health_text, (WIDTH - 220, 10))

    def take_damage(self):
        self.health -= 1


# Game Class
class SpaceInvaders:
    def __init__(self):
        self.player = Player()
        self.enemies = [Enemy(random.randint(50, WIDTH - 50), random.randint(50, 200)) for _ in range(5)]
        self.bullets = []
        self.enemy_count = 0
        self.master_enemy = None
        self.running = True

    def run(self):
        while self.running:
            screen.fill(BLACK)
            self.handle_events()
            self.update()
            self.draw()

            # Check Win/Loss conditions
            if self.master_enemy and self.master_enemy.health <= 0:
                self.display_message("YOU WIN!", f"Total Points: {self.enemy_count}")
                self.running = False

            if self.player.health <= 0:
                self.display_message("GAME OVER!", f"Total Points: {self.enemy_count}")
                self.running = False

            pygame.display.update()
            clock.tick(60)

    def handle_events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left")
        if keys[pygame.K_RIGHT]:
            self.player.move("right")
        if keys[pygame.K_SPACE]:
            self.bullets.append(Bullet(self.player.x, self.player.y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        for enemy in self.enemies:
            enemy.move()

        for bullet in self.bullets:
            bullet.move()

        # Check for collisions
        self.bullets = [b for b in self.bullets if b.active]
        for bullet in self.bullets:
            for enemy in self.enemies:
                if enemy.x < bullet.x < enemy.x + 40 and enemy.y < bullet.y < enemy.y + 40:
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.enemy_count += 1
                    self.enemies.append(Enemy(random.randint(50, WIDTH - 50), random.randint(50, 200)))
                    break

        # Handle Master Enemy
        if self.enemy_count >= 30:
            if not self.master_enemy:
                self.master_enemy = MasterEnemy()

            self.master_enemy.move()
            self.master_enemy.fire()

            # Boss bullets move down
            for bullet in self.master_enemy.bullets[:]:
                bullet.move()

                if (
                        self.player.x < bullet.x < self.player.x + 50
                        and self.player.y < bullet.y < self.player.y + 50
                ):
                    self.player.take_damage()
                    self.master_enemy.bullets.remove(bullet)

                if bullet.y > HEIGHT:
                    self.master_enemy.bullets.remove(bullet)

            # Check if player bullets hit boss
            for bullet in self.bullets:
                if self.master_enemy.x < bullet.x < self.master_enemy.x + 100 and self.master_enemy.y < bullet.y < self.master_enemy.y + 100:
                    self.master_enemy.take_damage()
                    self.bullets.remove(bullet)

    def draw(self):
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.bullets:
            bullet.draw()

        if self.master_enemy:
            self.master_enemy.draw()
            for bullet in self.master_enemy.bullets:
                bullet.draw()

        score_text = font.render(f"Enemies Defeated: {self.enemy_count}", True, WHITE)
        screen.blit(score_text, (10, 10))

    def display_message(self, message, subtext):
        screen.fill(BLACK)
        text = font.render(message, True, WHITE)
        subtext = font.render(subtext, True, WHITE)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        screen.blit(subtext, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
        pygame.display.update()
        pygame.time.delay(3000)


# Start the game
if __name__ == "__main__":
    game = SpaceInvaders()
    game.run()

    pygame.quit()
