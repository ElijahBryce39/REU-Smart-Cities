import adi
import numpy as np
import time

def bits_to_bytes(bits):
    bits = bits[:len(bits) - (len(bits) % 8)]
    return np.packbits(bits, bitorder='big')

def decode_with_sync(iq_samples):
    real_samples = np.real(iq_samples)
    bits = (real_samples > 0).astype(np.uint8)
    byte_array = bits_to_bytes(bits)
    raw_bytes = byte_array.tobytes()

    sync_marker = b"PLUTO|"
    index = raw_bytes.find(sync_marker)
    if index != -1:
        payload = raw_bytes[index + len(sync_marker):]
        try:
            return payload.decode('ascii', errors='ignore').strip()
        except UnicodeDecodeError:
            return "[Decode error]"
    return ""

def main():
    print("Connecting to PlutoSDR receiver...")
    sdr = adi.Pluto("usb:2.3.5")  # Adjust USB ID if needed
    sdr.rx_lo = int(915e6)
    sdr.sample_rate = int(1e6)
    sdr.rx_rf_bandwidth = int(2e6)
    sdr.gain_control_mode = "slow_attack"
    sdr.rx_buffer_size = 8192

    print("Listening for BPSK message...")

    try:
        while True:
            samples = sdr.rx()
            message = decode_with_sync(samples)
            if message:
                print("Received:", message)
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()