import json
import os
import math
import builtins

import pygame
import numpy as np


import tkinter as tk

tk_root = tk.Tk()
tk_root.withdraw()

help_window = None

def open_help():
    global help_window

    if help_window is not None:
        try:
            help_window.lift()
            help_window.focus_force()
            return
        except:
            help_window = None

    help_window = tk.Toplevel()
    help_window.title("Help")
    help_window.geometry("400x900")
    help_window.resizable(False, False)

    title = tk.Label(
        help_window,
        text="HELP",
        font=("Arial", 24)
    )
    title.pack(anchor="w", padx=30, pady=(20, 10))

    help_text = [
        ("CONTROLS", 18, "bold"),
        ("", 12, "normal"),

        ("Left Click + Drag", 14, "normal"),
        ("Move a body", 14, "normal"),
        ("", 12, "normal"),

        ("Right Click + Drag", 14, "normal"),
        ("Set the velocity of a body", 14, "normal"),
        ("", 12, "normal"),

        ("Space", 14, "normal"),
        ("Select the body under the mouse", 14, "normal"),
        ("", 12, "normal"),

        ("Enter", 14, "normal"),
        ("Start the simulation", 14, "normal"),
        ("", 12, "normal"),

        ("R", 14, "normal"),
        ("Reset to the default preset", 14, "normal"),
        ("", 12, "normal"),

        ("S", 14, "normal"),
        ("Save a preset", 14, "normal"),
        ("", 12, "normal"),

        ("RightClick + new name", 14, "normal"),
        ("Rename a preset", 14, "normal"),
        ("", 12, "normal"),

        ("Backspace", 14, "normal"),
        ("Delete a preset when hovering over it", 14, "normal"),
        ("", 12, "normal"),

        ("Disclaimer", 14, "normal"),
        ("The mass of the planets are not to scale", 12, "normal"),
    ]

    for text, size, weight in help_text:
        label = tk.Label(
            help_window,
            text=text,
            font=("Arial", size, weight),
            anchor="w"
        )
        label.pack(fill="x", padx=30)

    def close_help():
        global help_window
        help_window.destroy()
        help_window = None

    help_window.protocol("WM_DELETE_WINDOW", close_help)

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
dt = 0.005
TRAIL_LENGTH = 600
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

renaming = False
rename_index = 0


pygame.init()

Font = pygame.font.Font(None, 20)
font = pygame.font.Font(None, 16)

text_color = (0, 0, 0)

screen = pygame.display.set_mode((1000, 600))

clock = pygame.time.Clock()

zoom = 1.0
zoom_step = 0.1

def world_to_screen(pos):
    center = np.array([300.0, 300.0])

    return center + (pos - center) * zoom

def screen_to_world(pos):
    center = np.array([300.0, 300.0])

    return center + (pos - center) / zoom

def format_distance(distance):
    if distance >= 1000:
        return f"{distance/1000:.2f} km"
    else:
        return f"{distance:.0f} m"

def draw_distance():
    visible_width = 600/zoom
    text = font.render(f"Scale: {format_distance(visible_width)}", True, (0, 0, 0))

    x = 600 - text.get_width() - 15
    y = 600 - text.get_height() - 15

    screen.blit(text, (x, y))

def get_speed(body):
    return np.linalg.norm(body["vel"])

def get_hovered_body():
    mouse_pos = np.array(pygame.mouse.get_pos(), dtype=float)

    for i, body in enumerate(bodies):
        screen_pos = world_to_screen(body["pos"])
        distance = np.linalg.norm(mouse_pos - screen_pos)

        if distance <= body["radius"] * zoom:
            return i, body

    return None, None

def draw_tooltip():
    index, body = get_hovered_body()

    if body is None:
        return

    mouse_x, mouse_y = pygame.mouse.get_pos()

    speed = get_speed(body)
    angle = get_angle(body)

    lines = [
        f"Body {index + 1}",
        "",
        f"Mass: {body['mass']:.2f} kg",
        f"Position X: {body['pos'][0]:.2f} m",
        f"Position Y: {body['pos'][1]:.2f} m",
        "",
        f"Velocity X: {body['vel'][0]:.2f} m/s",
        f"Velocity Y: {body['vel'][1]:.2f} m/s",
        f"Speed: {speed:.2f} m/s",
        f"Angle: {angle:.2f}°"
    ]

    width = 150
    height = len(lines)*18+16

    tooltip_x = mouse_x+15
    tooltip_y = mouse_y+15

    if tooltip_x + width > 600:
        tooltip_x = mouse_x-width-15

    if tooltip_y + height > 600:
        tooltip_y = mouse_y-width-15

    pygame.draw.rect(screen, (40, 40, 40), (tooltip_x, tooltip_y, width, height))

    pygame.draw.rect(screen, (220, 220, 220), (tooltip_x, tooltip_y, width, height), 2)

    for i, line in enumerate(lines):
        text = font.render(line, True, (255, 255, 255))

        screen.blit(text, (tooltip_x + 8, tooltip_y + 8 + i * 18))


def get_angle(body):
    angle = math.degrees(math.atan2(body["vel"][1], body["vel"][0]))

    if angle < 0:
        angle += 360

    return angle

def set_body_count(count):
    global display_body
    global selected_body

    if count == 2:
        while len(bodies) > 2:
            bodies.pop()

    elif count == 3:
        while len(bodies) < 3:
            bodies.append({
                "pos": np.array([300.0, 200.0]),
                "vel": np.array([1.4, 0.0]),
                "mass": 100,
                "radius": 15,
                "color": (0, 200, 0),
                "trail": [],
                "vector": np.array([0.0, 0.0])
            })

    display_body = None
    selected_body = None
    
def set_speed_angle(body, speed, angle):
    angle_rad = math.radians(angle)

    body["vel"] = np.array([
        math.cos(angle_rad) * speed,
        math.sin(angle_rad) * speed
    ])

    body["vector"] = body["vel"].copy()

def setup():
    bodies.append({
        "pos": np.array([150.0, 500.0]),
        "vel": np.array([0.0, -1.0]),
        "mass": 100,
        "radius": 15,
        "color": (255, 0, 0),
        "trail": [],
        "vector": np.array([0.0, 0.0])
    })

    bodies.append({
        "pos": np.array([500.0, 500.0]),
        "vel": np.array([0.0, 1.0]),
        "mass": 100,
        "radius": 15,
        "color": (0, 150, 255),
        "trail": [],
        "vector": np.array([0.0, 0.0])
    })

    bodies.append({
        "pos": np.array([300.0, 200.0]),
        "vel": np.array([1.4, 0.0]),
        "mass": 100,
        "radius": 15,
        "color": (0, 200, 0),
        "trail": [],
        "vector": np.array([0.0, 0.0])
    })
        
    load_presets_from_file()


def draw():
    screen.fill((255, 255, 255))

    pygame.draw.rect(screen, (190, 190, 190), (520, 10, 35, 35), 5)
    pygame.draw.rect(screen, (190, 190, 190), (560, 10, 35, 35), 5)

    screen.blit(font.render("-", True, text_color), (532, 20))
    screen.blit(font.render("+", True, text_color), (572, 20))

    if not running:
        if selected_body is not None:
            selected_body["pos"] = screen_to_world(np.array(pygame.mouse.get_pos(), dtype=float))

        for body in bodies:
            vector = body["vector"]

            if np.linalg.norm(vector) > 0:
                pygame.draw.line(
                    screen,
                    body["color"],
                    world_to_screen(body["pos"]).astype(int),
                    world_to_screen(
                        body["pos"] + vector * VECTOR_SCALE
                    ).astype(int),
                    max(1, int(3 * zoom))
                )

        if velocity_body is not None:
            pygame.draw.line(
                screen,
                (0, 0, 0),
                world_to_screen(velocity_body["pos"]).astype(int),
                pygame.mouse.get_pos(),
                3
            )

        for body in bodies:
            screen_pos = world_to_screen(body["pos"])

            if body is display_body:
                pygame.draw.circle(
                    screen,
                    (0, 0, 0),
                    screen_pos.astype(int),
                    int((body["radius"]+5)*zoom)
                )
            
            pygame.draw.circle(
                screen,
                body["color"],
                screen_pos.astype(int),
                int(body["radius"]*zoom)
            )

    else:
        update_bodies()

        for body in bodies:
            if len(body["trail"]) > 1:
                pygame.draw.lines(
                    screen,
                    body["color"],
                    False,
                    [world_to_screen(p).astype(int) for p in body["trail"]],
                    max(1, int(2 * zoom))
                )

        for body in bodies:
            screen_pos = world_to_screen(body["pos"])
            pygame.draw.circle(
                screen,
                body["color"],
                screen_pos.astype(int),
                int(body["radius"]*zoom)
            )

    pygame.draw.rect(screen, (230, 230, 230), (600, 0, 200, 600))

    pygame.draw.rect(screen, (180, 180, 180), (600, 0, 2, 600))

    text = Font.render("Body Settings", True, (0, 0, 0))
    screen.blit(text, (620, 25))
    screen.blit(font.render("Bodies:", True, text_color), (620, 50))

    if len(bodies) == 2:
        button_color = (160, 160, 160)
    else:
        button_color = (195, 195, 195)

    pygame.draw.rect(screen, button_color, (680, 45, 45, 30), 5)
    screen.blit(font.render("2", True, text_color), (697, 53))

    if len(bodies) == 3:
        button_color = (160, 160, 160)
    else:
        button_color = (195, 195, 195)

    pygame.draw.rect(screen, button_color, (735, 45, 45, 30), 5)
    screen.blit(font.render("3", True, text_color), (752, 53))


    if display_body is not None:
        screen.blit(font.render("Mass (kg):", True, (0, 0, 0)), (620, 65))
        screen.blit(font.render("pos_x (m):", True, (0, 0, 0)), (620, 115))
        screen.blit(font.render("pos_y (m):", True, (0, 0, 0)), (620, 165))
        screen.blit(font.render("vel_x (m/s):", True, (0, 0, 0)), (620, 215))
        screen.blit(font.render("vel_y (m/s):", True, (0, 0, 0)), (620, 265))
        screen.blit(font.render("Speed (m/s):", True, (0, 0, 0)), (620, 315))
        screen.blit(font.render("Angle (°):", True, (0, 0, 0)), (620, 365))

        if editing_mass:
            text = font.render(mass_input, True, text_color)
        else:
            text = font.render(str(display_body["mass"]), True, text_color)

        screen.blit(text, (630, 80))

        if editing_pos_x:
            text = font.render(pos_x_input, True, text_color)
        else:
            text = font.render(str(round(display_body["pos"][0], 2)), True, text_color)

        screen.blit(text, (630, 130))

        if editing_pos_y:
            text = font.render(pos_y_input, True, text_color)
        else:
            text = font.render(str(round(display_body["pos"][1], 2)), True, text_color)

        screen.blit(text, (630, 180))

        if editing_vel_x:
            text = font.render(vel_x_input, True, text_color)
        else:
            text = font.render(str(round(display_body["vel"][0], 2)), True, text_color)

        screen.blit(text, (630, 230))

        if editing_vel_y:
            text = font.render(vel_y_input, True, text_color)
        else:
            text = font.render(str(round(display_body["vel"][1], 2)), True, text_color)

        screen.blit(text, (630, 280))

        if editing_speed:
            text = font.render(speed_input, True, text_color)
        else:
            text = font.render(str(round(get_speed(display_body), 2)), True, text_color)

        screen.blit(text, (630, 330))

        if editing_angle:
            text = font.render(angle_input, True, text_color)
        else:
            text = font.render(str(round(get_angle(display_body), 2)), True, text_color)

        screen.blit(text, (630, 380))

    pygame.draw.rect(screen, (215, 215, 215), (800, 0, 200, 600))

    pygame.draw.rect(screen, (180, 180, 180), (800, 0, 2, 600))

    text = Font.render("Presets", True, text_color)
    screen.blit(text, (820, 40))

    button_height = 40
    button_spacing = 10
    start_y = 65 - preset_scroll

    for i in range(len(presets)):
        y = start_y + i * (button_height + button_spacing)

        if y + button_height < 55:
            continue

        if y > 510:
            continue

        if pygame.mouse.get_pos()[0] >= 815 and pygame.mouse.get_pos()[0] <= 985 and pygame.mouse.get_pos()[1] >= y and pygame.mouse.get_pos()[1] <= y + button_height:
            button_color = (180, 180, 180)
        else:
            button_color = (195, 195, 195)

        pygame.draw.rect(screen, button_color, (815, y, 170, button_height), 6)

        text = font.render(presets[i]["name"], True, text_color)
        screen.blit(text, (830, y + 16))

    if pygame.mouse.get_pos()[0] >= 815 and pygame.mouse.get_pos()[0] <= 985 and pygame.mouse.get_pos()[1] >= 525 and pygame.mouse.get_pos()[1] <= 565:
        button_color = (170, 170, 170)
    else:
        button_color = (190, 190, 190)

    pygame.draw.rect(screen, button_color, (815, 525, 170, 40), 6)
    pygame.draw.rect(screen, button_color, (20, 10, 80, 40), 6)

    if saving:
        pygame.draw.rect(screen, (255, 255, 255), (810, 450, 180, 55), 6)


        text = font.render("Preset name:", True, text_color)
        screen.blit(text, (815, 445))

        text = font.render(name, True, text_color)
        screen.blit(text, (820, 480))

    screen.blit(font.render("SAVE PRESET", True, text_color), (850, 550))

    screen.blit(font.render("HELP", True, text_color), (40, 30))

    draw_distance()
    draw_tooltip()
    

def update_bodies():
    acc = [np.array([0.0, 0.0]) for _ in bodies]

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            r = bodies[j]["pos"] - bodies[i]["pos"]
            d = np.linalg.norm(r)

            if d < 10:
                d = 10

            force = GM / (d ** 3)

            ai = r.copy() * (force * bodies[j]["mass"])
            aj = r.copy() * (-force * bodies[i]["mass"])

            acc[i] += ai
            acc[j] += aj

    for i in range(len(bodies)):
        bodies[i]["vel"] += acc[i] * dt
        bodies[i]["pos"] += bodies[i]["vel"] * dt
        bodies[i]["trail"].append(bodies[i]["pos"].copy())

        if len(bodies[i]["trail"]) > TRAIL_LENGTH:
            bodies[i]["trail"].pop(0)


def update_velocity_vector():
    if display_body is not None:
        display_body["vector"] = np.array([
            display_body["vel"][0],
            display_body["vel"][1]
        ])


def mouse_pressed(event):
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

    global renaming
    global rename_index
    global name

    global zoom

    mouse_pos = np.array(pygame.mouse.get_pos(), dtype=float)


    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if not running:
                if 680 <= mouse_x <= 725 and 45 <= mouse_y <= 75:
                    set_body_count(2)
                    return

                if 735 <= mouse_x <= 780 and 45 <= mouse_y <= 75:
                    set_body_count(3)
                    return
            
                if pygame.mouse.get_pos()[0] >= 800:
                    button_height = 40
                    button_spacing = 10
                    start_y = 65 - preset_scroll

                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    for i in range(len(presets)):
                        y = start_y + i * (button_height + button_spacing)

                        if 815 <= mouse_x <= 985 and y <= mouse_y <= y + button_height:
                            if event.button == 1:
                                load_preset(i)
                                running = False
                                return

                            elif event.button == 3:
                                renaming = True
                                rename_index = i
                                name = ""
                                return

                    if (815 <= mouse_x <= 985 and 525 <= mouse_y <= 565 and event.button == 1):
                        save_preset()
                        return

                    return

        if event.button == 1:
            if 520 <= mouse_x <= 555 and 10 <= mouse_y <= 45:
                zoom = max(0.2, zoom - zoom_step)
                return

            if 560 <= mouse_x <= 595 and 10 <= mouse_y <= 45:
                zoom = min(3.0, zoom + zoom_step)
                return


            if pygame.mouse.get_pos()[0] >= 20 and pygame.mouse.get_pos()[0] <= 100 and pygame.mouse.get_pos()[1] >= 10 and pygame.mouse.get_pos()[1] <= 50:
                help_window = None
                open_help()
                return

                if running:
                    return
            

            if pygame.mouse.get_pos()[0] >= 600:

                point = np.array([630, 80])
                text_distance_mass = np.linalg.norm(mouse_pos - point)

                if text_distance_mass < 25:
                    if display_body is not None:
                        editing_mass = True
                        mass_input = str(display_body["mass"])
                    return

                point = np.array([630, 130])
                text_distance_pos_x = np.linalg.norm(mouse_pos - point)

                if text_distance_pos_x < 25:
                    if display_body is not None:
                        editing_pos_x = True
                        pos_x_input = str(display_body["pos"][0])
                    return

                point = np.array([630, 180])
                text_distance_pos_y = np.linalg.norm(mouse_pos - point)

                if text_distance_pos_y < 25:
                    if display_body is not None:
                        editing_pos_y = True
                        pos_y_input = str(display_body["pos"][1])
                    return

                point = np.array([630, 230])
                text_distance_vel_x = np.linalg.norm(mouse_pos - point)

                if text_distance_vel_x < 25:
                    if display_body is not None:
                        editing_vel_x = True
                        vel_x_input = str(display_body["vel"][0])
                    return

                point = np.array([630, 280])
                text_distance_vel_y = np.linalg.norm(mouse_pos - point)

                if text_distance_vel_y < 25:
                    if display_body is not None:
                        editing_vel_y = True
                        vel_y_input = str(display_body["vel"][1])
                    return

                point = np.array([630, 330])
                text_distance_speed = np.linalg.norm(mouse_pos - point)

                if text_distance_speed < 25:
                    if display_body is not None:
                        editing_speed = True
                        speed_input = str(round(get_speed(display_body), 2))
                    return

                point = np.array([630, 380])
                text_distance_angle = np.linalg.norm(mouse_pos - point)

                if text_distance_angle < 25:
                    if display_body is not None:
                        editing_angle = True
                        angle_input = str(round(get_angle(display_body), 2))
                    return

                return

            for body in bodies:
                screen_pos = world_to_screen(body["pos"])
                distance = np.linalg.norm(mouse_pos - screen_pos)

                if distance < body["radius"]*zoom:
                    selected_body = body
                    break

        if running:
            return
        
        elif event.button == 3:
            if pygame.mouse.get_pos()[0] >= 600:
                return

            for body in bodies:
                screen_pos = world_to_screen(body["pos"])
                distance = np.linalg.norm(mouse_pos - screen_pos)

                if distance < body["radius"]*zoom:
                    velocity_body = body
                    velocity_start = world_to_screen(body["pos"]).copy()
                    break


def mouse_released(event):
    global selected_body
    global velocity_body
    global velocity_start

    if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            selected_body = None

        elif event.button == 3:
            if velocity_body is not None:
                velocity_end = np.array([pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]])
                velocity = velocity_end - velocity_start

                velocity_body["vel"] = velocity * 0.025
                velocity_body["vector"] = velocity.copy() * 0.025

            velocity_body = None
            velocity_start = None


def key_pressed(event):
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

        global renaming
        global rename_index

        if renaming:
            if event.key == pygame.K_RETURN:
                if name != "":
                    presets[rename_index]["name"] = name

                    with open(PRESET_FILE, "w") as file:
                        json.dump(presets, file, indent=4)

                name = ""
                renaming = False
                rename_index = None
                return

            elif event.key == pygame.K_ESCAPE:
                name = ""
                renaming = False
                rename_index = None
                return

            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
                return

            else:
                if event.unicode.isprintable():
                    name += event.unicode

                return

        if saving:
            if event.key == pygame.K_RETURN:
                if name != "":
                    preset = {"name": name,
                            "body_count": len(bodies),
                            "bodies": []
                        }

                    for body in bodies:
                        preset["bodies"].append({
                            "x": body["pos"][0],
                            "y": body["pos"][1],
                            "vel_x": body["vel"][0],
                            "vel_y": body["vel"][1],
                            "mass": body["mass"],
                            "vector_x": body["vector"][0],
                            "vector_y": body["vector"][1]
                        })

                    presets.append(preset)

                    with open(PRESET_FILE, "w") as file:
                        json.dump(presets, file, indent=4)

                    name = ""
                    saving = False

                return

            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
                return

            else:
                name += event.unicode
                return
        
        if event.key == pygame.K_r:
            if running:
                running = False

            load_default_preset()

            return

        if not running:
            if event.key == pygame.K_SPACE:
                mouse_pos = np.array(pygame.mouse.get_pos(), dtype=float)

                display_body = None

                for body in bodies:
                    screen_pos = world_to_screen(body["pos"])
                    distance = np.linalg.norm(mouse_pos - screen_pos)

                    if distance <= body["radius"]:
                        display_body = body
                        break

                return

            if editing_mass:
                if event.key == pygame.K_RETURN:
                    if mass_input != "":
                        display_body["mass"] = float(mass_input)

                    editing_mass = False

                elif event.key == pygame.K_BACKSPACE:
                    mass_input = mass_input[:-1]

                elif event.unicode in "0123456789.":
                    mass_input += event.unicode

                return

            if editing_pos_x:
                if event.key == pygame.K_RETURN:
                    if pos_x_input != "":
                        display_body["pos"][0] = float(pos_x_input)

                    editing_pos_x = False

                elif event.key == pygame.K_BACKSPACE:
                    pos_x_input = pos_x_input[:-1]

                elif event.unicode in "0123456789.":
                    pos_x_input += event.unicode

                return

            if editing_pos_y:
                if event.key == pygame.K_RETURN:
                    if pos_y_input != "":
                        display_body["pos"][1] = float(pos_y_input)

                    editing_pos_y = False

                elif event.key == pygame.K_BACKSPACE:
                    pos_y_input = pos_y_input[:-1]

                elif event.unicode in "0123456789.":
                    pos_y_input += event.unicode

                return

            if editing_vel_x:
                if event.key == pygame.K_RETURN:
                    if vel_x_input != "":
                        display_body["vel"][0] = float(vel_x_input)

                    update_velocity_vector()
                    editing_vel_x = False

                elif event.key == pygame.K_BACKSPACE:
                    vel_x_input = vel_x_input[:-1]

                elif event.unicode in "0123456789.":
                    vel_x_input += event.unicode

                return

            if editing_vel_y:
                if event.key == pygame.K_RETURN:
                    if vel_y_input != "":
                        display_body["vel"][1] = float(vel_y_input)

                    update_velocity_vector()
                    editing_vel_y = False

                elif event.key == pygame.K_BACKSPACE:
                    vel_y_input = vel_y_input[:-1]

                elif event.unicode in "0123456789.":
                    vel_y_input += event.unicode

                return

            if editing_speed:
                if event.key == pygame.K_RETURN:
                    if speed_input != "":
                        speed = float(speed_input)
                        angle = get_angle(display_body)
                        set_speed_angle(display_body, speed, angle)

                    editing_speed = False

                elif event.key == pygame.K_BACKSPACE:
                    speed_input = speed_input[:-1]

                elif event.unicode in "0123456789.":
                    speed_input += event.unicode

                return

            if editing_angle:
                if event.key == pygame.K_RETURN:
                    if angle_input != "":
                        angle = float(angle_input)
                        speed = get_speed(display_body)
                        set_speed_angle(display_body, speed, angle)

                    editing_angle = False

                elif event.key == pygame.K_BACKSPACE:
                    angle_input = angle_input[:-1]

                elif event.unicode in "0123456789.":
                    angle_input += event.unicode

                return


            if event.key == pygame.K_BACKSPACE:
                if pygame.mouse.get_pos()[0] >= 800:
                    button_height = 40
                    button_spacing = 10
                    start_y = 65 - preset_scroll

                    for i in range(len(presets)):
                        y = start_y + i * (button_height + button_spacing)

                        if pygame.mouse.get_pos()[0] >= 815 and pygame.mouse.get_pos()[0] <= 985 and pygame.mouse.get_pos()[1] >= y and pygame.mouse.get_pos()[1] <= y + button_height:
                            delet_preset(i)
                            running = False
                            return

            if event.key == pygame.K_RETURN and not renaming and not saving:
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

        body["pos"][0] = data["x"]
        body["pos"][1] = data["y"]
        body["vel"] = np.array([data["vel_x"], data["vel_y"]])
        body["mass"] = data["mass"]
        body["vector"] = np.array([data["vector_x"], data["vector_y"]])
        body["trail"].clear() 

        
        for body in bodies:
            body["trail"].clear()

def load_preset(index):
    global display_body

    if index < 0 or index >= len(presets):
        return

    preset = presets[index]

    body_count = preset.get("body_count", len(preset["bodies"]))

    set_body_count(body_count)

    for i in range(body_count):
        body = bodies[i]
        data = preset["bodies"][i]

        body["pos"][0] = data["x"]
        body["pos"][1] = data["y"]

        body["vel"] = np.array([
            data["vel_x"],
            data["vel_y"]
        ])

        body["mass"] = data["mass"]

        body["vector"] = np.array([
            data["vector_x"],
            data["vector_y"]
        ])

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


setup()

while True:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_released(event)

        elif event.type == pygame.KEYDOWN:
            key_pressed(event)

    if help_window is not None:
        try:
            help_window.update()
        except tk.TclError:
            help_window = None
            
    draw()
    pygame.display.flip()

