#!/bin/bash

sudo apt update && sudo apt install -y \
  gnuradio gr-osmosdr rtl-sdr \
  libiio-utils iio-oscilloscope \
  python3-pip libad9361-dev cmake
