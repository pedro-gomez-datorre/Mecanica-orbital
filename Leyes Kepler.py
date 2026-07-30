import py5
import math, time
 
# ---------------- Physics ----------------
 
GM = 20000.0          # Gravitational parameter
PLANET_RADIUS = 40.0
START_HEIGHT = 180.0
PHYSICS_STEPS = 10
DT = 0.01
 
planet = None
pos = None
vel = None
trail = []
launched = False
crash_timer = 0 

def reset():
    global pos, vel, launched, trail
 
    pos = py5.Py5Vector(
        planet.x,
        planet.y - (PLANET_RADIUS + START_HEIGHT)
    )
    vel = py5.Py5Vector(0, 0)
    trail = []
    launched = False
 
 
def settings():
    py5.size(800, 800)
 
 
def setup():
    global planet
 
    planet = py5.Py5Vector(py5.width / 2, py5.height / 2)
    reset()
 
 
def draw():
    global pos, vel, launched, crash_timer, a

    a = py5.Py5Vector(0, 0)
    
    if crash_timer > 0:
        crash_timer -= 1
        if crash_timer == 0:
            reset()
 
    py5.background(20)
 
    # Planet
    py5.no_stroke()
    py5.fill(70, 120, 255)
    py5.circle(planet.x, planet.y, 2 * PLANET_RADIUS)
 
    if launched and crash_timer == 0:
        for _ in range(PHYSICS_STEPS):
            r = planet - pos
            d = r.mag
    
            # Collision
            if d < PLANET_RADIUS:
                crash_timer = 60
                launched = False
                break
    
            # Gravity
            a = r * (GM / d**3)
    
            vel += a * DT
            pos += vel * DT
    
            trail.append((pos.x, pos.y))
            if len(trail) > 6000:
                trail.pop(0)

            #Vector Velocidad
            py5.stroke(0,255,0)
            py5.line(pos.x, pos.y, pos.x+vel.x*15, pos.y+vel.y*15)

            #Vector Gravedad
            py5.stroke(255,0,0)
            py5.line(pos.x, pos.y, pos.x+a.x*500, pos.y+a.y*500)

            #Variables utiles
            speed = vel.mag
            height = d-PLANET_RADIUS

            py5.fill(255)
            py5.text(f"Speed: {speed:.2f}",10,20)
            py5.text(f"Altitude: {height:.1f}",10,40)

 
    # Draw trail
    py5.no_fill()
    py5.stroke(180)
    py5.begin_shape()
    for x, y in trail:
        py5.vertex(x, y)
    py5.end_shape()
 
    # Satellite
    py5.no_stroke()
    py5.fill(255)
    py5.circle(pos.x, pos.y, 8)
 
    # Initial velocity arrow
    if not launched and crash_timer == 0:
 
        mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
        v0 = (mouse - pos) * 0.05
 
        py5.stroke(255, 80, 80)
        py5.line(
            pos.x,
            pos.y,
            pos.x + v0.x * 10,
            pos.y + v0.y * 10
        )
 
 
def mouse_pressed():
    global vel, launched
 
    if not launched:
        mouse = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
        vel = (mouse - pos) * 0.05
        launched = True
 
 
def key_pressed():
    if py5.key == "r":
        reset()
 
 
py5.run_sketch()