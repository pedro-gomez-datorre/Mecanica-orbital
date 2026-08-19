import py5
import json
import os

help_window = None
class HelpWindow(py5.Sketch):

    def settings(self):
        self.size(400, 800)

    def draw(self):
        self.background(245)

        self.fill(0)
        self.text_size(28)
        self.text("HELP", 30, 45)

        self.text_size(16)

        help_text = [
            "CONTROLS",
            "",
            "Left Click + Drag",
            "Move a body",
            "",
            "Right Click + Drag",
            "Set the velocity of a body",
            "",
            "Space",
            "Select the body under the mouse",
            "",
            "Enter",
            "Start the simulation",
            "",
            "R",
            "Reset to the default preset",
            "",
            "S",
            "Save a preset",
            "",
            "Number + TAB",
            "Load a preset",
            "",
            "Backspace",
            "Delete a preset when hovering over it",
        ]

        y = 85

        for line in help_text:
            if line == "CONTROLS":
                self.fill(50)
                self.text_size(20)
            elif line == "":
                y += 10
                continue
            else:
                self.fill(0)
                self.text_size(16)

            self.text(line, 30, y)
            y += 25

def open_help():
    global help_window

    if help_window is None:
        help_window = HelpWindow()
        help_window.run_sketch()

DEFAULT_PRESET = [
        {
            "x": 150.0,
            "y": 500.0,
            "vel_x": 0.0,
            "vel_y": -1.0,
            "mass": 100,
            "vector_x": 0.0,
            "vector_y": 0.0
        },
        {
            "x": 500.0,
            "y": 500.0,
            "vel_x": 0.0,
            "vel_y": 1.0,
            "mass": 100,
            "vector_x": 0.0,
            "vector_y": 0.0
        },
        {
            "x": 300.0,
            "y": 200.0,
            "vel_x": 1.4,
            "vel_y": 0.0,
            "mass": 100,
            "vector_x": 0.0,
            "vector_y": 0.0
        }
    ]

PRESET_FILE = "presets.json"

name = ""
saving = False

bodies = []
presets = []
preset_number = ''

GM = 100
dt = 0.02
TRAIL_LENGTH = 300
VECTOR_SCALE = 40

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

speed_input = ""
editing_speed = False

angle_input = ""
editing_angle = False

preset_scroll = 0

import math

def get_speed(body):
    return body["vel"].mag


def get_angle(body):
    angle = math.degrees(math.atan2(body["vel"].y, body["vel"].x))

    if angle < 0:
        angle += 360

    return angle


def set_speed_angle(body, speed, angle):
    angle_rad = math.radians(angle)

    body["vel"] = py5.Py5Vector(
        math.cos(angle_rad) * speed,
        math.sin(angle_rad) * speed
    )

    body["vector"] = body["vel"].copy

def setup():
    py5.size(1000, 600)

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
                py5.circle(body["pos"].x, body["pos"].y, body["radius"] * 3)

            py5.fill(body["color"])
            py5.circle(body["pos"].x, body["pos"].y, body["radius"] * 2)

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
            py5.circle(body["pos"].x, body["pos"].y, body["radius"] * 2)

    py5.fill(230)
    py5.no_stroke()
    py5.rect(600, 0, 200, 600)

    py5.fill(180)
    py5.rect(600, 0, 2, 600)

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
        py5.text("Speed:", 620, 315)
        py5.text("Angle:", 620, 365)

        py5.fill(0)

        if editing_mass:
            py5.text(mass_input, 630, 80)
        else:
            py5.text(str(display_body["mass"]), 630, 80)

        if editing_pos_x:
            py5.text(pos_x_input, 630, 130)
        else:
            py5.text(str(round(display_body["pos"].x, 2)), 630, 130)

        if editing_pos_y:
            py5.text(pos_y_input, 630, 180)
        else:
            py5.text(str(round(display_body["pos"].y, 2)), 630, 180)

        if editing_vel_x:
            py5.text(vel_x_input, 630, 230)
        else:
            py5.text(str(round(display_body["vel"].x, 2)), 630, 230)

        if editing_vel_y:
            py5.text(vel_y_input, 630, 280)
        else:
            py5.text(str(round(display_body["vel"].y, 2)), 630, 280)

        if editing_speed:
            py5.text(speed_input, 630, 330)
        else:
            py5.text(str(round(get_speed(display_body), 2)), 630, 330)

        if editing_angle:
            py5.text(angle_input, 630, 380)
        else:
            py5.text(str(round(get_angle(display_body), 2)), 630, 380)


    py5.fill(215)
    py5.rect(800, 0, 200, 600)

    py5.fill(180)
    py5.rect(800, 0, 2, 600)

    py5.fill(0)
    py5.text_size(22)
    py5.text("Presets", 820, 40)

    button_height = 40
    button_spacing = 10
    start_y = 65 - preset_scroll

    for i in range(len(presets)):
        y = start_y + i * (button_height + button_spacing)

        if y + button_height < 55:
            continue

        if y > 510:
            continue

        if py5.mouse_x >= 815 and py5.mouse_x <= 985 and py5.mouse_y >= y and py5.mouse_y <= y + button_height:
            py5.fill(180)
        else:
            py5.fill(195)

        py5.rect(815, y, 170, button_height, 6)

        py5.fill(0)
        py5.text_size(15)
        py5.text(presets[i]["name"], 830, y + 26)

    if py5.mouse_x >= 815 and py5.mouse_x <= 985 and py5.mouse_y >= 525 and py5.mouse_y <= 565:
        py5.fill(170)
    else:
        py5.fill(190)

    py5.rect(815, 525, 170, 40, 6)
    py5.rect(20, 10, 80, 40, 6)

    if saving:
        py5.fill(255)
        py5.rect(810, 450, 180, 55, 6)

        py5.fill(0)
        py5.text_size(14)
        py5.text("Preset name:", 815, 445)
        py5.text(name, 820, 482)

    py5.fill(0)
    py5.text_size(14)
    py5.text("SAVE PRESET", 850, 550)

    py5.fill(0)
    py5.text_size(20)
    py5.text("HELP", 40, 35)




def update_bodies():
    acc = [py5.Py5Vector(0, 0) for _ in bodies]

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            r = bodies[j]["pos"] - bodies[i]["pos"]
            d = r.mag

            if d < 10:
                d = 10

            force = GM / (d ** 3)

            ai = r.copy * (force * bodies[j]["mass"])
            aj = r.copy * (-force * bodies[i]["mass"])

            acc[i] += ai
            acc[j] += aj

    for i in range(len(bodies)):
        bodies[i]["vel"] += acc[i] * dt
        bodies[i]["pos"] += bodies[i]["vel"] * dt
        bodies[i]["trail"].append(bodies[i]["pos"].copy)

        if len(bodies[i]["trail"]) > TRAIL_LENGTH:
            bodies[i]["trail"].pop(0)


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

    global angle_input
    global editing_angle
    global speed_input
    global editing_speed
    
    global preset_scroll
    global running
    global help_window

    if running:
        return

    if py5.mouse_button == py5.LEFT:
        if py5.mouse_x >= 20 and py5.mouse_x <= 100 and py5.mouse_y >= 10 and py5.mouse_y <= 50:
            help_window = None
            open_help()
            return
        
        if py5.mouse_x >= 800:
            button_height = 40
            button_spacing = 10
            start_y = 65 - preset_scroll

            for i in range(len(presets)):
                y = start_y + i * (button_height + button_spacing)

                if py5.mouse_x >= 815 and py5.mouse_x <= 985 and py5.mouse_y >= y and py5.mouse_y <= y + button_height:
                    load_preset(i)
                    running = False
                    return

            if py5.mouse_x >= 815 and py5.mouse_x <= 985 and py5.mouse_y >= 525 and py5.mouse_y <= 565:
                save_preset()
                return

            return

        if py5.mouse_x >= 600:
            text_distance_mass = py5.dist(py5.mouse_x, py5.mouse_y, 630, 80)

            if text_distance_mass < 25:
                if display_body is not None:
                    editing_mass = True
                    mass_input = str(display_body["mass"])
                return

            text_distance_pos_x = py5.dist(py5.mouse_x, py5.mouse_y, 630, 130)

            if text_distance_pos_x < 25:
                if display_body is not None:
                    editing_pos_x = True
                    pos_x_input = str(display_body["pos"].x)
                return

            text_distance_pos_y = py5.dist(py5.mouse_x, py5.mouse_y, 630, 180)

            if text_distance_pos_y < 25:
                if display_body is not None:
                    editing_pos_y = True
                    pos_y_input = str(display_body["pos"].y)
                return

            text_distance_vel_x = py5.dist(py5.mouse_x, py5.mouse_y, 630, 230)

            if text_distance_vel_x < 25:
                if display_body is not None:
                    editing_vel_x = True
                    vel_x_input = str(display_body["vel"].x)
                return

            text_distance_vel_y = py5.dist(py5.mouse_x, py5.mouse_y, 630, 280)

            if text_distance_vel_y < 25:
                if display_body is not None:
                    editing_vel_y = True
                    vel_y_input = str(display_body["vel"].y)
                return

            text_distance_speed = py5.dist(py5.mouse_x, py5.mouse_y, 630, 330)

            if text_distance_speed < 25:
                if display_body is not None:
                    editing_speed = True
                    speed_input = str(round(get_speed(display_body), 2))
                return


            text_distance_angle = py5.dist(py5.mouse_x, py5.mouse_y, 630, 380)

            if text_distance_angle < 25:
                if display_body is not None:
                    editing_angle = True
                    angle_input = str(round(get_angle(display_body), 2))
                return

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
        if py5.mouse_x >= 600:
            return

        for body in bodies:
            distance = py5.dist(
                py5.mouse_x,
                py5.mouse_y,
                body["pos"].x,
                body["pos"].y
            )

            if distance < body["radius"]:
                velocity_body = body
                velocity_start = py5.Py5Vector(body["pos"].x, body["pos"].y)
                break


def mouse_released():
    global selected_body
    global velocity_body
    global velocity_start

    if py5.mouse_button == py5.LEFT:
        selected_body = None

    elif py5.mouse_button == py5.RIGHT:
        if velocity_body is not None:
            velocity_end = py5.Py5Vector(py5.mouse_x, py5.mouse_y)
            velocity = velocity_end - velocity_start

            velocity_body["vel"] = velocity * 0.025
            velocity_body["vector"] = velocity.copy * 0.025

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

    global name
    global saving

    global speed_input
    global editing_speed
    global angle_input
    global editing_angle

    if saving:
        if py5.key == py5.ENTER:
            if name != "":
                preset = {
                    "name": name,
                    "bodies": []
                }

                for body in bodies:
                    preset["bodies"].append({
                        "x": body["pos"].x,
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

                name = ""
                saving = False

            return

        elif py5.key == py5.BACKSPACE:
            name = name[:-1]
            return

        elif py5.key != py5.CODED:
            name += py5.key
            return
    
    if py5.key == 'r':
        if running:
            running = False

        load_default_preset()

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

        if editing_speed:
            if py5.key == py5.ENTER:
                if speed_input != "":
                    speed = float(speed_input)
                    angle = get_angle(display_body)
                    set_speed_angle(display_body, speed, angle)

                editing_speed = False

            elif py5.key == py5.BACKSPACE:
                speed_input = speed_input[:-1]

            elif py5.key in "0123456789.":
                speed_input += py5.key

            return

        if editing_angle:
            if py5.key == py5.ENTER:
                if angle_input != "":
                    angle = float(angle_input)
                    speed = get_speed(display_body)
                    set_speed_angle(display_body, speed, angle)

                editing_angle = False

            elif py5.key == py5.BACKSPACE:
                angle_input = angle_input[:-1]

            elif py5.key in "0123456789.":
                angle_input += py5.key

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

        if py5.key == py5.BACKSPACE:
            if py5.mouse_x >= 800:
                button_height = 40
                button_spacing = 10
                start_y = 65 - preset_scroll

                for i in range(len(presets)):
                    y = start_y + i * (button_height + button_spacing)

                    if py5.mouse_x >= 815 and py5.mouse_x <= 985 and py5.mouse_y >= y and py5.mouse_y <= y + button_height:
                        delet_preset(i)
                        running = False
                        return

        if py5.key == py5.ENTER:
            running = True


def load_presets_from_file():
    global presets

    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r") as file:
            presets = json.load(file)
    else:
        presets = []


def load_default_preset():
    for i in range(len(bodies)):
        body = bodies[i]
        data = DEFAULT_PRESET[i]

        body["pos"].x = data["x"]
        body["pos"].y = data["y"]
        body["vel"] = py5.Py5Vector(data["vel_x"], data["vel_y"])
        body["mass"] = data["mass"]
        body["vector"] = py5.Py5Vector(data["vector_x"], data["vector_y"])
        body["trail"].clear() 

        
        for body in bodies:
            body["trail"].clear()

def load_preset(index):
    global display_body

    if index < 0 or index >= len(presets):
        return

    preset = presets[index]

    if len(preset["bodies"]) != len(bodies):
        return

    for i in range(len(bodies)):
        body = bodies[i]
        data = preset["bodies"][i]

        body["pos"].x = data["x"]
        body["pos"].y = data["y"]
        body["vel"] = py5.Py5Vector(data["vel_x"], data["vel_y"])
        body["mass"] = data["mass"]
        body["vector"] = py5.Py5Vector(data["vector_x"], data["vector_y"])
        body["trail"].clear()

    display_body = None


def save_preset():
    global name
    global saving

    name = ""
    saving = True

def delet_preset(index):
    global presets

    if index < 0 or index >= len(presets):
        return

    presets.pop(index)

    with open(PRESET_FILE, "w") as file:
        json.dump(presets, file, indent=4)

py5.run_sketch()