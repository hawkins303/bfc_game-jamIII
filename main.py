from gc import disable

from direct.distributed.DistributedSmoothNode import globalActivateSmoothing
from panda3d.interrogatedb import interrogate_type_number_of_enum_values
from ursina import *
from enum import Enum

import player
from player import *
from sound_collection import SoundCollection

app = Ursina()
sounds = SoundCollection()
startTitle = Entity(model="quad", texture="/assets/title.png",disabled=True,position=Vec3(0,0,-3), scale=(1.5,.9,1))
endTitle = Entity(model="quad", texture="/assets/game_over.png",disabled=True,position=Vec3(0,0,-3), scale=(1.5,.9,1))
endTitle.disable()
floor = Entity(model="quad",texture="/assets/floor.png", position=Vec3(0,0,5))
window.color = color.black
camera.orthographic = True
camera.fov = 1
speed = .5

gameover_sequence = Sequence(
    1,                              # wait 1 second
    endTitle.enable,
    loop=False
)



gameover = False

class BulletState(Enum):
    HELD = 0
    SHOOTING = 1
    DROPPED = 2

# Define bullet Entity
bullet = Entity(model='circle', scale=.01,collider='box',
        move_dir=Vec3(0,0,0),   # Bullet movement direction
        TOTAL_TIME = 2.0,       # Time until the bullet stops
        bullet_timer = 0.0,     # Time the bullet has been active
        speed = 2.0,            # Bullet speed
        state=BulletState.HELD  # Bullet state
    )


# Define enemy entity
class EnemyMovePattern(Enum):
    HLINE = 1  # travel back and forth on a horizontal line
    VLINE = 5  # travel back and forth on a vertical line
    BOX = 0  # travel in a box pattern
    FOLLOW = 2  # follow towards the player position


class Enemy(Entity):
    def __init__(self, position, name, pattern, starting_direction,movement_distance):
        Entity.__init__(self)

        self.entity = Entity(scale=.05, disabled=True, collider='sphere',
                             mov_dir=Vec3(0, 0, 0),  # Unit movement direction
                             speed=0.4,  # Unit speed
                             color=color.gray,
                             position=position,  # Unit current position
                             starting_position=position,  # Unit starting position
                             name=name,  # unit name, just in case
                             pattern=pattern,  # Pathing placeholder
                             starting_direction=starting_direction,  # initial movement
                             movement_distance=movement_distance    # how far to move from spawn point, if applicable
                             )


# Add enemies here by giving them
# a spawning poing Vector
# a placeholder name that is probably not neccesary
# a pattern from the EnemyMovePattern Enum
# a starting Vector so it knows which way to begin moving in
enemy_list = [
    #Enemy(position=Vec3(0.1, 0.1, 0.0), name="thing1",pattern=EnemyMovePattern.HLINE,starting_direction=Vec3(0.0, 0.0, 0.0),movement_distance=.5),
    Enemy(position=Vec3(-0.1, 0.1, 0.0), name="thing1", pattern=EnemyMovePattern.HLINE, starting_direction=Vec3(1.0, 0.0, 0.0), movement_distance=.5),
    Enemy(position=Vec3(0.1, -0.1, 0.0), name="thing2", pattern=EnemyMovePattern.VLINE, starting_direction=Vec3(0.0, 1.0, 0.0), movement_distance=.5)
    # Enemy(position=Vec3(-0.2, -0.1, 0.0), name="thing3", pattern=EnemyMovePattern.BOX, starting_direction=Vec3(1.0, 0.0, 0.0))
]

# now for some adjustments per enemy entity that couldn't work inside the class init
for enemy in enemy_list:
    enemy.entity.collider = SphereCollider(enemy, radius=.8)  # adjust colliders
    enemy.entity.speed += random.randrange(0, 5) * 0.05  # tweak the speed to be randomish per enemy
    r_sprite = SpriteSheetAnimation(parent=enemy.entity, texture="/assets/robot_sprite_walk1.png", autoplay=True,tileset_size=[4, 5], fps=2,
                                    animations={'idle': ((0, 4), (3, 4)), 'walk_down': ((0, 4), (3, 4)),
                                                'walk_up': ((0, 3), (3, 3)), 'walk_left': ((0, 2), (3, 2)),
                                               'walk_right': ((0, 1), (3, 1)), 'death':((0,0),(1, 0))})
    r_sprite.play_animation('idle')

# Wall entities
walls = [
    Entity(position = Vec3(0.0, 0.5, 0.0), scale=Vec3(1.4, 0.05, 1), model='quad', collider='box'),
    Entity(position = Vec3(0.0, -0.5, 0.0), scale=Vec3(1.4, 0.05, 1), model='quad', collider='box'),
    Entity(position = Vec3(0.7, 0.0, 0.0), scale=Vec3(.05, 1.0, 1), model='quad', collider='box'),
    Entity(position = Vec3(-0.7, 0.0, 0.0), scale=Vec3(.05, 1.0, 1), model='quad', collider='box'),
    
    Entity(position = Vec3(-0.56, 0.2, 0.0), scale=Vec3(0.2, 0.05, 1), model='quad', collider='box'),
    Entity(position = Vec3(0.6, 0.1, 0.0), scale=Vec3(0.05, .15, 1), model='quad', collider='box'),
    Entity(position = Vec3(-0.3, -0.3, 0.0), rotation=Vec3(0, 0, -10), scale=Vec3(0.05, .15, 1), model='quad', collider='box'),
    Entity(position = Vec3(0.4, -0.4, 0.0), rotation=Vec3(0, 0, 45), scale=Vec3(0.05, .15, 1), model='quad', collider='box'),
]

sounds.background_sound.play(start=0)

def enemy_wall_collision(enemy, enemy_speed):
    # this might be busted
    # i copy pasted this from the player collision and renamed some variables
    # it was working at one point, but now i'm not sure
    # if the enemy is set to follow the player the enemy entity kinda freaks out when it hits a wall, it probably needs to update the direction
    if abs(enemy.move_dir.x) + abs(enemy.move_dir.y) != 0.0:
        enemy_collision_done = False
        wall_ignore_list = [bullet, player, enemy]
        while not enemy_collision_done:
            hit_info = raycast(origin=enemy.position, direction=enemy.move_dir, distance=enemy_speed,
                               ignore=wall_ignore_list, debug=False)
            if hit_info.hit:
                vec_from_p = enemy.move_dir * enemy_speed
                vec_a = -enemy.move_dir * (enemy_speed - hit_info.distance)
                vec_b = hit_info.world_normal
                # Skip colliding with inside of walls
                if vec_a.dot(vec_b) >= 0:
                    proj_a_to_b = vec_a.dot(vec_b) * vec_b

                    target_vec = vec_from_p + proj_a_to_b
                    # if proj_a_to_b.x + proj_a_to_b.y == 0:
                    # Add a bumper zone for the wall
                    target_vec -= target_vec.normalized() * 0.01

                    enemy.move_dir = target_vec.normalized()
                    enemy_speed = distance(Vec3(0, 0, 0), target_vec)
                wall_ignore_list.append(hit_info.entity)
            else:
                enemy_collision_done = True


def update_enemy(enemy):
    global gameover
    # enemy movement logic

    # set move direction and speed per enemy unit
    # depending on the movement pattern they have defined
    match enemy.pattern:
        case EnemyMovePattern.HLINE:

            enemy.move_dir = enemy.starting_direction
            # compare current and starting positions
            # if it moves too far one way, reverse and head back the other way
            if abs(enemy.x) > abs(enemy.starting_position.x + .5):
                enemy.move_dir.x = -enemy.move_dir.x # Reverse direction

            enemy_speed = enemy.speed * time.dt

        case EnemyMovePattern.VLINE:
            enemy.move_dir = enemy.starting_direction

            # compare current and starting positions
            if abs(enemy.y) > abs(enemy.starting_position.y + .5):
                enemy.move_dir.y = -enemy.move_dir.y  # Reverse direction
            enemy_speed = enemy.speed * time.dt

        case EnemyMovePattern.BOX:
            # this one isn't working right, might be easier to make this logic move in a circle or something
            enemy.move_dir = enemy.starting_direction
            # compare current and starting positions
            if abs(enemy.x) > abs(enemy.starting_position.x + .5):
                enemy.rotation_y -= time.dt * 100
            if abs(enemy.y) > abs(enemy.starting_position.y + .5):
                enemy.rotation_x -= time.dt * 100
            enemy_speed = enemy.speed * time.dt

        case EnemyMovePattern.FOLLOW:
            # find where player is and begin moving in that direction
            # this logic isn't working super effectively but it...kinda works
            enemy.move_dir = player.position.normalized()
            enemy_speed = enemy.speed * time.dt

    # enemy bullet collision
    if enemy.intersects(bullet) and bullet.state == BulletState.SHOOTING:
        sounds.enemy_hit.play()
        # Guess I'll die
        enemy.collider = None
        enemy.speed = 0.0
        r_sprite.play_animation('death')

    # enemy player collision
    if enemy.intersects(player) and enemy.enabled:
        # Game over man, game over
        sounds.player_hit.play() # this repeats a bunch because i haven't figured out better logic
        gameover = True
        p_sprite.play_animation('death')
       # endTitle.enable()
        gameover_sequence.start()


    # enemy wall collision
    #enemy_wall_collision(enemy, enemy_speed)

    # Move enemy
    enemy.position += enemy.move_dir * enemy_speed


def update():
    global startingGame
    if startingGame:
        startTitle.enable()
        if held_keys["enter"]:
            startingGame = False
            startTitle.disable()
            for enemy in enemy_list:
                enemy.entity.enable()      
        return
        
    if gameover:
        return


    # Player logic
    player.move_dir = Vec3(held_keys['d'] - held_keys['a'], held_keys['w'] - held_keys['s'], 0).normalized()
    player_speed = player.speed * time.dt
    # n_robs = 3
    # for r in range(n_robs):
    #     enemy_list.append(enemy.entity)
    # Player collision for walls
    if abs(player.move_dir.x) + abs(player.move_dir.y) != 0.0:
        player_collision_done = False
        wall_ignore_list = [bullet, player]
        while not player_collision_done:
            hit_info = raycast(origin=player.position, direction=player.move_dir, distance=player_speed, ignore=wall_ignore_list, debug=False)
            if hit_info.hit:
                vec_from_p = player.move_dir * player_speed
                vec_a = -player.move_dir * (player_speed - hit_info.distance)
                vec_b = hit_info.world_normal
                # Skip colliding with inside of walls
                if vec_a.dot(vec_b) >= 0:

                    proj_a_to_b = vec_a.dot(vec_b) * vec_b

                    target_vec = vec_from_p + proj_a_to_b
                    # if proj_a_to_b.x + proj_a_to_b.y == 0:
                    # Add a bumper zone for the wall
                    target_vec -= target_vec.normalized() * 0.001

                    player.move_dir = target_vec.normalized()
                    player_speed = distance(Vec3(0,0,0), target_vec)
                wall_ignore_list.append(hit_info.entity)
            else:
                player_collision_done = True

        # Move player
        player.position += player.move_dir * player_speed

    # Handle bullet logic
    match(bullet.state):
        case BulletState.HELD:
            # Bullet is being held, make invisible
            bullet.color = color.clear
        case BulletState.SHOOTING:

            bullet.color = color.white
            # Reduce speed over time
            bullet_speed = bullet.speed * (bullet.bullet_timer / bullet.TOTAL_TIME) * time.dt

            # Bounce bullet off walls
            hit_info = raycast(bullet.position,
                               bullet.move_dir,
                               ignore=[bullet,player],
                               distance=bullet_speed,
                               debug=False)
            if hit_info.hit:
                bullet.move_dir = bullet.move_dir - 2 * (bullet.move_dir.dot(hit_info.world_normal)) * hit_info.world_normal

                #when bullet hits objects, that are not enemies
                ting = Entity(name='ting_parent', model='circle', scale=Vec3(.1, .1, 0))
                tingText = Text(text='TING', origin=(0, 0))
                ting.position = bullet.position
                tingText.position = bullet.position
                tingText.color = color.red
                ting.fade_out(duration=.2)
                tingText.fade_out(duration=.2)
                sounds.bullet_bounce_sound.play()

            bullet.position += bullet.move_dir * bullet_speed

            # When time runs out, drop the bullet
            bullet.bullet_timer -= time.dt
            if (bullet.bullet_timer <= 0.0):
                bullet.state = BulletState.DROPPED
        case BulletState.DROPPED:
            bullet.color = color.white
            if bullet.intersects(player).hit:
                # Player picks up bullet
                bullet.state = BulletState.HELD
                sounds.reload_sound.play()
    
    for enemy in enemy_list:
        update_enemy(enemy.entity)
        
def input(key):
    if startingGame or gameover: return

    if key == "left mouse down":
        # Fire bullet
        if bullet.state == BulletState.HELD:
            bullet.state = BulletState.SHOOTING
            bullet.position = player.position
            bullet.move_dir = (mouse.position - player.position).normalized()
            bullet.bullet_timer = bullet.TOTAL_TIME

       # bang sound effect bubble
            bang = Entity(name='bang_parent', model='circle', scale=Vec3(.1, .1, 0), origin=(.5, .5))
            bangText = Text(text='BANG', origin=(.75,1.75))
            bang.enable()
            bangText.enable()
            bang.position = bullet.position
            bangText.position =bullet.position
            bangText.color = color.red
            bang.fade_out(duration=.2)
            bangText.fade_out(duration=.2)
            sounds.shoot_sound.play()

    if key == False:
        p_sprite.play_animation('idle')
    if key == 'd':
        p_sprite.play_animation('walk_right')
    if key == 's':
        p_sprite.play_animation('walk_down')
    if key == 'a':
        p_sprite.play_animation('walk_left')
    if key == 'w':
        p_sprite.play_animation('walk_up')

startingGame = True
app.run()
