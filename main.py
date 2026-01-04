from ursina import *
from enum import Enum

app = Ursina()

window.color = color.black
camera.orthographic = True
camera.fov = 1

player = Entity(model='circle', scale=.05, collider='box', move_dir=Vec3(0,0,0))

class BulletState(Enum):
    INACTIVE = 0
    SHOOTING = 1
    DROPPED = 2

bullet = Entity(model='circle', scale=.01, collider='box', move_dir=Vec3(0,0,0), state=BulletState.INACTIVE)

# Return a vector's unit vector
def unit_vector(vector):
    if distance(Vec3(0,0,0), vector) == 0:
        return Vec3(0,0,0)
    return vector / distance(Vec3(0,0), vector)

def update():
    # Player logic
    player.move_dir = unit_vector(Vec3(held_keys['d'] - held_keys['a'], held_keys['w'] - held_keys['s'], 0))
    player.position += player.move_dir * time.dt
    
    # Handle bullet logic
    match(bullet.state):
        case BulletState.INACTIVE:
            pass
        case BulletState.SHOOTING:
            bullet.position += bullet.move_dir * time.dt
            pass
        case BulletState.DROPPED:
            pass
            
def input(key):
    if key == "left mouse down":
        # Fire bullet
        bullet.state = BulletState.SHOOTING
        bullet.position = player.position
        bullet.move_dir = unit_vector(mouse.position - player.position)

app.run()
