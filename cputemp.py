from gpiozero import CPUTemperature

cpu = CPUTemperature()
print(f"CPU Temperature: {cpu.temperature:.1f} °C")

