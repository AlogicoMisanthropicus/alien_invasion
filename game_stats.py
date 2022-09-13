import json

class GameStats:
    """Monitorowanie danych statystycznych w grze "Inwazja obcych"."""

    def __init__(self, ai_game):
        """Inicjalizacja danych statystycznych."""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = self.load_hscore()

    def reset_stats(self):
        """
        Inicjalizacja danych statystycznych, które mogą zmieniać się 
        w trakcie gry.
        """
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def load_hscore(self):
        """Wczytuje najwyższy wynik z pliku."""
        filename = 'highscore.json'
        try:
            with open(filename) as f:
                hscore = json.load(f)
        except FileNotFoundError:
            return 0
        else:
            return hscore