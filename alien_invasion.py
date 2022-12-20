import sys
from time import sleep
import pygame

from settings import Settings
from game_stats import GameStats
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion():
    """Overall class to manage assets and behavior"""

    def __init__(self):
        """Initalizing the game and create game resources"""

        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        #Create an instance to store game statistics.
        self.stats = GameStats(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Make the play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Starting the mainloop for the game"""

        while True:
            self._check_events()
            self._update_screen()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            
    def _check_events(self):
        for event in pygame.event.get():
            #Watch for keyboard and mouse events
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Reset the game settings.
            self.settings.initialize_dynamic_settings()
            self.stats.game_active = True
            self.stats.reset_stats()

            #Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            #Hide the mouse cursor.
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        """Respond to keypresses"""
        if event.key == pygame.K_UP:
            #Move ship up
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            #Move ship down
            self.ship.moving_down = True  
        elif event.key == pygame.K_q:
            sys.exit()  
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        """Respond to key releases"""
        if event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _update_screen(self):
        """Update Images on the screen, and flip to the new screen"""
        #Redraw the screen during each pass of the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme() 
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()
            
        pygame.display.flip()

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
                if bullet.rect.right > self.settings.screen_width:
                    self.bullets.remove(bullet)

        #Check for any bullets that have hit aliens
        # If so, get rid of the bullet and the alien
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-allien collisions."""
        #Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        #Count Kills
        for collision in collisions:
            self.stats.deaths += 1

        if not self.aliens:
            #Destroy existing bullets and create new fleet
            self.bullets.empty
            self._create_fleet()
            self.settings.increase_speed()

    def _create_fleet(self):
        """Create the fleet of Aliens"""
        #Create first row of aliens
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_y = self.settings.screen_height - (2 * alien_height)
        number_aliens_y = available_space_y // (2 * alien_height)

        #Determine the number of rows of aliens that fit on the screen
        ship_width = self.ship.rect.width
        available_space_x = (self.settings.screen_width - (3 * alien_width) - ship_width)
        number_rows = available_space_x // (2 * alien_width)

        #Create full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_y):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
            #Create an alien and place it in the row
            alien = Alien(self)
            alien_width, alien_height = alien.rect.size
            alien.y = alien_height + 2 * alien_height * alien_number
            alien.rect.y = alien.y
            alien.rect.x = self.settings.screen_width -  2 * alien.rect.width * row_number
            self.aliens.add(alien)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update the positions of all aliens in the fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        #Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_left()


    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fllet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.x += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            #Decrement ships_left and count deaths
            self.stats.ships_left -= 1
            self.stats.deaths += 1

            #Get Rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            #Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_left(self):
        """Check if any aliens have reached the bottom:"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.left <= screen_rect.left:
                #Treat this the same as if the ship got hit
                self._ship_hit()
                break


if __name__ == '__main__':
    #Make a game instance and run the game
    ai = AlienInvasion()
    ai.run_game()