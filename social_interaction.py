import glob
import math
import os
from tkinter import filedialog
import pandas as pd
from ast import literal_eval


def avg(corner_one, corner_two):
    """
    Calculates the average (x,y) coordinates from two coordinate pairs
    :param corner_one: The first coordinates (x,y)
    :param corner_two: The second coordinates (x,y)
    :return: The midpoint between the two coordinates
    """
    return int((corner_one[0] + corner_two[0]) / 2), int((corner_one[1] + corner_two[1]) / 2)


def make_midpoints(top_left, top_right, bottom_left, bottom_right, is_left):
    """
    Calculates the the midpoint coordinates for the entire enclosure
    :param top_left: The coordinates of the top-left enclosure corner
    :param top_right: The coordinates of the top-right enclosure corner
    :param bottom_left: The coordinates of the bottom-left enclosure corner
    :param bottom_right: The coordinates of the bottom-right enclosure corner
    :param is_left: A boolean checking for the left or right enclosure
    :return: All the coordinates around the enclosure
    """
    tltr_mid = avg(top_left, top_right)
    blbr_mid = avg(bottom_left, bottom_right)
    trbr_mid = avg(top_right, bottom_right)
    tlbl_mid = avg(top_left, bottom_left)

    tltr_l_mid = avg(tltr_mid, top_left)
    tltr_r_mid = avg(tltr_mid, top_right)
    blbr_l_mid = avg(blbr_mid, bottom_left)
    blbr_r_mid = avg(blbr_mid, bottom_right)
    trbr_u_mid = avg(trbr_mid, top_right)
    trbr_d_mid = avg(trbr_mid, bottom_right)
    tlbl_u_mid = avg(tlbl_mid, top_left)
    tlbl_d_mid = avg(tlbl_mid, bottom_left)

    if is_left:
        return tltr_mid, blbr_mid, trbr_mid, tltr_l_mid, tltr_r_mid, blbr_l_mid, blbr_r_mid, trbr_u_mid, trbr_d_mid
    return tltr_mid, blbr_mid, tlbl_mid, tltr_l_mid, tltr_r_mid, blbr_l_mid, blbr_r_mid, tlbl_u_mid, tlbl_d_mid


def check_distance(mouse_nose_coord, enclosure_points_list, interaction_dist_pixel):
    """
    Checks if the mouse is within the interaction distance for each point around the enclosure
    :param mouse_nose_coord: The mouse's (x,y) nose coordinate
    :param enclosure_points_list: A list of all the enclosure point coordinates for one side
    :param interaction_dist_pixel: The interaction distince in pixel length
    :return: A true or false value, depending if the condition is met
    """
    # iterate through all the points
    for enclosure_point in enclosure_points_list:
        # check if the distance is within interaction distance
        if math.dist(mouse_nose_coord, enclosure_point) <= interaction_dist_pixel:
            return True
    return False


def update_counters(first_col, second_col, enclosure, dist_pix, total_frames_counter, total_sniffle_frames_counter,
                    current_sniffle_frame_counter, sniffle_counter, required_frames):
    """
    Updates all the frame counters if they satisfy the conditions
    :param first_col: The column corresponding to the x position of the mouse's nose
    :param second_col: The column corresponding to the y position of the mouse's nose
    :param enclosure: The list of enclosure coordinates
    :param dist_pix: The interaction distance in pixel length
    :param total_frames_counter: The total amount of frames in the video
    :param total_sniffle_frames_counter: The total amount of sniffles frame for the mouse
    :param current_sniffle_frame_counter: The current amount of frames going towards the sniffle requirement
    :param sniffle_counter: The mouse's total sniffle counter
    :param required_frames: The amount of frames needed for a sniffle bout
    :return: An updated version of the total frame counter, the total sniffle frame counter, the current sniffle frame counter, and the sniffle counter
    """
    mouse_nose_coord = (float(first_col), float(second_col))
    # increment the total frame counter
    if not math.isnan(mouse_nose_coord[0]) and not math.isnan(mouse_nose_coord[1]):
        total_frames_counter += 1
    # if the condition is met, increase current and total sniffle counteres
    if check_distance(mouse_nose_coord, enclosure, dist_pix):
        current_sniffle_frame_counter += 1
        total_sniffle_frames_counter += 1
        consecutive = True
    else:
        consecutive = False

    # if the frames aren't consecutive, reset the counter
    if not consecutive:
        current_sniffle_frame_counter = 0
    # increase the sniffle counter once if the required frames is met
    if current_sniffle_frame_counter == required_frames:
        sniffle_counter += 1

    return total_frames_counter, total_sniffle_frames_counter, current_sniffle_frame_counter, sniffle_counter


def social_interaction(enclosure_conversion, left_enclosure_inputs, right_enclosure_inputs, time_inputs, video_inputs,
                       exp_inputs):
    """
    A function that produces a CSV containing the total sniffles, total sniffle frames, total sniffle time, and percentage of sniffle frames and time
    :param enclosure_conversion: A list of enclosure measurements and interaction distance
    :param left_enclosure_inputs: A list of left enclosure coordinates
    :param right_enclosure_inputs: A list of right enclosure coordinates
    :param time_inputs: The interaction time requirement
    :param video_inputs: The frames per second for the video
    :param exp_inputs: The experimental time for each trial
    """
    # inches-pixel conversion
    enclosure_pixel_length = int(enclosure_conversion[0].get())
    enclosure_cm_length = float(enclosure_conversion[1].get())
    pixel_per_cm = enclosure_pixel_length / enclosure_cm_length
    mouse_interaction_dist_cm = float(enclosure_conversion[2].get())
    distance_in_pixels = pixel_per_cm * mouse_interaction_dist_cm

    # left enclosure
    left_enclosure_top_left = literal_eval(left_enclosure_inputs[0].get())
    left_enclosure_top_right = literal_eval(left_enclosure_inputs[1].get())
    left_enclosure_bottom_left = literal_eval(left_enclosure_inputs[2].get())
    left_enclosure_bottom_right = literal_eval(left_enclosure_inputs[3].get())

    left_enclosure_tltr_middle, left_enclosure_blbr_middle, left_enclosure_trbr_middle, \
    left_enclosure_tltr_left_middle, left_enclosure_tltr_right_middle, left_enclosure_blbr_left_middle, \
    left_enclosure_blbr_right_middle, left_enclosure_trbr_top_middle, \
    left_enclosure_trbr_bottom_middle = make_midpoints(left_enclosure_top_left, left_enclosure_top_right,
                                                       left_enclosure_bottom_left, left_enclosure_bottom_right, True)

    left_enclosure = [left_enclosure_top_left, left_enclosure_top_right, left_enclosure_bottom_left,
                      left_enclosure_bottom_right, left_enclosure_tltr_middle, left_enclosure_blbr_middle,
                      left_enclosure_trbr_middle, left_enclosure_tltr_left_middle, left_enclosure_tltr_right_middle,
                      left_enclosure_blbr_left_middle, left_enclosure_blbr_right_middle, left_enclosure_trbr_top_middle,
                      left_enclosure_trbr_bottom_middle]

    # right enclosure
    right_enclosure_top_left = literal_eval(right_enclosure_inputs[0].get())
    right_enclosure_top_right = literal_eval(right_enclosure_inputs[1].get())
    right_enclosure_bottom_left = literal_eval(right_enclosure_inputs[2].get())
    right_enclosure_bottom_right = literal_eval(right_enclosure_inputs[3].get())

    right_enclosure_tltr_middle, right_enclosure_blbr_middle, right_enclosure_tlbl_middle, \
    right_enclosure_tltr_left_middle, right_enclosure_tltr_right_middle, right_enclosure_blbr_left_middle, \
    right_enclosure_blbr_right_middle, right_enclosure_tlbl_top_middle, \
    right_enclosure_tlbl_bottom_middle = make_midpoints(right_enclosure_top_left, right_enclosure_top_right,
                                                        right_enclosure_bottom_left, right_enclosure_bottom_right,
                                                        False)

    right_enclosure = [right_enclosure_top_left, right_enclosure_top_right, right_enclosure_bottom_left,
                       right_enclosure_bottom_right, right_enclosure_tltr_middle, right_enclosure_blbr_middle,
                       right_enclosure_tlbl_middle, right_enclosure_tltr_left_middle, right_enclosure_tltr_right_middle,
                       right_enclosure_blbr_left_middle, right_enclosure_blbr_right_middle,
                       right_enclosure_tlbl_top_middle, right_enclosure_tlbl_bottom_middle]

    # time criteria
    time_criteria_ms = int(time_inputs.get())
    time_criteria_s = time_criteria_ms / 1000

    # video information
    video_fps = int(video_inputs.get())

    # experiment criteria
    trial_runtime_s = int(exp_inputs.get())
    # round down for the sake of simplicity because fractional frames aren't possible
    required_frames_for_sniffle = math.floor(video_fps * time_criteria_s)

    # finding directory
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    mouse_entry = dict()
    mouse_entry_missed = dict()

    for index, file in enumerate(files):
        df_csv = pd.read_csv(file, index_col=False)
        # left mouse counters
        left_current_sniffle_frame_counter, left_total_sniffle_frames, left_sniffle_counter, left_total_frames = 0, 0, 0, 0
        # right mouse counters
        right_current_sniffle_frame_counter, right_total_sniffle_frames, right_sniffle_counter, right_total_frames = 0, 0, 0, 0
        # left missed mouse counters
        left_missed_current_sniffle_frame_counter, left_missed_total_sniffle_frames, left_missed_sniffle_counter, left_missed_total_frames = 0, 0, 0, 0
        # right missed mouse counters
        right_missed_current_sniffle_frame_counter, right_missed_total_sniffle_frames, right_missed_sniffle_counter, right_missed_total_frames = 0, 0, 0, 0
        # other counters
        mouse_counter = 1

        # iterate through all the rows and update the counters
        for row in df_csv[3:].itertuples():
            left_total_frames, left_total_sniffle_frames, \
            left_current_sniffle_frame_counter, left_sniffle_counter = update_counters(row[14], row[15], left_enclosure,
                                                                                       distance_in_pixels,
                                                                                       left_total_frames,
                                                                                       left_total_sniffle_frames,
                                                                                       left_current_sniffle_frame_counter,
                                                                                       left_sniffle_counter,
                                                                                       required_frames_for_sniffle)
            right_total_frames, right_total_sniffle_frames, \
            right_current_sniffle_frame_counter, right_sniffle_counter = update_counters(row[2], row[3],
                                                                                         right_enclosure,
                                                                                         distance_in_pixels,
                                                                                         right_total_frames,
                                                                                         right_total_sniffle_frames,
                                                                                         right_current_sniffle_frame_counter,
                                                                                         right_sniffle_counter,
                                                                                         required_frames_for_sniffle)
            left_missed_total_frames, left_missed_total_sniffle_frames, \
            left_missed_current_sniffle_frame_counter, left_missed_sniffle_counter = update_counters(row[2], row[3],
                                                                                                     left_enclosure,
                                                                                                     distance_in_pixels,
                                                                                                     left_missed_total_frames,
                                                                                                     left_missed_total_sniffle_frames,
                                                                                                     left_missed_current_sniffle_frame_counter,
                                                                                                     left_missed_sniffle_counter,
                                                                                                     required_frames_for_sniffle)
            right_missed_total_frames, right_missed_total_sniffle_frames, \
            right_missed_current_sniffle_frame_counter, right_missed_sniffle_counter = update_counters(row[14], row[15],
                                                                                                       right_enclosure,
                                                                                                       distance_in_pixels,
                                                                                                       right_missed_total_frames,
                                                                                                       right_missed_total_sniffle_frames,
                                                                                                       right_missed_current_sniffle_frame_counter,
                                                                                                       right_missed_sniffle_counter,
                                                                                                       required_frames_for_sniffle)

        # update information for each mouse
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
    """
    Creates the UI for the social interaction functionality
    :param tk:
    :param root:
    """
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
