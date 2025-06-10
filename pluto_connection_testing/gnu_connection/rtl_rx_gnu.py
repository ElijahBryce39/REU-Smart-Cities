from gnuradio import analog, blocks, gr, qtgui, osmosdr
from PyQt5 import Qt
import sys
import sip

class RtlReceiver(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        self.sample_rate = 2.4e6
        self.center_freq = 915e6

        # Blocks
        self.rtlsdr = osmosdr.source(args="numchan=1")
        self.rtlsdr.set_sample_rate(self.sample_rate)
        self.rtlsdr.set_center_freq(self.center_freq)
        self.rtlsdr.set_gain_mode(True)

        self.qtgui_sink = qtgui.sink_c(
            1024, "Freq Spectrum", True, True, True, True
        )
        self.qtgui_sink.set_update_time(0.10)
        self.qtgui_sink.set_frequency_range(self.center_freq, self.sample_rate)

        self.connect(self.rtlsdr, self.qtgui_sink)

if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    tb = RtlReceiver()
    tb.start()
    tb.qtgui_sink.win.show()
    app.exec_()
    tb.stop()
    tb.wait()
