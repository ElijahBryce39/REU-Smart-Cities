import adi
import numpy as np
import time

sdr = adi.Pluto("usb:2.7.5")
sdr.sample_rate = int(2.5e6)
sdr.tx_rf_bandwidth = int(2e6)
sdr.tx_lo = int(915e6)
sdr.tx_cyclic_buffer = True

N = 1024
t = np.arange(N)
samples = 0.5 * np.exp(2j * np.pi * t / N)  # Complex sine

# Transmit in hardware-looped mode
sdr.tx_cyclic_buffer = True
sdr.tx(samples)  # ONE CALL ONLY
print("Transmitting continuously...")

input("Press Enter to stop...")  # Keep the script alive