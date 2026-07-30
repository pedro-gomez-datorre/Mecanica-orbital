import math
G = 6.67*10**-11
M = 5*10**24

def v_circular(r):
    return math.sqrt((G*M/r))

def v_visviva(r, a):
    return math.sqrt(G*M*(2/r-1/a))

def hohmann(r, R):
    a = (r+R)/2

    v1 = v_visviva(r)
    v2 = v_visviva(r, a)
    dv1 = v2-v1

    v3 = v_visviva(R, a)
    v4 = v_circular(R)
    dv2 = v4-v3

    text = f"""
    Orbita de Transferencia
    -radio inicial = {r/1000} km
    -radio final = {a/1000} km
    -semieje mayor = {a/1000} km

    dv1 = {dv1} m/s
    dv2 = {dv2} m/s
    """
    print(text)

hohmann()