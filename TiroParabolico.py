import matplotlib.pyplot as plt

g = -9.8

def tiro_parabolico(vx_0, vy_0):
    tiempo = []
    xx = []
    yy = []

    for tc in range(0, 101):
        t = tc/100
        x = vx_0*t
        y = vy_0*t+1/2*g*t**2

        tiempo.append(t)
        xx.append(x)
        yy.append(y)

    return tiempo, xx, yy

tt, xx, yy = tiro_parabolico(1, 1)
plt.plot(xx, yy, 'b-')
tt, xx, yy = tiro_parabolico(2, 2)
plt.plot(xx, yy, 'b-')
tt, xx, yy = tiro_parabolico(3, 3)
plt.plot(xx, yy, 'b-')
tt, xx, yy = tiro_parabolico(4 ,4)
plt.plot(xx, yy, 'b-')
tt, xx, yy = tiro_parabolico(5 ,5)
plt.plot(xx, yy, 'b-')
plt.show()