import pygame
from game import Game

pygame.init()

# Play background music (simple, one file, no interruption)
try:
    pygame.mixer.init()
    pygame.mixer.music.load('assets/music/puppy no woof.mp3')
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)  # Loop indefinitely
except Exception as e:
    print(f"[WARNING] Could not play background music: {e}")

game = Game()
game.run_game_loop()

pygame.quit()
quit()