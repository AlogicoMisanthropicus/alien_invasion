import sys
from time import sleep
import json

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """
    Ogólna klasa przeznaczona do zarządzania zasobami i sposobem
    działania gry.
    """

    def __init__(self):
        """Inicjalizacja gry i utworzenie jej zasobów."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Inwazja obcych")

        #Utworzenie egzemplarza przeznaczonego do przechowywania danych
        #statystycznych gry oraz utworzenie egzemplarza klasy Scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        self.play_button = Button(self, "Gra")

        self._make_difficulty_buttons()

    def _make_difficulty_buttons(self):
        """Stworzenie przycisków pozwalających wybrać poziom trudności."""
        self.easy_button = Button(self, "Łatwy")
        self.medium_button = Button(self, "Średni")
        self.hard_button = Button(self, "Trudny")

        self.easy_button.rect.top = (
            self.play_button.rect.top + 1.5*self.play_button.rect.height)
        self.easy_button._update_msg_position()

        self.medium_button.rect.top = (
            self.easy_button.rect.top + 1.5*self.play_button.rect.height)
        self.medium_button._update_msg_position()

        self.hard_button.rect.top = (
            self.medium_button.rect.top + 1.5*self.play_button.rect.height)
        self.hard_button._update_msg_position()

    def run_game(self):
        """Rozpoczęcie pętli głównej gry."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """Reakcja na zdarzenia generowane przez klawiaturę i mysz."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_hscore()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_difficulty_buttons(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Rozpoczęcie nowej gry po kliknięciu przycisku Gra przez 
        użytkownika."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_game()

    def _check_difficulty_buttons(self, mouse_pos):
        """Ustawienie odpowiedniego poziomu trudności."""
        easy_button_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        medium_button_clicked = self.medium_button.rect.collidepoint(mouse_pos)
        hard_button_clicked = self.hard_button.rect.collidepoint(mouse_pos)

        if easy_button_clicked:
            self.settings.difficulty_level = 'easy'
        elif medium_button_clicked:
            self.settings.difficulty_level = 'medium'
        elif hard_button_clicked:
            self.settings.difficulty_level = 'hard'

    def _check_keydown_events(self, event):
        """Reakcja na zdarzenia klawiatura/mysz."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self.save_hscore()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_g and not self.stats.game_active:
            self._start_game()            
    def _check_keyup_events(self, event):
        """Reakcja na zwolnienie klawisza."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _start_game(self):
        """Rozpoczęcie gry."""
        self.settings.initialize_dynamic_settings()
        #Wyzerowanie danych statystycznych gry.
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        #Usunięcie zawartości listy aliens i bullets.
        self.aliens.empty()
        self.bullets.empty()

        #Utworzenie nowej floty i wyśrodkowanie statku.
        self._create_fleet()
        self.ship.center_ship()
        pygame.mouse.set_visible(False)

    def _fire_bullet(self):
        """Utworzenie nowego pocisku i dodanie go do grupy pocisków."""
        if len(self.bullets) < self.settings.bullets_allowed and (
            self.stats.game_active):
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Uaktualnienie położenia pocisków i usunięcie tych, które są 
        niewidoczne na ekranie."""
        #Uaktualnienie położenia pocisków.
        self.bullets.update()

        #Usunięcie pocisków, które znajdują się poza ekranem.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Reakcja na kolizję między pociskiem a obcym."""
        #Usunięcie wszystkich pocisków i obcych,
        # między którymi doszło do kolizji.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #Pozbycie się istniejących pocisków i utworzenie nowej floty.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #Inkrementacja numeru poziomu.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        Sprawdzenie, czy flota obcych znajduje się przy krawędzi, 
        a następnie uaktualnienie położenia wszystkich obcych w flocie.
        """
        self._check_fleet_edges()
        self.aliens.update()

        #Wykrywanie kolizji między obcym a statkiem.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Wyszukiwanie obcych docierających do dolnej krawędzi ekranu.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Utworzenie pełnej floty obcych."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #Ustalenie, ile rzędów obcych zmieści się na ekranie.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
            (3 * alien_height) - 2 * ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #Utworzenie pełnej floty obcych.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Utworzenie obcego i umieszczenie go w rzędzie."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Odpowiednia reakcja, gdy obcy dotrze do krawędzi ekranu."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _ship_hit(self):
        """Reakcja na uderzenie obcego w statek."""
        if self.stats.ships_left > 0:
            #Zmniejszenie wartości przechowywanej w ships_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Usunięcie zawartości list aliens i bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Utworzenie nowej floty i wypośrodkowanie statku.
            self._create_fleet()
            self.ship.center_ship()

            #Pauza.
            sleep(0.5)

        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Sprawdzenie, czy którykolwiek obcy dotarł do dolnej krawędzi 
        ekranu."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Tak samo, jak w przypadku zderzenia statku z obcym.
                self._ship_hit()
                break

    def _change_fleet_direction(self):
        """Przesunięcie całej floty w dół i zmiana kierunku, w którym się 
        ona porusza."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def save_hscore(self):
        """Zapis najlepszego wyniku w pliku."""
        filename = 'highscore.json'
        high_score = self.stats.high_score

        with open(filename, 'w') as f:
            json.dump(high_score, f)

    def _update_screen(self):
        """Uaktualnienie obrazów na ekranie i przejście do nowego ekranu."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Wyświetlenie informacji o punktacji.
        self.sb.show_score()

        #Wyświetlenie przycisków tylko wtedy, gdy gra jest nieaktywna.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.medium_button.draw_button()
            self.hard_button.draw_button()

        #Wyświetlenie ostatnio zmodyfikowanego ekranu.
        pygame.display.flip()

if __name__ == '__main__':
    #Utworzenie egzemplarza gry i jej uruchomienie.
    ai = AlienInvasion()
    ai.run_game()