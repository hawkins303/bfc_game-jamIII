from ursina import *

app = Ursina()

window.color = color.black
camera.orthographic = True
camera.fov = 1

player = Entity(model='circle', scale=.05, collider='box', move_dir=Vec3(0,0))

def unit_vector(vector):
    if distance(Vec3(0,0,0), vector) == 0:
        return Vec3(0,0,0)
    return vector / distance(Vec3(0,0,0), vector)

def update():
    player.move_dir = unit_vector(Vec3(held_keys['d'] - held_keys['a'], held_keys['w'] - held_keys['s'],0))
    player.position += player.move_dir * time.dt
    
    
app.run()
