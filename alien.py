import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """A class to represent a single alien in the fleet"""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        #Load the alien image and set its rect attribute
        self.image = pygame.image.load("images/rick-sanchez_pixelart.bmp")
        self.image = pygame.transform.scale(self.image, (65, 75))
        self.rect = self.image.get_rect()

        #Start each new alien near the top right of the screen
        self.rect.topright = self.screen_rect.topright
        #self.rect.x = self.rect.width
        #self.rect.y = self.rect.height
       

        #Store the alien's exact vertical position
        self.y = float(self.rect.y)

    def update(self):
        """Move the alien down or up"""
        self.y -= self.settings.alien_speed * self.settings.fleet_direction
        self.rect.y = self.y

    def check_edges(self):
        """Return True if alien is at edge of screen"""
        screen_rect = self.screen.get_rect()
        if self.rect.bottom >= screen_rect.bottom or self.rect.top <= 0:
            return True
