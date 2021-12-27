import math
import os

import glob
import tkinter.filedialog as filedialog

import numpy as np
import pandas as pd

pd.set_option("display.max_rows", None, "display.max_columns", None)

file_path = filedialog.askdirectory()
pattern = os.path.join(file_path, '*.csv')
files = glob.glob(pattern)

p_value = 0.8
beginning_frames_dropped_left = 181
beginning_frames_dropped_right = 247

# calculate dropped frames / model accuracy
percent_dropped = []
for file in files:
    df_csv = pd.read_csv(file, index_col=False)
    dropped_frames_mouse_left = 0
    dropped_frames_mouse_right = 0

    for row in df_csv[3:].itertuples():
        if math.isnan(float(row[16])) or float(row[16]) < p_value:
            dropped_frames_mouse_left += 1
        if math.isnan(float(row[4])) or float(row[4]) < p_value:
            dropped_frames_mouse_right += 1
    # get rid of frames where mice not there in beginning
    dropped_frames_mouse_left -= beginning_frames_dropped_left
    dropped_frames_mouse_right -= beginning_frames_dropped_right
    # subtract those frames from total before adding
    percent_dropped.append(dropped_frames_mouse_left / (len(df_csv[3:]) - beginning_frames_dropped_left))
    percent_dropped.append(dropped_frames_mouse_right / (len(df_csv[3:]) - beginning_frames_dropped_right))

print('The average dropped frame percentage is:', sum(percent_dropped) / len(percent_dropped))
print('The average model accuracy is:', 1 - sum(percent_dropped) / len(percent_dropped))

# inches into pixel converter
pixel_length_enclosure = 77
enclosure_length_cm = 10.16
pixel_per_cm = pixel_length_enclosure / enclosure_length_cm
metric_cm = 2
distance_in_pixels = pixel_per_cm * metric_cm

# enclosure corners pixel location
left_enclosure_top_left = (120, 236)
left_enclosure_top_right = (172, 236)
left_enclosure_bottom_left = (120, left_enclosure_top_right[1] + pixel_length_enclosure)
left_enclosure_bottom_right = (172, left_enclosure_top_right[1] + pixel_length_enclosure)

right_enclosure_top_left = (627, 219)
right_enclosure_top_right = (682, 219)
right_enclosure_bottom_left = (627, right_enclosure_top_left[1] + pixel_length_enclosure)
right_enclosure_bottom_right = (682, right_enclosure_top_left[1] + pixel_length_enclosure)

# time measurement criteria
time_criteria_ms = 500
time_criteria_s = time_criteria_ms / 1000
video_frame_rate = 25
# round down for the sake of simplicity because fractional frames aren't exactly practical to calculate this way
required_frames_for_sniffle = math.floor(video_frame_rate * time_criteria_s)

mouse_entry_dict = dict()
trial_counter = 1
for file in files:
    df_csv = pd.read_csv(file, index_col=False)
    left_current_sniffle_frame_counter = 0
    right_current_sniffle_frame_counter = 0
    left_total_sniffle_frames = 0
    right_total_sniffle_frames = 0
    left_sniffle_counter = 0
    right_sniffle_counter = 0
    left_consecutive = False
    right_consecutive = False
    mouse_counter = 1
    left_total_frames = 0
    right_total_frames = 0
    for row in df_csv[3:].itertuples():
        left_mouse_nose_coord = (float(row[14]), float(row[15]))
        right_mouse_nose_coord = (float(row[2]), float(row[3]))

        if not math.isnan(left_mouse_nose_coord[0]) and not math.isnan(left_mouse_nose_coord[1]):
            left_total_frames += 1
        if not math.isnan(right_mouse_nose_coord[0]) and not math.isnan(right_mouse_nose_coord[1]):
            right_total_frames += 1

        if math.dist(left_mouse_nose_coord, left_enclosure_top_left) <= distance_in_pixels or math.dist(
                left_mouse_nose_coord, left_enclosure_top_right) <= distance_in_pixels or math.dist(
            left_mouse_nose_coord,
            left_enclosure_bottom_left) <= distance_in_pixels or math.dist(
            left_mouse_nose_coord, left_enclosure_bottom_right) <= distance_in_pixels:
            left_current_sniffle_frame_counter += 1
            left_consecutive = True
            left_total_sniffle_frames += 1
        else:
            left_consecutive = False

        if not left_consecutive:
            left_current_sniffle_frame_counter = 0

        if left_current_sniffle_frame_counter == required_frames_for_sniffle:
            left_sniffle_counter += 1

        if math.dist(right_mouse_nose_coord, right_enclosure_top_left) <= distance_in_pixels or math.dist(
                right_mouse_nose_coord, right_enclosure_top_right) <= distance_in_pixels or math.dist(
            right_mouse_nose_coord,
            right_enclosure_bottom_left) <= distance_in_pixels or math.dist(
            right_mouse_nose_coord, right_enclosure_bottom_right) <= distance_in_pixels:
            right_current_sniffle_frame_counter += 1
            right_consecutive = True
            right_total_sniffle_frames += 1
        else:
            right_consecutive = False

        if not right_consecutive:
            right_current_sniffle_frame_counter = 0

        if right_current_sniffle_frame_counter == required_frames_for_sniffle:
            right_sniffle_counter += 1

    mouse_entry_dict['trial_' + str(trial_counter) + '_mouse_' + str(mouse_counter)] = [left_sniffle_counter,
                                                                                        left_total_sniffle_frames,
                                                                                        left_total_sniffle_frames / video_frame_rate,
                                                                                        left_total_sniffle_frames / left_total_frames * 100]
    mouse_counter += 1

    mouse_entry_dict['trial_' + str(trial_counter) + '_mouse_' + str(mouse_counter)] = [right_sniffle_counter,
                                                                                        right_total_sniffle_frames,
                                                                                        right_total_sniffle_frames / video_frame_rate,
                                                                                        right_total_sniffle_frames / right_total_frames * 100]
    trial_counter += 1
    # print(mouse_entry_dict)

sniffle_df = pd.DataFrame.from_dict(mouse_entry_dict, orient='index',
                                    columns=['Total Sniffles', 'Total Sniffle Frames', 'Total Sniffle Time in Seconds',
                                             'Percentage of Sniffle Frames'])
print(sniffle_df)
