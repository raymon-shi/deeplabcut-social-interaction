import glob
import math
import os
from tkinter import filedialog
import pandas as pd


def social_interaction():
    # inches-pixel conversion
    enclosure_pixel_length = 77
    enclosure_cm_length = 10.16
    pixel_per_cm = enclosure_pixel_length / enclosure_cm_length
    mouse_interaction_dist_cm = 2
    distance_in_pixels = pixel_per_cm * mouse_interaction_dist_cm

    # enclosure corner pixel location
    # left enclosure
    left_enclosure_top_left = (120, 236)
    left_enclosure_top_right = (172, 236)
    left_enclosure_bottom_left = (120, left_enclosure_top_right[1] + enclosure_pixel_length)
    left_enclosure_bottom_right = (172, left_enclosure_top_right[1] + enclosure_pixel_length)
    left_enclosure = [left_enclosure_top_left, left_enclosure_top_right, left_enclosure_bottom_left,
                      left_enclosure_bottom_right]

    # right enclosure
    right_enclosure_top_left = (627, 219)
    right_enclosure_top_right = (682, 219)
    right_enclosure_bottom_left = (627, right_enclosure_top_left[1] + enclosure_pixel_length)
    right_enclosure_bottom_right = (682, right_enclosure_top_left[1] + enclosure_pixel_length)
    right_enclosure = [right_enclosure_top_left, right_enclosure_top_right, right_enclosure_bottom_left,
                       right_enclosure_bottom_right]

    # time criteria
    time_criteria_ms = 500
    time_criteria_s = time_criteria_ms / 1000

    # video information
    video_fps = 25

    # experiment criteria
    trial_runtime_s = 150
    # round down for the sake of simplicity because fractional frames aren't possible
    required_frames_for_sniffle = math.floor(video_fps * time_criteria_s)

    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    mouse_entry = dict()
    mouse_entry_missed = dict()

    for index, file in enumerate(files):
        df_csv = pd.read_csv(file, index_col=False)
        # left mouse counters
        left_current_sniffle_frame_counter, left_total_sniffle_frames, left_sniffle_counter, left_total_frames = 0, 0, 0, 0
        left_consecutive = False
        # right mouse counters
        right_current_sniffle_frame_counter, right_total_sniffle_frames, right_sniffle_counter, right_total_frames = 0, 0, 0, 0
        right_consecutive = False
        # left missed mouse counters
        left_missed_current_sniffle_frame_counter, left_missed_total_sniffle_frames, left_missed_sniffle_counter, left_missed_total_frames = 0, 0, 0, 0
        left_missed_consecutive = False
        # right missed mouse counters
        right_missed_current_sniffle_frame_counter, right_missed_total_sniffle_frames, right_missed_sniffle_counter, right_missed_total_frames = 0, 0, 0, 0
        right_missed_consecutive = False
        # other counters
        mouse_counter = 1
        for row in df_csv[3:].itertuples():
            # left mouse nose x, y
            left_mouse_nose_coord = (float(row[14]), float(row[15]))
            # count left mouse frames that are present
            if not math.isnan(left_mouse_nose_coord[0]) and not math.isnan(left_mouse_nose_coord[1]):
                left_total_frames += 1
            # check if the mouse at most criteria distance away in pixels using euclidean distance
            if math.dist(left_mouse_nose_coord, left_enclosure_top_left) <= distance_in_pixels or math.dist(
                    left_mouse_nose_coord, left_enclosure_top_right) <= distance_in_pixels or math.dist(
                left_mouse_nose_coord,
                left_enclosure_bottom_left) <= distance_in_pixels or math.dist(
                left_mouse_nose_coord, left_enclosure_bottom_right) <= distance_in_pixels:
                left_current_sniffle_frame_counter += 1
                left_total_sniffle_frames += 1
                left_consecutive = True
            else:
                left_consecutive = False
            # reset the current frame counter if not consecutive frames
            if not left_consecutive:
                left_current_sniffle_frame_counter = 0
            # increase the sniffle counter once it reaches the required frame amount
            if left_current_sniffle_frame_counter == required_frames_for_sniffle:
                left_sniffle_counter += 1

            # right mouse nose x, y
            right_mouse_nose_coord = (float(row[2]), float(row[3]))
            # count right mouse frames that are present
            if not math.isnan(right_mouse_nose_coord[0]) and not math.isnan(right_mouse_nose_coord[1]):
                right_total_frames += 1
            # check if the mouse at most criteria distance away in pixels using euclidean distance
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
            # reset the current frame counter if not consecutive frames
            if not right_consecutive:
                right_current_sniffle_frame_counter = 0
            # increase the sniffle counter once it reaches the required frame amount
            if right_current_sniffle_frame_counter == required_frames_for_sniffle:
                right_sniffle_counter += 1

            # the output format from DLC is a bit inconsistent, so we have to catch the ones that we missed
            # left mouse nose x, y
            left_missed_mouse_nose_coord = (float(row[2]), float(row[3]))
            # count left mouse frames that are present
            if not math.isnan(left_missed_mouse_nose_coord[0]) and not math.isnan(left_missed_mouse_nose_coord[1]):
                left_missed_total_frames += 1
            # check if the mouse at most criteria distance away in pixels using euclidean distance
            if math.dist(left_missed_mouse_nose_coord, left_enclosure_top_left) <= distance_in_pixels or math.dist(
                    left_missed_mouse_nose_coord, left_enclosure_top_right) <= distance_in_pixels or math.dist(
                left_missed_mouse_nose_coord,
                left_enclosure_bottom_left) <= distance_in_pixels or math.dist(
                left_missed_mouse_nose_coord, left_enclosure_bottom_right) <= distance_in_pixels:
                left_missed_current_sniffle_frame_counter += 1
                left_missed_total_sniffle_frames += 1
                left_missed_consecutive = True
            else:
                left_missed_consecutive = False
            # reset the current frame counter if not consecutive frames
            if not left_missed_consecutive:
                left_missed_current_sniffle_frame_counter = 0
            # increase the sniffle counter once it reaches the required frame amount
            if left_missed_current_sniffle_frame_counter == required_frames_for_sniffle:
                left_missed_sniffle_counter += 1

            # right mouse nose x, y
            right_missed_mouse_nose_coord = (float(row[14]), float(row[15]))
            # count right mouse frames that are present
            if not math.isnan(right_missed_mouse_nose_coord[0]) and not math.isnan(right_missed_mouse_nose_coord[1]):
                right_missed_total_frames += 1
            # check if the mouse at most criteria distance away in pixels using euclidean distance
            if math.dist(right_missed_mouse_nose_coord, left_enclosure_top_left) <= distance_in_pixels or math.dist(
                    right_missed_mouse_nose_coord, left_enclosure_top_right) <= distance_in_pixels or math.dist(
                right_missed_mouse_nose_coord,
                left_enclosure_bottom_left) <= distance_in_pixels or math.dist(
                right_missed_mouse_nose_coord, left_enclosure_bottom_right) <= distance_in_pixels:
                right_missed_current_sniffle_frame_counter += 1
                right_missed_total_sniffle_frames += 1
                right_missed_consecutive = True
            else:
                right_missed_consecutive = False
            # reset the current frame counter if not consecutive frames
            if not right_missed_consecutive:
                right_missed_current_sniffle_frame_counter = 0
            # increase the sniffle counter once it reaches the required frame amount
            if right_missed_current_sniffle_frame_counter == required_frames_for_sniffle:
                right_missed_sniffle_counter += 1

        mouse_entry['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [left_sniffle_counter,
                                                                                   left_total_sniffle_frames,
                                                                                   left_total_sniffle_frames / video_fps,
                                                                                   left_total_sniffle_frames / left_total_frames * 100,
                                                                                   (
                                                                                           left_total_sniffle_frames / video_fps) / trial_runtime_s * 100]
        mouse_entry_missed['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [left_missed_sniffle_counter,
                                                                                          left_missed_total_sniffle_frames,
                                                                                          left_missed_total_sniffle_frames / video_fps,
                                                                                          left_missed_total_sniffle_frames / left_missed_total_frames * 100,
                                                                                          (
                                                                                                  left_missed_total_sniffle_frames / video_fps) / trial_runtime_s * 100]
        mouse_counter += 1
        mouse_entry['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [right_sniffle_counter,
                                                                                   right_total_sniffle_frames,
                                                                                   right_total_sniffle_frames / video_fps,
                                                                                   right_total_sniffle_frames / right_total_frames * 100,
                                                                                   (
                                                                                           right_total_sniffle_frames / video_fps) / trial_runtime_s * 100]
        mouse_entry_missed['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [right_missed_sniffle_counter,
                                                                                          right_missed_total_sniffle_frames,
                                                                                          right_missed_total_sniffle_frames / video_fps,
                                                                                          right_missed_total_sniffle_frames / right_missed_total_frames * 100,
                                                                                          (
                                                                                                  right_missed_total_sniffle_frames / video_fps) / trial_runtime_s * 100]

    sniffle_df = pd.DataFrame.from_dict(mouse_entry, orient='index',
                                        columns=['Total Sniffles', 'Total Sniffle Frames',
                                                 'Total Sniffle Time in Seconds',
                                                 'Percentage of Sniffle Frames', 'Percentage of Sniffle Time'])

    # filter out all the missed entries
    sniffle_filtered_df = sniffle_df[(sniffle_df['Total Sniffles'] == 0) & (sniffle_df['Total Sniffle Frames'] == 0) & (
            sniffle_df['Total Sniffle Time in Seconds'] == 0) & (
                                             sniffle_df['Percentage of Sniffle Frames'] == 0) & (
                                             sniffle_df['Percentage of Sniffle Time'] == 0)]
    missed_entries = list(sniffle_filtered_df.index)

    sniffle_missed_df = pd.DataFrame.from_dict(mouse_entry_missed, orient='index',
                                               columns=['Total Sniffles', 'Total Sniffle Frames',
                                                        'Total Sniffle Time in Seconds',
                                                        'Percentage of Sniffle Frames', 'Percentage of Sniffle Time'])
    sniffle_missed_series = sniffle_missed_df.index.isin(missed_entries)
    sniffle_missed_df = sniffle_missed_df[sniffle_missed_series]

    # update the missed entries with information
    sniffle_df.update(sniffle_missed_df)

    # save to csv
    save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
    sniffle_df.to_csv(save_file_path)


social_interaction()
