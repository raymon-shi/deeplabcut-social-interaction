import glob
import math
import os
from tkinter import filedialog
import pandas as pd
from ast import literal_eval


def social_interaction(enclosure_conversion, left_enclosure_inputs, right_enclosure_inputs, time_inputs, video_inputs,
                       exp_inputs):
    # inches-pixel conversion
    enclosure_pixel_length = int(enclosure_conversion[0].get())
    enclosure_cm_length = float(enclosure_conversion[1].get())
    pixel_per_cm = enclosure_pixel_length / enclosure_cm_length
    mouse_interaction_dist_cm = float(enclosure_conversion[2].get())
    distance_in_pixels = pixel_per_cm * mouse_interaction_dist_cm

    # enclosure corner pixel location
    # left enclosure
    left_enclosure_top_left = literal_eval(left_enclosure_inputs[0].get())
    left_enclosure_top_right = literal_eval(left_enclosure_inputs[1].get())
    left_enclosure_bottom_left = literal_eval(left_enclosure_inputs[2].get())
    left_enclosure_bottom_right = literal_eval(left_enclosure_inputs[3].get())
    left_enclosure = [left_enclosure_top_left, left_enclosure_top_right, left_enclosure_bottom_left,
                      left_enclosure_bottom_right]

    # right enclosure
    right_enclosure_top_left = literal_eval(right_enclosure_inputs[0].get())
    right_enclosure_top_right = literal_eval(right_enclosure_inputs[1].get())
    right_enclosure_bottom_left = literal_eval(right_enclosure_inputs[2].get())
    right_enclosure_bottom_right = literal_eval(right_enclosure_inputs[3].get())
    right_enclosure = [right_enclosure_top_left, right_enclosure_top_right, right_enclosure_bottom_left,
                       right_enclosure_bottom_right]

    # time criteria
    time_criteria_ms = int(time_inputs.get())
    time_criteria_s = time_criteria_ms / 1000

    # video information
    video_fps = int(video_inputs.get())

    # experiment criteria
    trial_runtime_s = int(exp_inputs.get())
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
            if math.dist(right_missed_mouse_nose_coord, right_enclosure_top_left) <= distance_in_pixels or math.dist(
                    right_missed_mouse_nose_coord, right_enclosure_top_right) <= distance_in_pixels or math.dist(
                right_missed_mouse_nose_coord,
                right_enclosure_bottom_left) <= distance_in_pixels or math.dist(
                right_missed_mouse_nose_coord, right_enclosure_bottom_right) <= distance_in_pixels:
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


def make_social_interaction_buttons(tk, root):
    si_enclosure_pixel_label = tk.Label(root, text='Enter enclosure length in pixels:')
    si_enclosure_pixel_label.grid(row=0, column=0)
    si_enclosure_pixel_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_pixel_entry.grid(row=0, column=1)

    si_enclosure_cm_label = tk.Label(root, text='Enter enclosure length in cm:')
    si_enclosure_cm_label.grid(row=1, column=0)
    si_enclosure_cm_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_cm_entry.grid(row=1, column=1)

    si_interaction_dist_label = tk.Label(root, text='Enter interaction distance in cm:')
    si_interaction_dist_label.grid(row=2, column=0)
    si_interaction_dist_entry = tk.Entry(root, width=30, justify='center')
    si_interaction_dist_entry.grid(row=2, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=3, column=0)

    conversion_details = [si_enclosure_pixel_entry, si_enclosure_cm_entry, si_interaction_dist_entry]

    si_enclosure_left_tl_label = tk.Label(root, text='Enter left-enclosure top-left coordinates as (x,y):')
    si_enclosure_left_tl_label.grid(row=4, column=0)
    si_enclosure_left_tl_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_left_tl_entry.grid(row=4, column=1)

    si_enclosure_left_tr_label = tk.Label(root, text='Enter left-enclosure top-right coordinates as (x,y):')
    si_enclosure_left_tr_label.grid(row=5, column=0)
    si_enclosure_left_tr_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_left_tr_entry.grid(row=5, column=1)

    si_enclosure_left_bl_label = tk.Label(root, text='Enter left-enclosure bottom-left coordinates as (x,y):')
    si_enclosure_left_bl_label.grid(row=6, column=0)
    si_enclosure_left_bl_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_left_bl_entry.grid(row=6, column=1)

    si_enclosure_left_br_label = tk.Label(root, text='Enter left-enclosure bottom-right coordinates as (x,y):')
    si_enclosure_left_br_label.grid(row=7, column=0)
    si_enclosure_left_br_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_left_br_entry.grid(row=7, column=1)

    spacer_btn_2 = tk.Label(root, text='')
    spacer_btn_2.grid(row=8, column=0)

    left_enclosure_details = [si_enclosure_left_tl_entry, si_enclosure_left_tr_entry, si_enclosure_left_bl_entry,
                              si_enclosure_left_br_entry]

    si_enclosure_right_tl_label = tk.Label(root, text='Enter right-enclosure top-left coordinates as (x,y):')
    si_enclosure_right_tl_label.grid(row=9, column=0)
    si_enclosure_right_tl_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_right_tl_entry.grid(row=9, column=1)

    si_enclosure_right_tr_label = tk.Label(root, text='Enter right-enclosure top-right coordinates as (x,y):')
    si_enclosure_right_tr_label.grid(row=10, column=0)
    si_enclosure_right_tr_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_right_tr_entry.grid(row=10, column=1)

    si_enclosure_right_bl_label = tk.Label(root, text='Enter right-enclosure bottom-left coordinates as (x,y):')
    si_enclosure_right_bl_label.grid(row=11, column=0)
    si_enclosure_right_bl_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_right_bl_entry.grid(row=11, column=1)

    si_enclosure_right_br_label = tk.Label(root, text='Enter right-enclosure bottom-right coordinates as (x,y):')
    si_enclosure_right_br_label.grid(row=12, column=0)
    si_enclosure_right_br_entry = tk.Entry(root, width=30, justify='center')
    si_enclosure_right_br_entry.grid(row=12, column=1)

    spacer_btn_3 = tk.Label(root, text='')
    spacer_btn_3.grid(row=13, column=0)

    right_enclosure_details = [si_enclosure_right_tl_entry, si_enclosure_right_tr_entry, si_enclosure_right_bl_entry,
                               si_enclosure_right_br_entry]

    si_interaction_time_label = tk.Label(root, text='Enter the interaction time in ms:')
    si_interaction_time_label.grid(row=14, column=0)
    si_interaction_time_entry = tk.Entry(root, width=30, justify='center')
    si_interaction_time_entry.grid(row=14, column=1)

    si_video_fps_label = tk.Label(root, text='Enter the video fps:')
    si_video_fps_label.grid(row=15, column=0)
    si_video_fps_entry = tk.Entry(root, width=30, justify='center')
    si_video_fps_entry.grid(row=15, column=1)

    si_exp_time_label = tk.Label(root, text='Enter the experiment trial time in seconds:')
    si_exp_time_label.grid(row=16, column=0)
    si_exp_time_entry = tk.Entry(root, width=30, justify='center')
    si_exp_time_entry.grid(row=16, column=1)

    si_csv_btn = tk.Button(root, text='Make SI CSV',
                           command=lambda: social_interaction(conversion_details, left_enclosure_details,
                                                              right_enclosure_details, si_interaction_time_entry,
                                                              si_video_fps_entry, si_exp_time_entry))
    si_csv_btn.grid(row=18, column=0, columnspan=2)
