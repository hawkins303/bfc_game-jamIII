from ursina import *

class SoundCollection(Entity):
    def __init__(self):
        super().__init__()

        self.background_sound = Audio(
            'BFC-gj3_take3.wav',
            volume=3,
            volume_multiplier=.5,
            loop=True,
            autoplay=True
        )

        self.shoot_sound = Audio(
            'cartoon_gunshot.wav',
            volume=5,
            volume_multiplier=.5,
            loop=False,
            autoplay=False
        )

        self.reload_sound = Audio(
            'reload.wav',
            volume=5,
            volume_multiplier=.5,
            loop=False,
            autoplay=False
        )

        self.bullet_bounce_sound = Audio(
            'boing.wav',
            volume=5,
            volume_multiplier=.5,
            loop=False,
            autoplay=False
        )

        self.enemy_hit = Audio(
            'cartoon_hit1.wav',
            volume=5,
            volume_multiplier=.5,
            loop=False,
            autoplay=False
        )

        self.player_hit = Audio(
            'cartoon_hit2.wav',
            volume=5,
            volume_multiplier=.5,
            loop=False,
            autoplay=False
        )