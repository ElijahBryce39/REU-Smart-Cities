from gnuradio import analog, blocks, gr, osmosdr
import numpy as np

class PlutoTransmitter(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        self.sample_rate = 2.5e6
        self.center_freq = 915e6

        # Generate complex sine
        self.signal = analog.sig_source_c(
            self.sample_rate, analog.GR_COS_WAVE, 100e3, 0.5, 0
        )

        self.pluto_sink = osmosdr.sink(args="pluto=0")
        self.pluto_sink.set_sample_rate(self.sample_rate)
        self.pluto_sink.set_center_freq(self.center_freq)
        self.pluto_sink.set_gain_mode(False)
        self.pluto_sink.set_gain(30)

        self.connect(self.signal, self.pluto_sink)

if __name__ == '__main__':
    tb = PlutoTransmitter()
    tb.start()
    input("Transmitting... Press Enter to stop.")
    tb.stop()
    tb.wait()
