import traceback
import adi
import numpy as np
import time

# === Encoding/Decoding ===
def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join([chr(int(c, 2)) if len(c) == 8 else '?' for c in chars])

def bits_to_bytes_list(bits):
    return [int(bits[i:i+8], 2) for i in range(0, len(bits), 8) if len(bits[i:i+8]) == 8]

def hamming_distance(s1, s2):
    if len(s1) != len(s2):
        return None
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def parity_check(byte_bits):
    return byte_bits.count('1') % 2 == 0

# === Modulation ===
def bpsk_modulate(bits, oversample=10):
    symbols = np.array([1.0 if bit == '1' else -1.0 for bit in bits], dtype=np.complex64)
    return np.repeat(symbols, oversample)

def bpsk_demodulate(samples, oversample=10):
    samples -= np.mean(samples)
    samples = samples[:len(samples)//oversample*oversample]
    samples_reshaped = samples.reshape(-1, oversample)
    avg_samples = samples_reshaped.mean(axis=1)
    return ''.join(['1' if x.real > 0 else '0' for x in avg_samples])

# === Sync using correlation ===
def align_to_preamble(samples, preamble_symbols, oversample):
    corr = np.correlate(samples.real, preamble_symbols.real, mode='valid')
    peak = np.argmax(np.abs(corr))
    return peak - (peak % oversample), corr

# === PlutoSDR setup ===
pluto = adi.Pluto("usb:2.6.5")

sample_rate = int(1e6)
center_freq = int(915e6)
bandwidth = int(0.8e6)
oversample = 10

pluto.tx_lo = center_freq
pluto.tx_rf_bandwidth = bandwidth
pluto.tx_sample_rate = sample_rate
pluto.tx_cyclic_buffer = False

# Adjust TX gain - try -2 dB to avoid clipping
pluto.tx_hardwaregain = -2  # previously -5

pluto.rx_lo = center_freq
pluto.rx_rf_bandwidth = bandwidth
pluto.rx_sample_rate = sample_rate
pluto.rx_enabled_channels = [0]

pluto.rx_buffer_size = 65536

# Increase RX gain (if hardware gain control exposed)
try:
    pluto.rx_hardwaregain = 20
except Exception as e:
    print(f"⚠ Could not set RX gain: {e}")

# === Transmission Config ===
preamble = "10101010" * 8
message = "HELLO"
preamble_bits = text_to_bits(preamble)
message_bits = text_to_bits(message)
all_bits = preamble_bits + message_bits

mod_signal = bpsk_modulate(all_bits, oversample=oversample) * 0.2
preamble_symbols = bpsk_modulate(preamble_bits, oversample=oversample)

for i in range(3):
    print(f"\n[Attempt {i+1}] Transmitting: {message}")

    print(f"TX signal max: {np.max(mod_signal):.3f}, min: {np.min(mod_signal):.3f}")
    pluto.tx(mod_signal)

    tx_time = time.time()
    print(f"TX timestamp: {tx_time:.6f}")

    # Add a small delay after TX to ensure hardware is settled
    time.sleep(0.3)

    rx_samples = pluto.rx()
    rx_time = time.time()
    print(f"RX timestamp: {rx_time:.6f}, RX delay: {(rx_time - tx_time)*1000:.1f} ms")

    print(f"RX samples length: {len(rx_samples)}")
    print(f"RX samples raw stats: min={np.min(rx_samples):.4f}, max={np.max(rx_samples):.4f}, mean={np.mean(rx_samples):.4f}, std={np.std(rx_samples):.4f}")

    # Optional: apply simple DC offset correction on complex samples
    rx_samples -= np.mean(rx_samples.real) + 1j * np.mean(rx_samples.imag)

    # Normalize RX samples: zero mean, unit variance
    rx_samples -= np.mean(rx_samples)
    rx_samples /= np.std(rx_samples)

    print(f"RX samples normalized stats: min={np.min(rx_samples):.4f}, max={np.max(rx_samples):.4f}, mean={np.mean(rx_samples):.4f}, std={np.std(rx_samples):.4f}")

    try:
        start, corr = align_to_preamble(rx_samples, preamble_symbols, oversample)
        print(f"Correlation array shape: {corr.shape}, first 10 values: {corr[:10]}")
        print(f"Max correlation: {np.max(np.abs(corr)):.2f} at index {np.argmax(np.abs(corr))}")
        print(f"Aligned start index: {start}")

        end = start + oversample * len(all_bits)
        if end > len(rx_samples):
            print("⚠ Signal clipped")
            continue

        segment = rx_samples[start:end]
        print(f"Segment power: {np.mean(np.abs(segment)**2):.4f}")

        rx_bits = bpsk_demodulate(segment, oversample)

        print(f"Received bits length: {len(rx_bits)}")
        print(f"Bits: {rx_bits}")

        if len(rx_bits) == len(all_bits):
            bit_errors = hamming_distance(rx_bits, all_bits)
            ber = bit_errors / len(all_bits) if bit_errors is not None else None
            print(f"Bit errors vs transmitted bits: {bit_errors} / {len(all_bits)} (BER={ber:.4f})")
        else:
            print(f"⚠ Received bits length ({len(rx_bits)}) differs from transmitted bits length ({len(all_bits)})")

        payload_bits = rx_bits[len(preamble_bits):len(preamble_bits)+len(message_bits)]
        print(f"Payload bits length: {len(payload_bits)}")

        if len(payload_bits) < len(message_bits):
            print("❌ Too few bits received")
            continue

        bytes_list = bits_to_bytes_list(payload_bits)
        for idx, b in enumerate(bytes_list):
            byte_bits = payload_bits[idx*8:(idx+1)*8]
            if not parity_check(byte_bits):
                print(f"⚠ Parity check failed for byte {idx}: bits={byte_bits} value={b}")

        decoded = bits_to_text(payload_bits)
        print("✅ Received (text):", decoded)

        print("✅ Received (byte values, hex):", [hex(b) for b in bytes_list])

        try:
            ascii_str = bytes(bytes_list).decode('ascii')
            print("✅ Received (ASCII):", ascii_str)
        except Exception as e:
            print("❌ ASCII decode error:", e)

    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()
