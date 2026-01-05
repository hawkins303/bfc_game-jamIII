from ursina import *
from enum import Enum

app = Ursina()

window.color = color.black
camera.orthographic = True
camera.fov = 1

# Define player entity
player = Entity(model='circle', scale=.05, collider='box', move_dir=Vec3(0,0,0))

class BulletState(Enum):
    INACTIVE = 0
    SHOOTING = 1
    DROPPED = 2

# Define bullet Entity
bullet = Entity(model='circle', scale=.01, collider='box', move_dir=Vec3(0,0,0), state=BulletState.INACTIVE)

# Wall entities
walls = [
    Entity(position = Vec3(0.05, 0.02, 0.0), scale=Vec3(.02, 0.1, 1), model='quad', collider='box')
]

def update():
    # Player logic
    player.move_dir = Vec3(held_keys['d'] - held_keys['a'], held_keys['w'] - held_keys['s'], 0).normalized()
    player.position += player.move_dir * time.dt
    
    # Handle bullet logic
    match(bullet.state):
        case BulletState.INACTIVE:
            pass
        case BulletState.SHOOTING:
            bullet.position += bullet.move_dir * time.dt

            # If bullet intersects a wall
            for wall in walls:
                hit_info = raycast(bullet.position, bullet.move_dir, ignore=(bullet,player), distance=.01, debug=False)
                if hit_info.hit:
                    print(hit_info.world_normal)
                    bullet.move_dir = bullet.move_dir - 2 * (bullet.move_dir.dot(hit_info.normal)) * hit_info.normal

            pass
        case BulletState.DROPPED:
            pass
            
def input(key):
    if key == "left mouse down":
        # Fire bullet
        bullet.state = BulletState.SHOOTING
        bullet.position = player.position
        bullet.move_dir = (mouse.position - player.position).normalized()

app.run()
