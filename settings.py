class Settings:
    """Klasa przeznaczona do przechowywania wszystkich ustawień gry."""

    def __init__(self):
        """Inicjalizacja ustawień gry."""
        self.bg_color = (230, 230, 230)

        self.ship_limit = 2
        
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3
        
        self.fleet_drop_speed = 10

        self.speedup_scale = 1.1

        self.difficulty_level = 'medium'

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Inicjalizacja ustawień, które ulegają zmianie w trakcie gry."""
        if self.difficulty_level == 'easy':
            self.ship_limit = 4
            self.bullets_allowed = 7
            self.ship_speed = 0.75
            self.bullet_speed = 1.3
            self.alien_speed = 0.5
        elif self.difficulty_level == 'medium':
            self.ship_limit = 2
            self.bullets_allowed = 3
            self.ship_speed = 1.5
            self.bullet_speed = 3.0
            self.alien_speed = 1.0
        elif self.difficulty_level == 'hard':
            self.ship_limit = 0
            self.bullets_allowed = 3
            self.ship_speed = 3.0
            self.bullet_speed = 6.0
            self.alien_speed = 2.0

        self.fleet_direction = 1

    def increase_speed(self):
        """Zmiana ustawień dotyczących szybkości."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale