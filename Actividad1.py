import matplotlib.pyplot as plt

def mrua(x_0, v_0, a):
    tiempos = []
    posiciones = []

    for t in range(101):
        tiempos.append(t)
        posiciones.append(x_0 + v_0 * t + 0.5 * a * t**2)

    return tiempos, posiciones


def mrua_aprox(x_0, v_0, a, dt, t_final):
    tiempos = []
    posiciones = []

    x = x_0
    v = v_0
    t = 0

    while t <= t_final:
        tiempos.append(t)
        posiciones.append(x)

        x += v * dt
        v += a * dt
        t += dt

    return tiempos, posiciones

t1, x1 = mrua(0, 2, 1)

# 1 paso por segundo
t2, x2 = mrua_aprox(0, 2, 1, 1, 100)
plt.plot(t2, x2, "--", label="Euler (dt=1)")

# 5 pasos por segundo
t2, x2 = mrua_aprox(0, 2, 1, 0.2, 100)
plt.plot(t2, x2, "--", label="Euler (dt=0.2)")

# 10 pasos por segundo
t2, x2 = mrua_aprox(0, 2, 1, 0.1, 100)
plt.plot(t2, x2, "--", label="Euler (dt=0.1)")

plt.plot(t1, x1, linewidth=2, label="Exacta")

plt.title("MRUA: Solución exacta vs Euler")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición (m)")
plt.grid(True)
plt.legend()

plt.show()