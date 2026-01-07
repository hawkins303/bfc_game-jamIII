from ursina import *
from enum import Enum

app = Ursina()

window.color = color.black
camera.orthographic = True
camera.fov = 1

# Define player entity
player = Entity(model='circle', scale=.05, collider='box',
        move_dir=Vec3(0,0,0),   # Player movement direction
        speed = 0.5             # Player move speed
    )

class BulletState(Enum):
    HELD = 0
    SHOOTING = 1
    DROPPED = 2

# Define bullet Entity
bullet = Entity(model='circle', scale=.01, collider='box',
        move_dir=Vec3(0,0,0),   # Bullet movement direction
        TOTAL_TIME = 2.0,       # Time until the bullet stops
        bullet_timer = 0.0,     # Time the bullet has been active
        speed = 2.0,            # Bullet speed
        state=BulletState.HELD  # Bullet state
    )

# Wall entities
walls = [
    Entity(position = Vec3(0.0, 0.5, 0.0), scale=Vec3(1.4, 0.05, 1), color=color.blue, model='quad', collider='box'),
    Entity(position = Vec3(0.0, -0.5, 0.0), scale=Vec3(1.4, 0.05, 1),color=color.blue, model='quad', collider='box'),
    Entity(position = Vec3(0.7, 0.0, 0.0), scale=Vec3(.05, 1.0, 1), model='quad', collider='box'),
    Entity(position = Vec3(-0.7, 0.0, 0.0), scale=Vec3(.05, 1.0, 1), model='quad', collider='box'),
]

def update():
    # Player logic
    player.move_dir = Vec3(held_keys['d'] - held_keys['a'], held_keys['w'] - held_keys['s'], 0).normalized()
    player_speed = player.speed * time.dt

    # Player collision for walls
    if abs(player.move_dir.x) + abs(player.move_dir.y) != 0.0:
        player_collision_done = False
        wall_ignore_list = [bullet, player]
        while not player_collision_done:
            hit_info = raycast(origin=player.position, direction=player.move_dir, distance=player_speed, ignore=wall_ignore_list, debug=False)
            if hit_info.hit:
                vec_from_p = player.move_dir * player_speed
                vec_a = -player.move_dir * (player_speed - hit_info.distance)
                vec_b = hit_info.normal
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
            hit_info = raycast(bullet.position, bullet.move_dir, ignore=(bullet,player), distance=bullet_speed, debug=False)
            if hit_info.hit:
                bullet.move_dir = bullet.move_dir - 2 * (bullet.move_dir.dot(hit_info.normal)) * hit_info.normal
		
		#when bullet hits objects, that are not enemies
                ting = Entity(name='ting_parent', model='circle', scale=Vec3(.1, .1, 0))
                tingText = Text(text='TING', origin=(0, 0))
                ting.position = bullet.position
                tingText.position = bullet.position
                tingText.color = color.red
                ting.fade_out(duration=.2)
                tingText.fade_out(duration=.2)

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

def input(key):
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

app.run()
