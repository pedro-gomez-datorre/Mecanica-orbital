import py5

bodies = []

GM = 100
dt = 0.1
TRAIL_LENGTH = 300


def setup():
    py5.size(600, 600)

    bodies.append({
        "pos": py5.Py5Vector(150, 500),
        "vel": py5.Py5Vector(0, -1),
        "mass": 100,
        "radius": 15,
        "color": py5.color(255, 0, 0),
        "trail": []
    })

    bodies.append({
        "pos": py5.Py5Vector(500, 500),
        "vel": py5.Py5Vector(0, 1),
        "mass": 100,
        "radius": 15,
        "color": py5.color(0, 150, 255),
        "trail": []
    })

    bodies.append({
        "pos": py5.Py5Vector(300, 200),
        "vel": py5.Py5Vector(1.4, 0),
        "mass": 200,
        "radius": 15,
        "color": py5.color(0, 200, 0),
        "trail": []
    })


def draw():
    py5.background(255)

    update_bodies()

    py5.no_fill()
    py5.stroke_weight(2)

    for body in bodies:
        py5.stroke(body["color"])

        py5.begin_shape()

        for p in body["trail"]:
            py5.vertex(p.x, p.y)

        py5.end_shape()

    # Draw bodies
    py5.no_stroke()

    for body in bodies:
        py5.fill(body["color"])

        py5.circle(
            body["pos"].x,
            body["pos"].y,
            body["radius"] * 2
        )


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

    # Update velocity and position
    for i in range(len(bodies)):
        bodies[i]["vel"] += acc[i] * dt

        bodies[i]["pos"] += bodies[i]["vel"] * dt

        bodies[i]["trail"].append(
            bodies[i]["pos"].copy
        )

        # Limit trail length
        if len(bodies[i]["trail"]) > TRAIL_LENGTH:
            bodies[i]["trail"].pop(0)


py5.run_sketch()