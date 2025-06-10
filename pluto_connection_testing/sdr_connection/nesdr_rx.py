import matplotlib.pyplot as plt
import numpy as np
from rtlsdr import RtlSdr

sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.center_freq = 915e6
sdr.gain = 'auto'

fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_xlim(914, 916)  # MHz
ax.set_ylim(-70, 0)
ax.set_title("Live NESDR PSD")
ax.set_xlabel("Frequency (MHz)")
ax.set_ylabel("Power (dB)")

def update(frame):
    samples = sdr.read_samples(256*1024)
    psd, freqs = plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6,
                         Fc=sdr.center_freq/1e6, visible=False)
    line.set_data(freqs, 10 * np.log10(psd))
    return line,

import matplotlib.animation as animation
ani = animation.FuncAnimation(fig, update, interval=1000, blit=True)
plt.tight_layout()
plt.show()
sdr.close()
