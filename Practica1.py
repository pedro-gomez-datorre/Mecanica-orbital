import numpy as np

mu = 398600.4418  # km³/s² (Tierra)
r = np.array([7000, 0, 0])  # km
v = np.array([0, 7.546, 0])  # km/s

energia = np.linalg.norm(v)**2 / 2 - mu / np.linalg.norm(r)
print(energia)