import adi
import numpy as np
import matplotlib.pyplot as plt
import time

# Connect to the receiving Pluto device
sdr = adi.Pluto("usb:2.9.5")  # Update if needed

# SDR receive configuration (must match transmitter)
sdr.rx_lo = int(915e6)
sdr.sample_rate = int(2.5e6)
sdr.rx_rf_bandwidth = int(2e6)
sdr.rx_buffer_size = 1024
sdr.gain_control_mode = "slow_attack"

print("Starting real-time plot...")

# Set up live plot
plt.ion()
fig, ax = plt.subplots()
line_i, = ax.plot([], [], label="I")
line_q, = ax.plot([], [], label="Q")
ax.set_title("Live Received I/Q Signal")
ax.set_xlim(0, sdr.rx_buffer_size)
ax.set_ylim(-100, 100)
ax.grid(True)
ax.legend()

# Continuously update the plot
try:
    while True:
        samples = sdr.rx()
        line_i.set_ydata(np.real(samples))
        line_q.set_ydata(np.imag(samples))
        line_i.set_xdata(np.arange(len(samples)))
        line_q.set_xdata(np.arange(len(samples)))
        ax.relim()
        ax.autoscale_view(scalex=False)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.0001)  # Adjust refresh interval
except KeyboardInterrupt:
    print("Stopping...")
    plt.ioff()
    plt.show()
