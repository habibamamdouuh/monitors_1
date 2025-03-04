import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from matplotlib.animation import FuncAnimation

# Load the signal
file_path = r'Downloads\all_emg_values.txt'
data = pd.read_csv(file_path, header=None, skiprows=1)
signal = data[0].values

# Step 1: Remove DC Offset
signal = signal - np.mean(signal)

# Step 2: Bandpass Filter
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

sampling_rate = 1000  # Adjust as needed
filtered_signal = bandpass_filter(signal, 20, 450, sampling_rate)

# Step 3: Rectify the Signal
rectified_signal = np.abs(filtered_signal)

# Step 4: Smooth the Signal
window_size = 50  # Adjust based on your data
smoothed_signal = np.convolve(rectified_signal, np.ones(window_size) / window_size, mode='same')

# Threshold for detecting flexions
threshold = 0.5 * np.max(smoothed_signal)  # Dynamic threshold
flexion_count = 0
flexion_indices = []
flexion_times = []
refractory_period = int(sampling_rate * 0.5)  # 500 ms refractory period
last_flexion_index = -refractory_period

# Real-time plotting setup
window_size = 200  # Number of points to display at a time
time_interval = 1000 / sampling_rate  # Time interval between updates in ms

# Create figure for plotting
plt.style.use('dark_background')  # Set a dark theme
fig, ax = plt.subplots(figsize=(12, 6))
x_data = np.arange(0, window_size)
y_data = np.zeros(window_size)
line, = ax.plot(x_data, y_data, label='Filtered Signal', color='red', linewidth=1.5)
threshold_line = ax.axhline(y=threshold, color='blue', linestyle='--', label='Threshold')
ax.set_xlim(0, window_size)
ax.set_ylim(np.min(filtered_signal), np.max(filtered_signal))
ax.set_title('Real-Time EMG Signal Monitoring', fontsize=16, color='white')
ax.set_xlabel('Sample Index', fontsize=12, color='white')
ax.set_ylabel('Amplitude', fontsize=12, color='white')
ax.legend(loc='upper right', fontsize=10)
ax.grid(color='gray', linestyle='--', linewidth=0.5)

# Display flexion count and status dynamically
flexion_text = ax.text(0.02, 0.95, f'Flexions: {flexion_count}', transform=ax.transAxes, fontsize=12, color='lime', verticalalignment='top')
time_text = ax.text(0.02, 0.90, f'Time: 0.00 s', transform=ax.transAxes, fontsize=12, color='white', verticalalignment='top')
status_text = ax.text(0.02, 0.85, f'Status: Monitoring', transform=ax.transAxes, fontsize=12, color='cyan', verticalalignment='top')

# Flexion markers
marker_style = dict(color='cyan', linestyle='-', linewidth=1.5, alpha=0.7)

def update(frame):
    global flexion_count, last_flexion_index, flexion_indices, flexion_times

    # Define the window of data to display
    start_index = frame
    end_index = frame + window_size
    if end_index > len(filtered_signal):
        ani.event_source.stop()  # Stop when the signal ends
        status_text.set_text('Status: Finished')
    else:
        # Update the signal window
        current_window = smoothed_signal[start_index:end_index]
        line.set_ydata(filtered_signal[start_index:end_index])

        # Flexion detection in the current window
        for i in range(start_index, end_index):
            if smoothed_signal[i] > threshold and (i - last_flexion_index > refractory_period):
                flexion_count += 1
                flexion_indices.append(i)
                flexion_times.append(i / sampling_rate)  # Time in seconds
                last_flexion_index = i
                # Add a marker for the detected flexion
                ax.axvline(x=i - start_index, **marker_style)

        # Update flexion count display
        flexion_text.set_text(f'Flexions: {flexion_count}')
        time_text.set_text(f'Time: {frame / sampling_rate:.2f} s')

    return line, threshold_line, flexion_text, time_text, status_text

# Animation
ani = FuncAnimation(fig, update, frames=np.arange(0, len(filtered_signal) - window_size), interval=time_interval, blit=True)

plt.show()

# Output final flexion information
print(f"Total Flexions Detected: {flexion_count}")
print("Flexion Positions (Sample Indices):", flexion_indices)
print("Flexion Times (Seconds):", flexion_times)