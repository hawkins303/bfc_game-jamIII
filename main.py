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
    Entity(position = Vec3(0.7, 0.0, 0.0), scale=Vec3(.01, 1.0, 1), model='quad', collider='box'),
    Entity(position = Vec3(-0.7, 0.0, 0.0), scale=Vec3(.01, 1.0, 1), model='quad', collider='box'),
    Entity(position = Vec3(0.0, 0.5, 0.0), scale=Vec3(1.4, 0.01, 1), model='quad', collider='box'),
    Entity(position = Vec3(0.0, -0.5, 0.0), scale=Vec3(1.4, 0.01, 1), model='quad', collider='box'),
]

def update():
    # Player logic
    player.move_dir = Vec3(held_keys['d'] - held_keys['a'], held_keys['w'] - held_keys['s'], 0).normalized()
    player.position += player.move_dir * player.speed * time.dt
    
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
            for wall in walls:
                hit_info = raycast(bullet.position, bullet.move_dir, ignore=(bullet,player), distance=bullet_speed, debug=False)
                if hit_info.hit:
                    bullet.move_dir = bullet.move_dir - 2 * (bullet.move_dir.dot(hit_info.normal)) * hit_info.normal

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

app.run()
