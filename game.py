import pygame
import random
import math
import os
from gameObject import GameObject
from player import Player
from enemy import Enemy


class SoundEffect:
    def __init__(self): 
        pygame.mixer.music.load('assets/background_music.mp3')
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
        self.popSound = pygame.mixer.Sound('assets/pop.wav')
        self.correctSound = pygame.mixer.Sound('assets/correct.wav')
        self.wrongSound = pygame.mixer.Sound('assets/wrong.wav')
        self.clickSound = pygame.mixer.Sound('assets/click.wav')
        self.levelUpSound = pygame.mixer.Sound('assets/levelup.wav')
        self.gameOverSound = pygame.mixer.Sound('assets/gameover.wav')
        self.backgroundMusic = pygame.mixer.Sound('assets/background_music.mp3')
        self.backgroundMusic.set_volume(0.5)
        self.backgroundMusic.play(-1)

    def play_sound(self, sound_name):
        if sound_name == 'pop':
            self.popSound.play()
        elif sound_name == 'correct':
            self.correctSound.play()
        elif sound_name == 'wrong':
            self.wrongSound.play()
        elif sound_name == 'click':
            self.clickSound.play()
        elif sound_name == 'levelup':
            self.levelUpSound.play()
        elif sound_name == 'gameover':
            self.gameOverSound.play()
        elif sound_name == 'background':
            self.backgroundMusic.play()

    def stop_sound(self, sound_name):
        if sound_name == 'background':
            self.backgroundMusic.stop()

class PowerUp(GameObject):
    def __init__(self, x, y, width, height, image_path, power_type, color):
        super().__init__(x, y, width, height, image_path)
        self.power_type = power_type   # "speed", "shield", "points"
        self.color = color
        self.active = True

class TreasureItem(GameObject):
    def __init__(self, x, y, width, height, image_path, item_type):
        super().__init__(x, y, width, height, image_path)
        self.item_type = item_type  # "gem", "coin", "crown"
        self.collected = False
        self.returned = False
        self.color = None  # Color to display (None = default)
        self.speed = random.choice([-4, -3, -2, 2, 3, 4])  # Move horizontally like enemy

    def move(self, max_width):
        self.x += self.speed
        if self.x <= 0:
            self.x = 0
            self.speed = abs(self.speed)
        elif self.x >= max_width - self.width:
            self.x = max_width - self.width
            self.speed = -abs(self.speed)

class MagicParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y)), int(self.size))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Game:
    
    def __init__(self):
        self.width = 800
        self.height = 800

        self.game_window = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        
        # Game state
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.power_up_active = False
        self.power_up_timer = 0
        
        # Level system
        self.current_level = 1
        self.level_completed = False
        self.level_start_time = 0
        
        # Time limit system (varies by level)
        self.base_time_limit = 7200  # 2 minutes base
        self.time_limit = self.base_time_limit
        self.time_remaining = self.time_limit
        
        # Magic effects
        self.magic_particles = []
        
        # Power-ups
        self.power_ups = []
        
        # Treasure system
        self.treasure_opened = False
        self.treasure_items = []
        self.items_collected = 0
        self.total_items = 5
        self.treasure_box = GameObject(375, 50, 50, 50, 'assets/chest.png')
        
        # Enemy system (varies by level)
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 180  # 3 seconds at 60 FPS
        self.max_enemies = 8  # Base max enemies
        self.enemy_speed_multiplier = 1.0  # Speed multiplier for enemies
        
        # Treasure item spawning system
        self.treasure_spawn_timer = 0
        self.treasure_spawn_delay = 600  # 10 seconds at 60 FPS
        self.max_treasure_items = 15  # Maximum treasure items on screen at once

        # Fixed image file paths to match actual files
        self.background = GameObject(0, 0, self.width, self.height, 'assets/background.png')
        self.player = Player(375, 700, 50, 50, 'assets/character.png', 10)
        
        # Initialize enemies
        self.enemies = []
        self.setup_level()
        
        # UI Buttons
        self.quit_button = Button(self.width - 120, 10, 100, 40, "QUIT", (200, 50, 50), (255, 100, 100))

    def setup_level(self):
        """Setup the current level with appropriate difficulty"""
        # Clear existing enemies and items
        self.enemies = []
        self.treasure_items = []
        self.treasure_opened = False
        self.items_collected = 0
        
        # Level-specific settings
        if self.current_level == 1:
            self.max_enemies = 6
            self.enemy_speed_multiplier = 1.0
            self.time_limit = self.base_time_limit
            self.total_items = 8  # Increased from 3
        elif self.current_level == 2:
            self.max_enemies = 8
            self.enemy_speed_multiplier = 1.2
            self.time_limit = int(self.base_time_limit * 0.9)  # 10% less time
            self.total_items = 12  # Increased from 4
        elif self.current_level == 3:
            self.max_enemies = 10
            self.enemy_speed_multiplier = 1.4
            self.time_limit = int(self.base_time_limit * 0.8)  # 20% less time
            self.total_items = 15  # Increased from 5
        elif self.current_level == 4:
            self.max_enemies = 12
            self.enemy_speed_multiplier = 1.6
            self.time_limit = int(self.base_time_limit * 0.7)  # 30% less time
            self.total_items = 18  # Increased from 6
        elif self.current_level == 5:
            self.max_enemies = 15
            self.enemy_speed_multiplier = 1.8
            self.time_limit = int(self.base_time_limit * 0.6)  # 40% less time
            self.total_items = 20  # Increased from 7
        else:  # Level 6+
            self.max_enemies = 15 + (self.current_level - 5) * 2
            self.enemy_speed_multiplier = 1.8 + (self.current_level - 5) * 0.2
            self.time_limit = max(1800, int(self.base_time_limit * (0.5 - (self.current_level - 5) * 0.05)))  # Minimum 30 seconds
            self.total_items = min(25, 20 + (self.current_level - 5) * 2)  # Increased max items
        
        # Reset time
        self.time_remaining = self.time_limit
        self.level_start_time = pygame.time.get_ticks()
        
        # Spawn initial enemies for this level
        self.spawn_enemies()
        
        # Clear power-ups and spawn new ones
        self.power_ups = []
        self.spawn_power_up()

    def spawn_magic_particles(self):
        """Spawn magic particles around the player"""
        if self.power_up_active:
            # Spawn particles around player
            for _ in range(3):  # Spawn 3 particles per frame
                x = self.player.x + random.randint(0, self.player.width)
                y = self.player.y + random.randint(0, self.player.height)
                
                # Use the current power-up color
                if hasattr(self, 'current_power_color'):
                    color = self.current_power_color
                else:
                    color = (255, 255, 255)  # White default
                
                particle = MagicParticle(x, y, color)
                self.magic_particles.append(particle)

    def update_magic_particles(self):
        """Update magic particles"""
        # Update existing particles
        for particle in self.magic_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.magic_particles.remove(particle)
        
        # Spawn new particles if power-up is active
        self.spawn_magic_particles()

    def draw_magic_particles(self):
        """Draw magic particles"""
        for particle in self.magic_particles:
            particle.draw(self.game_window)

    def spawn_enemies(self):
        """Spawn initial enemies based on current level"""
        # Base enemy positions
        base_positions = [
            (100, 200), (600, 300), (200, 400), (500, 150), (50, 500),
            (700, 250), (150, 350), (650, 450), (300, 100), (400, 600),
            (100, 300), (700, 400), (200, 200), (600, 500), (50, 400),
            (750, 150), (150, 600), (550, 250), (250, 550), (450, 300)
        ]
        
        # Spawn enemies based on level
        for i in range(min(self.max_enemies, len(base_positions))):
            x, y = base_positions[i]
            # Vary speed based on level
            base_speed = random.choice([-3, -2, 2, 3, 4])
            speed = int(base_speed * self.enemy_speed_multiplier)
            enemy = Enemy(x, y, 50, 50, 'assets/enemy.png', speed)
            self.enemies.append(enemy)

    def spawn_new_enemy(self):
        """Spawn a single new enemy at random position"""
        # Random position on the edges
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x = random.randint(50, self.width - 100)
            y = random.randint(50, 150)
        elif side == 'bottom':
            x = random.randint(50, self.width - 100)
            y = random.randint(650, 750)
        elif side == 'left':
            x = random.randint(50, 150)
            y = random.randint(100, self.height - 100)
        else:  # right
            x = random.randint(650, 750)
            y = random.randint(100, self.height - 100)
        
        # Random speed with level multiplier
        base_speed = random.choice([-4, -3, -2, 2, 3, 4])
        speed = int(base_speed * self.enemy_speed_multiplier)
        
        enemy = Enemy(x, y, 50, 50, 'assets/enemy.png', speed)
        self.enemies.append(enemy)

    def update_enemy_spawning(self):
        """Update enemy spawning system"""
        if len(self.enemies) < self.max_enemies:
            self.enemy_spawn_timer += 1
            # Faster spawning in higher levels
            spawn_delay = max(60, self.enemy_spawn_delay - (self.current_level - 1) * 20)
            if self.enemy_spawn_timer >= spawn_delay:
                self.spawn_new_enemy()
                self.enemy_spawn_timer = 0
                # Decrease spawn delay to make it more challenging
                self.enemy_spawn_delay = max(30, self.enemy_spawn_delay - 10)

    def open_treasure(self):
        """Open the treasure and scatter items"""
        if not self.treasure_opened:
            self.treasure_opened = True
            self.scatter_treasure_items()
            self.score += 100 * self.current_level  # Bonus scales with level

    def scatter_treasure_items(self):
        """Scatter treasure items around the map"""
        item_types = ["gem", "coin", "crown", "ruby", "emerald", "diamond", "sapphire", "gold"]
        
        for i in range(self.total_items):
            # More varied positioning - divide screen into more zones
            zone = i % 6  # 6 different zones
            
            if zone == 0:
                # Top-left area
                x = random.randint(50, 250)
                y = random.randint(50, 200)
            elif zone == 1:
                # Top-right area
                x = random.randint(550, 750)
                y = random.randint(50, 200)
            elif zone == 2:
                # Middle-left area
                x = random.randint(50, 250)
                y = random.randint(250, 400)
            elif zone == 3:
                # Middle-right area
                x = random.randint(550, 750)
                y = random.randint(250, 400)
            elif zone == 4:
                # Bottom-left area
                x = random.randint(50, 250)
                y = random.randint(450, 600)
            else:  # zone == 5
                # Bottom-right area
                x = random.randint(550, 750)
                y = random.randint(450, 600)
            
            # Add some random variation to avoid perfect grid
            x += random.randint(-20, 20)
            y += random.randint(-20, 20)
            
            # Ensure items stay within screen bounds
            x = max(50, min(x, self.width - 80))
            y = max(50, min(y, self.height - 80))
            
            item_type = item_types[i % len(item_types)]
            # Use different colored versions of enemy image for items (you can replace with actual item images)
            item = TreasureItem(x, y, 30, 30, 'assets/enemy.png', item_type)
            self.treasure_items.append(item)

    def spawn_power_up(self):
        """Spawn a new power-up at random location"""
        if len(self.power_ups) < 2:  # Max 2 power-ups at once
            x = random.randint(50, self.width - 100)
            y = random.randint(100, self.height - 100)
            power_type = random.choice(["speed", "shield", "points"])
            
            # Define the allowed colors for power-ups (including sky blue)
            allowed_colors = [
                (0, 0, 255),    # Blue
                (0, 255, 0),    # Green
                (255, 0, 0),    # Red
                (255, 255, 0),  # Yellow
                (255, 192, 203), # Pink
                (128, 0, 128),  # Purple
                (255, 255, 255), # White
                (255, 165, 0),  # Orange
                (0, 0, 0),      # Black
                (135, 206, 235) # Sky Blue
            ]
            
            color = random.choice(allowed_colors)
            
            # Use enemy image for power-ups (you can replace with actual power-up images)
            power_up = PowerUp(x, y, 30, 30, 'assets/enemy.png', power_type, color)
            self.power_ups.append(power_up)

    def check_collision(self, obj1, obj2):
        """Check collision between two objects"""
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)

    def check_enemy_collision(self):
        """Check collision between player and enemies"""
        for enemy in self.enemies[:]:  # Use slice to avoid modification during iteration
            if self.check_collision(self.player, enemy):
                if not self.power_up_active:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Reset player position
                        self.player.x = 375
                        self.player.y = 700
                else:
                    # Destroy enemy if shield is active
                    self.enemies.remove(enemy)
                    self.score += 50 * self.current_level  # Score scales with level
                    break

    def check_treasure_collision(self):
        """Check if player reached the treasure"""
        if self.check_collision(self.player, self.treasure_box):
            if not self.treasure_opened:
                self.open_treasure()
            elif self.items_collected == self.total_items:
                # All items returned to treasure box - level completed!
                self.level_completed = True
                self.score += 1000 * self.current_level  # Level completion bonus
                self.next_level()

    def next_level(self):
        """Advance to the next level"""
        self.current_level += 1
        self.level_completed = False
        self.setup_level()

    def check_treasure_item_collision(self):
        """Check collision between player and treasure items"""
        for item in self.treasure_items[:]:
            if not item.collected and self.check_collision(self.player, item):
                item.collected = True
                self.items_collected += 1
                self.score += 50 * self.current_level
                # Change item color to current power-up color if available
                if hasattr(self, 'current_power_color') and self.current_power_color:
                    item.color = self.current_power_color
                else:
                    item.color = (255, 255, 255)  # Default to white
                self.treasure_items.remove(item)
                # Optionally: keep item on screen for a moment to show color (not removed immediately)

    def check_power_up_collision(self):
        """Check collision between player and power-ups"""
        for power_up in self.power_ups[:]:
            if self.check_collision(self.player, power_up):
                self.current_power_type = power_up.power_type
                self.current_power_color = power_up.color
                if power_up.power_type == "speed":
                    self.player.speed += 5
                    self.power_up_active = True
                    self.power_up_timer = 300  # 5 seconds at 60 FPS
                elif power_up.power_type == "shield":
                    self.power_up_active = True
                    self.power_up_timer = 600  # 10 seconds at 60 FPS
                elif power_up.power_type == "points":
                    self.score += 200 * self.current_level  # Points scale with level
                
                self.power_ups.remove(power_up)

    def update_power_ups(self):
        """Update power-up timers and spawn new ones"""
        if self.power_up_active:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.power_up_active = False
                self.current_power_type = None
                self.current_power_color = None
                if self.player.speed > 10:  # Reset speed boost
                    self.player.speed = 10
        
        # Spawn new power-ups occasionally (more frequent in higher levels)
        spawn_chance = max(100, 300 - (self.current_level - 1) * 50)  # More frequent in higher levels
        if random.randint(1, spawn_chance) == 1:
            self.spawn_power_up()

    def update_time_limit(self):
        """Update time limit"""
        self.time_remaining -= 1
        if self.time_remaining <= 0:
            self.game_over = True

    def format_time(self, frames):
        """Convert frames to MM:SS format"""
        seconds = frames // 60
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def draw_objects(self):
        # Clear the screen completely first
        self.game_window.fill((0, 0, 0))
        
        # Draw background with proper scaling to fill the entire window
        self.game_window.blit(self.background.image, (0, 0))
        
        # Draw treasure box
        self.game_window.blit(self.treasure_box.image, (self.treasure_box.x, self.treasure_box.y))
        
        # Draw treasure items
        for item in self.treasure_items:
            if item.color:
                item_surface = pygame.Surface((item.width, item.height))
                item_surface.fill(item.color)
                self.game_window.blit(item_surface, (item.x, item.y))
            else:
                self.game_window.blit(item.image, (item.x, item.y))
        
        # Draw player
        self.game_window.blit(self.player.image, (self.player.x, self.player.y))
        
        # Draw magic particles around player
        self.draw_magic_particles()
        
        # Draw all enemies
        for enemy in self.enemies:
            self.game_window.blit(enemy.image, (enemy.x, enemy.y))
        
        # Draw power-ups with their colors
        for power_up in self.power_ups:
            # Create a colored surface for the power-up
            power_surface = pygame.Surface((power_up.width, power_up.height))
            power_surface.fill(power_up.color)
            self.game_window.blit(power_surface, (power_up.x, power_up.y))

        # Draw UI with semi-transparent background for better readability
        self.draw_ui()
        
        # Draw buttons
        self.quit_button.draw(self.game_window)

        pygame.display.update()

    def draw_ui(self):
        """Draw score, lives, and game over screen"""
        font = pygame.font.Font(None, 36)
        
        # Create a semi-transparent overlay for UI elements
        ui_surface = pygame.Surface((280, 270))
        ui_surface.set_alpha(180)  # Semi-transparent
        ui_surface.fill((0, 0, 0))  # Black background
        self.game_window.blit(ui_surface, (5, 5))
        
        # Level display
        level_text = font.render(f"Level: {self.current_level}", True, (255, 255, 0))
        self.game_window.blit(level_text, (10, 10))
        
        # Score with better contrast
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.game_window.blit(score_text, (10, 50))
        
        # Lives with better contrast
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.game_window.blit(lives_text, (10, 90))
        
        # Time remaining
        time_color = (255, 255, 255) if self.time_remaining > 600 else (255, 0, 0)  # Red when less than 10 seconds
        time_text = font.render(f"Time: {self.format_time(self.time_remaining)}", True, time_color)
        self.game_window.blit(time_text, (10, 130))
        
        # Enemy count
        enemy_text = font.render(f"Enemies: {len(self.enemies)}", True, (255, 255, 255))
        self.game_window.blit(enemy_text, (10, 170))
        
        # Treasure items collected
        if self.treasure_opened:
            items_text = font.render(f"Items: {self.items_collected}/{self.total_items}", True, (255, 255, 255))
            self.game_window.blit(items_text, (10, 210))
            
            if self.items_collected == self.total_items:
                return_text = font.render("Return to treasure!", True, (255, 255, 0))
                self.game_window.blit(return_text, (10, 250))
        else:
            objective_text = font.render("Touch treasure to open!", True, (255, 255, 0))
            self.game_window.blit(objective_text, (10, 210))
        
        # Power-up status
        if self.power_up_active:
            power_text = font.render("POWER-UP ACTIVE!", True, (255, 255, 0))
            self.game_window.blit(power_text, (10, 290))
        
        # Level completion message
        if self.level_completed:
            level_complete_font = pygame.font.Font(None, 48)
            level_text = level_complete_font.render(f"LEVEL {self.current_level - 1} COMPLETE!", True, (0, 255, 0))
            text_rect = level_text.get_rect(center=(self.width/2, self.height/2 - 50))
            self.game_window.blit(level_text, text_rect)
            
            next_text = font.render("Preparing next level...", True, (255, 255, 255))
            next_rect = next_text.get_rect(center=(self.width/2, self.height/2))
            self.game_window.blit(next_text, next_rect)
        
        # Game over screen with better visibility
        if self.game_over:
            # Create a semi-transparent overlay for game over screen
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.game_window.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 72)
            if self.lives <= 0:
                game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            elif self.time_remaining <= 0:
                game_over_text = game_over_font.render("TIME'S UP!", True, (255, 165, 0))
            else:
                game_over_text = game_over_font.render("YOU WIN!", True, (0, 255, 0))
            
            text_rect = game_over_text.get_rect(center=(self.width/2, self.height/2))
            self.game_window.blit(game_over_text, text_rect)
            
            final_score_text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            final_score_rect = final_score_text.get_rect(center=(self.width/2, self.height/2 + 30))
            self.game_window.blit(final_score_text, final_score_rect)
            
            restart_text = font.render("Press R to restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.width/2, self.height/2 + 60))
            self.game_window.blit(restart_text, restart_rect)
    
    def handle_input(self):
        """Handle keyboard input for player movement"""
        if self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.restart_game()
            return
        
        keys = pygame.key.get_pressed()
        
        # Horizontal movement (left/right)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_horizontal(-1, self.width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_horizontal(1, self.width)
        
        # Vertical movement (up/down)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_vertical(-1, self.height)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_vertical(1, self.height)
    
    def restart_game(self):
        """Restart the game"""
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.power_up_active = False
        self.power_up_timer = 0
        self.current_level = 1
        self.level_completed = False
        self.time_remaining = self.base_time_limit
        self.treasure_opened = False
        self.items_collected = 0
        self.treasure_items = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 180
        self.treasure_spawn_timer = 0
        self.treasure_spawn_delay = 600
        self.max_treasure_items = 15
        self.magic_particles = []
        
        self.player.x = 375
        self.player.y = 700
        self.player.speed = 10
        
        # Reset to level 1
        self.setup_level()
    
    def update_enemies(self):
        """Update all enemy and treasure item movements"""
        for enemy in self.enemies:
            enemy.move(self.width)
        for item in self.treasure_items:
            item.move(self.width)
        
    def spawn_additional_treasure(self):
        """Spawn additional treasure items during gameplay"""
        if len(self.treasure_items) < self.max_treasure_items and self.treasure_opened:
            self.treasure_spawn_timer += 1
            if self.treasure_spawn_timer >= self.treasure_spawn_delay:
                self.treasure_spawn_timer = 0
                
                # Spawn in random location
                x = random.randint(100, self.width - 130)
                y = random.randint(100, self.height - 130)
                
                item_types = ["gem", "coin", "crown", "ruby", "emerald", "diamond", "sapphire", "gold"]
                item_type = random.choice(item_types)
                
                item = TreasureItem(x, y, 30, 30, 'assets/enemy.png', item_type)
                self.treasure_items.append(item)
                
                # Increase total items count
                self.total_items += 1

    def update_treasure_spawning(self):
        """Update treasure item spawning"""
        self.spawn_additional_treasure()

    def run_game_loop(self):
        while True: 
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                
                # Handle quit button
                if self.quit_button.handle_event(event):
                    return

            # Handle input
            self.handle_input()
            
            # Update game state
            if not self.game_over and not self.level_completed:
                self.player.update()
                self.update_enemies()
                self.update_enemy_spawning()
                self.update_power_ups()
                self.update_time_limit()
                self.update_magic_particles()
                self.update_treasure_spawning()
                
                # Check collisions
                self.check_enemy_collision()
                self.check_treasure_collision()
                self.check_treasure_item_collision()
                self.check_power_up_collision()
                
                # Spawn magic particles
                self.spawn_magic_particles()
            
            # Draw everything
            self.draw_objects()
            
            # Control frame rate
            self.clock.tick(60)