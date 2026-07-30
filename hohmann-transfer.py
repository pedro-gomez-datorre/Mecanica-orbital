import math

G = 6.67e-11
M = 5.97e24

def v_circular(r):
    return math.sqrt(G * M / r)

def v_visviva(r, a):
    return math.sqrt(G * M * (2 / r - 1 / a))

def v(r, a):
    return math.sqrt(G * M * (2 / r - 1 / a))

def T(a):
    return 2 * math.pi * math.sqrt(a ** 3 / (G * M))

def hohmann(r, R):
    a = (r + R) / 2
    
    # primer delta-v
    v1 = v(r, r) # = v_circular(r)
    v2 = v(r, a)
    dv1 = v2 - v1
    
    # segundo delta-v
    v3 = v(R, a)
    v4 = v(R, R)
    dv2 = v4 - v3
    
    duracion = T(a) / 2
    
    texto = f"""
    Δv_1 = {dv1:.2f} m/s
    Δv_2 = {dv2:.2f} m/s
    Duración transferencia = {duracion} s = {duracion//3600} h {(duracion%3600)//60} min {(duracion % 60):.2f} s
    """
    
    print(texto)
    
    return (dv1, dv2)


def bieliptica(r1, r2, r3):
    a1 = (r1 + r2) / 2
    a2 = (r2 + r3) / 2
    
    # primer delta-v
    v1 = v(r1, r1)
    v2 = v(r1, a1)
    dv1 = v2 - v1
    
    # segundo delta-v
    v3 = v(r2, a1)
    v4 = v(r2, a2)
    dv2 = v4 - v3
    
    # tercer delta-v
    v5 = v(r3, a2)
    v6 = v(r3, r3)
    dv3 = v6 - v5
    
    duracion1 = T(a1) / 2
    duracion2 = T(a2) / 2
    
    texto = f"""
    Δv_1 = {dv1:.2f} m/s
    Δv_2 = {dv2:.2f} m/s
    Δv_3 = {dv3:.2f} m/s
    Δv total = {(abs(dv1)+abs(dv2)+abs(dv3)):.2f} m/s
    Duración transferencia 1 = {duracion1} s = {duracion1//3600} h {(duracion1%3600)//60} min {(duracion1 % 60):.2f} s
    Duración transferencia 2 = {duracion2} s = {duracion2//3600} h {(duracion2%3600)//60} min {(duracion2 % 60):.2f} s    
    """
    
    print(texto)
    
    return (dv1, dv2)
    
    
    
    