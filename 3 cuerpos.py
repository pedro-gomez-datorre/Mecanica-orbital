import py5
import json
import os

PRESET_FILE = "presets.json"

bodies = []
presets = []
preset_number = ''

GM = 100
dt = 0.1
TRAIL_LENGTH = 300
VECTOR_SCALE = 1

running = False

selected_body = None
display_body = None

velocity_body = None
velocity_start = None

mass_input = ""
editing_mass = False

pos_x_input = ""
editing_pos_x = False

pos_y_input = ""
editing_pos_y = False

vel_x_input = ""
editing_vel_x = False

vel_y_input = ""
editing_vel_y = False

def setup():

    py5.size(800, 600)

    bodies.append({
        "pos": py5.Py5Vector(150, 500),
        "vel": py5.Py5Vector(0, -1),
        "mass": 100,
        "radius": 15,
        "color": py5.color(255, 0, 0),
        "trail": [],
        "vector": py5.Py5Vector(0, 0)
    })

    bodies.append({
        "pos": py5.Py5Vector(500, 500),
        "vel": py5.Py5Vector(0, 1),
        "mass": 100,
        "radius": 15,
        "color": py5.color(0, 150, 255),
        "trail": [],
        "vector": py5.Py5Vector(0, 0)
    })

    bodies.append({
        "pos": py5.Py5Vector(300, 200),
        "vel": py5.Py5Vector(1.4, 0),
        "mass": 100,
        "radius": 15,
        "color": py5.color(0, 200, 0),
        "trail": [],
        "vector": py5.Py5Vector(0, 0)
    })

    load_presets_from_file()

def draw():
    py5.background(255)

    if not running:
        if selected_body is not None:
            selected_body["pos"].x = py5.mouse_x
            selected_body["pos"].y = py5.mouse_y

        for body in bodies:
            vector = body["vector"]

            if vector.mag > 0:
                py5.stroke(body["color"])
                py5.stroke_weight(3)

                py5.line(
                    body["pos"].x,
                    body["pos"].y,
                    body["pos"].x + vector.x * VECTOR_SCALE,
                    body["pos"].y + vector.y * VECTOR_SCALE
                )

        if velocity_body is not None:
            py5.stroke(0)
            py5.stroke_weight(3)

            py5.line(
                velocity_body["pos"].x,
                velocity_body["pos"].y,
                py5.mouse_x,
                py5.mouse_y
            )

        py5.no_stroke()

        for body in bodies:
            if body == display_body:
                py5.fill(0)

                py5.circle(
                    body["pos"].x,
                    body["pos"].y,
                    body["radius"] * 3
                )
        
            py5.fill(body["color"])

            py5.circle(
                body["pos"].x,
                body["pos"].y,
                body["radius"] * 2
            )

    else:
        update_bodies()

        py5.no_fill()
        py5.stroke_weight(2)

        for body in bodies:
            py5.stroke(body["color"])

            py5.begin_shape()

            for p in body["trail"]:
                py5.vertex(p.x, p.y)

            py5.end_shape()

        py5.no_stroke()

        for body in bodies:
            py5.fill(body["color"])

            py5.circle(
                body["pos"].x,
                body["pos"].y,
                body["radius"] * 2
            )

    py5.fill(230)
    py5.no_stroke()
    py5.rect(600, 0, 200, 600)

    py5.fill(0)
    py5.text_size(20)
    py5.text("Body Settings", 620, 40)

    if display_body is not None:
        py5.text_size(16)
        py5.text("Mass:", 620, 65)

        py5.text("pos_x:", 620, 115)
        py5.text("pos_y:", 620, 165)

        py5.text("vel_x:", 620, 215)
        py5.text("vel_y:", 620, 265)

        py5.fill(0)

        if editing_mass:
            py5.text(mass_input, 630, 80)
        else:
            py5.text(str(display_body["mass"]), 630, 80)

        if editing_pos_x:
            py5.text(pos_x_input, 630, 130)
        else:
            py5.text(str(display_body["pos"].x), 630, 130)

        if editing_pos_y:
            py5.text(pos_y_input, 630, 180)
        else:
            py5.text(str(display_body["pos"].y), 630, 180)

        if editing_vel_x:
            py5.text(vel_x_input, 630, 230)
        else:
            py5.text(str(display_body["vel"].x), 630, 230)

        if editing_vel_y:
            py5.text(str(display_body["vel"].y), 630, 280)
        else:
            py5.text(str(display_body["vel"].y), 630, 280)

def update_velocity_vector():
    if display_body is not None:
        display_body["vector"] = py5.Py5Vector(
            display_body["vel"].x,
            display_body["vel"].y
        )
        
def mouse_pressed():
    global selected_body
    global velocity_body
    global velocity_start

    global editing_mass
    global mass_input

    global pos_x_input
    global editing_pos_x

    global pos_y_input
    global editing_pos_y

    global vel_x_input
    global editing_vel_x

    global vel_y_input
    global editing_vel_y

    if running:
        return

    if py5.mouse_button == py5.LEFT:
        text_distance_mass = py5.dist(py5.mouse_x,py5.mouse_y, 630, 80)

        if text_distance_mass < 25:
            if display_body is not None:
                editing_mass = True
                mass_input = str(display_body["mass"])

            return

        text_distance_pos_x = py5.dist(py5.mouse_x,py5.mouse_y, 630, 130)

        if text_distance_pos_x < 25:
            if display_body is not None:
                editing_pos_x = True
                pos_x_input = str(display_body["pos"].x)

            return

        text_distance_pos_y = py5.dist(py5.mouse_x,py5.mouse_y, 630, 180)

        if text_distance_pos_y < 25:
            if display_body is not None:
                editing_pos_y = True
                pos_y_input = str(display_body["pos"].y)

            return

        text_distance_vel_x = py5.dist(py5.mouse_x,py5.mouse_y, 630, 230)

        if text_distance_vel_x < 25:
            if display_body is not None:
                editing_vel_x = True
                vel_x_input = str(display_body["vel"].x)

            return

        text_distance_vel_y = py5.dist(py5.mouse_x,py5.mouse_y, 630, 280)

        if text_distance_vel_y < 25:
            if display_body is not None:
                editing_vel_y = True
                vel_y_input = str(display_body["vel"].y)

            return
        
        for body in bodies:
            distance = py5.dist(
                py5.mouse_x,
                py5.mouse_y,
                body["pos"].x,
                body["pos"].y
            )

            if distance < body["radius"]:
                selected_body = body
                break

    elif py5.mouse_button == py5.RIGHT:

        for body in bodies:
            distance = py5.dist(
                py5.mouse_x,
                py5.mouse_y,
                body["pos"].x,
                body["pos"].y
            )

            if distance < body["radius"]:
                velocity_body = body

                velocity_start = py5.Py5Vector(
                    body["pos"].x,
                    body["pos"].y
                )

                break


def mouse_released():
    global selected_body
    global velocity_body
    global velocity_start

    if py5.mouse_button == py5.LEFT:
        selected_body = None

    elif py5.mouse_button == py5.RIGHT:

        if velocity_body is not None:

            velocity_end = py5.Py5Vector(
                py5.mouse_x,
                py5.mouse_y
            )

            velocity = velocity_end - velocity_start

            velocity_body["vel"] = velocity * 0.1
            velocity_body["vector"] = velocity.copy

        velocity_body = None
        velocity_start = None


def key_pressed():
    global running

    global editing_mass
    global mass_input

    global pos_x_input
    global editing_pos_x

    global pos_y_input
    global editing_pos_y

    global vel_x_input
    global editing_vel_x

    global vel_y_input
    global editing_vel_y

    global display_body

    global preset_number

    if not running:
        if py5.key == ' ':
            for body in bodies:
                distance = py5.dist(
                    py5.mouse_x,
                    py5.mouse_y,
                    body["pos"].x,
                    body["pos"].y
                )

                if distance < body["radius"]:
                    display_body = body
                    break
                else:
                    display_body = None

        if editing_mass:
            if py5.key == py5.ENTER:
                if mass_input != "":
                    display_body["mass"] = float(mass_input)

                editing_mass = False

            elif py5.key == py5.BACKSPACE:
                mass_input = mass_input[:-1]

            elif py5.key in "0123456789.":
                mass_input += py5.key

            return

        if editing_pos_x:
            if py5.key == py5.ENTER:
                if pos_x_input != "":
                    display_body["pos"].x = float(pos_x_input)
                    
                editing_pos_x = False

            elif py5.key == py5.BACKSPACE:
                pos_x_input = pos_x_input[:-1]

            elif py5.key in "0123456789.":
                pos_x_input += py5.key

            return

        if editing_pos_y:
            if py5.key == py5.ENTER:
                if pos_y_input != "":
                    display_body["pos"].y = float(pos_y_input)

                editing_pos_y = False

            elif py5.key == py5.BACKSPACE:
                pos_y_input = pos_y_input[:-1]

            elif py5.key in "0123456789.":
                pos_y_input += py5.key

            return

        if editing_vel_x:
            if py5.key == py5.ENTER:
                if vel_x_input != "":
                    display_body["vel"].x = float(vel_x_input)

                update_velocity_vector()

                editing_vel_x = False

            elif py5.key == py5.BACKSPACE:
                vel_x_input = vel_x_input[:-1]

            elif py5.key in "0123456789.":
                vel_x_input += py5.key

            return

        if editing_vel_y:
            if py5.key == py5.ENTER:
                if vel_y_input != "":
                    display_body["vel"].y = float(vel_y_input)
                
                update_velocity_vector()

                editing_vel_y = False
                

            elif py5.key == py5.BACKSPACE:
                vel_y_input = vel_y_input[:-1]

            elif py5.key in "0123456789.":
                vel_y_input += py5.key

            return

        if py5.key == 's':
            save_preset()
            running = False
            return


        if py5.key in "0123456789":
            preset_number += py5.key

        if py5.key == py5.TAB:

            try:
                preset_number = int(preset_number)

            except:
                preset_number = ''
                return
                
            load_preset(preset_number)
            running = False
            preset_number = ''
            return

        if py5.key == py5.ENTER:
            running = True

def update_bodies():
    acc = [
        py5.Py5Vector(0, 0)
        for _ in bodies
    ]

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):

            r = bodies[j]["pos"] - bodies[i]["pos"]

            d = r.mag

            if d < 10:
                d = 10

            force = GM / (d ** 3)

            ai = r.copy * (
                force * bodies[j]["mass"]
            )

            aj = r.copy * (
                -force * bodies[i]["mass"]
            )

            acc[i] += ai
            acc[j] += aj

    for i in range(len(bodies)):

        bodies[i]["vel"] += acc[i] * dt

        bodies[i]["pos"] += bodies[i]["vel"] * dt

        bodies[i]["trail"].append(
            bodies[i]["pos"].copy
        )

        if len(bodies[i]["trail"]) > TRAIL_LENGTH:
            bodies[i]["trail"].pop(0)


def load_presets_from_file():
    global presets

    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r") as file:
            presets = json.load(file)

    else:
        presets = []

def load_preset(index):
    if index < 0 or index >= len(presets):
        return

    preset = presets[index]

    if len(preset) != len(bodies):
        return

    for i in range(len(bodies)):
        body = bodies[i]
        data = preset[i]

        body["pos"].x = preset[i]["x"]
        body["pos"].y = preset[i]["y"]

        body["vel"] = py5.Py5Vector(data["vel_x"], data["vel_y"])

        body["mass"] = preset[i]["mass"]

        body["vector"] = py5.Py5Vector(data["vector_x"], data["vector_y"])

        bodies[i]["trail"].clear()

def save_preset():
    preset = []

    for body in bodies:
        preset.append({"x": body["pos"].x, 
                       "y": body["pos"].y,

                       "vel_x": body["vel"].x,
                       "vel_y": body["vel"].y,

                       "mass": body["mass"],

                       "vector_x": body["vector"].x,
                       "vector_y": body["vector"].y
                       })

    presets.append(preset)

    with open(PRESET_FILE, "w") as file:
        json.dump(presets, file, indent=4)

py5.run_sketch()