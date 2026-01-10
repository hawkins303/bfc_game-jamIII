from ursina import *

# Define player entity
player = Entity(scale=.05, collider='box',
        move_dir=Vec3(0,0,0),   # Player movement direction
        speed = 0.5             # Player move speed
    )
p_sprite = SpriteSheetAnimation(parent=player, texture="/assets/nancy_sprite.png", tileset_size=[6,6], fps= 4,
                                animations={'idle': ((0, 5), (1, 5)), 'walk_down': ((0, 5), (3, 5)),
                                                       'walk_up': ((0, 4), (3, 4)), 'walk_left': ((0, 3), (3, 3)),
                                                       'walk_right': ((0, 2), (3, 2)), 'death':((0,1),(1,1))})



