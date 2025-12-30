import time

for i in range(1, 6):
    print(f"\rCargando: {i * 20}%", end=" ", flush=True)
    time.sleep(0.5)