import math

import cv2
import numpy as np
import glob
import tkinter.filedialog as filedialog
import cv2 as cv
import os
import re
from ast import literal_eval
import pandas as pd
from social_interaction import make_midpoints
import cvzone


def check_point(x, y, w, h, enclosure, interaction_dist):
    """
    Check if the center of the mouse's nose is within the interaction distance
    :param x: Top left x coordinate
    :param y: Top left y coordinate
    :param w: The width of the rectangle
    :param h: The height of the rectangle
    :param enclosure: A list containing the coordinates of the enclosure
    :param interaction_dist: The interaction distance to meet a sniffle bout
    :return: A boolean value depending if the condition was met
    """
    for point in enclosure:
        if math.dist((x + .5 * w, y + .5 * h), point) <= interaction_dist:
            return True
    return False


def update_ctr(x_start, x_end, y_start, y_end, l_range, u_range, frame, enclosure, interaction_dist, total_frames,
               current_frames, sniffle_counter, req_frames):
    """
    Updates all the frame counter if they satisfy the conditions
    :param x_start: The starting x position
    :param x_end: The ending x position
    :param y_start: The starting y position
    :param y_end: The ending y position
    :param l_range: The lower HSV range for purple
    :param u_range: the upper HSV range for purple
    :param frame: The working image from OpenCV
    :param enclosure: A list of coordinates for the enclosure
    :param interaction_dist: The interaction distance needed for a sniffle bout
    :param total_frames: The total sniffle frame counter
    :param current_frames: The current frame counter
    :param sniffle_counter: The total sniffle counter
    :param req_frames: The amount of frames needed for a sniffle
    :return: An updated version of all the counters
    """
    # the specific area corresponding to the arena
    area_of_interest = frame[int(y_start.get()):int(y_end.get()), int(x_start.get()):int(x_end.get())]
    hsv = cv.cvtColor(area_of_interest, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, l_range, u_range)
    contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv.contourArea(contour)
        if area > 10:
            x, y, w, h = cv.boundingRect(contour)
            # draw a red box if within the interaction distance
            if check_point(x, y, w, h, enclosure, interaction_dist):
                cv.rectangle(area_of_interest, (x, y), (x + w, y + h), (0, 0, 255), 2)
                consecutive = True
                current_frames += 1
                total_frames += 1
            else:
                # draw a green box otherwise
                consecutive = False
                cv.rectangle(area_of_interest, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # reset if the frames aren't consecutive
            if not consecutive:
                current_frames = 0

            if current_frames == req_frames:
                sniffle_counter += 1
        break

    return total_frames, current_frames, sniffle_counter


def extract_one_frame(left_x_start, left_x_end, left_y_start, left_y_end):
    """
    A function that extracts one frame
    :param left_x_start: The left starting x position
    :param left_x_end: The left ending x position
    :param left_y_start: The left starting y position
    :param left_y_end: The left ending y position
    """
    # asking for file path
    file_path = filedialog.askopenfilename()
    capture = cv.VideoCapture(filename=file_path)
    save_path = filedialog.asksaveasfilename(defaultextension='.jpg', title='Save the Frame')

    # reads the first frame
    exist, frame = capture.read()
    # writes the first frame to save path
    cv.imwrite(save_path,
               frame[int(left_y_start.get()):int(left_y_end.get()), int(left_x_start.get()):int(left_x_end.get())])


def create_live_video(left_x_start, left_x_end, left_y_start, left_y_end, interaction_dist_cm, enclosure_len_pix,
                      enclosure_len_cm, vid_fps, left_enclosure_tl, left_enclosure_tr, left_enclosure_bl,
                      left_enclosure_br, right_x_start, right_x_end, right_y_start, right_y_end, right_enclosure_tl,
                      right_enclosure_tr, right_enclosure_bl, right_enclosure_br, interaction_time):
    """
    A function that analyzes each video, extracts all the frames, and stores the frames in another location
    :param left_x_start: The left starting x position
    :param left_x_end: The left ending x position
    :param left_y_start: The left starting y position
    :param left_y_end: The left ending y position
    :param interaction_dist_cm: The interaction distance in centimeters
    :param enclosure_len_pix: The enclosure length in pixel
    :param enclosure_len_cm: The enclosure length in centimeters
    :param vid_fps: The frames per second in the video
    :param left_enclosure_tl: The top left corner of the left enclosure
    :param left_enclosure_tr: The top right corner of the left enclosure
    :param left_enclosure_bl: The bottom left corner of the left enclosure
    :param left_enclosure_br: The bottom right corner of the left enclosure
    :param right_x_start: The right starting x position
    :param right_x_end: The right ending x position
    :param right_y_start: The right starting y position
    :param right_y_end: The right ending y position
    :param right_enclosure_tl: The top left corner of the right enclosure
    :param right_enclosure_tr: The top right corner of the right enclosure
    :param right_enclosure_bl: The bottom left corner of the right enclosure
    :param right_enclosure_br: The bottom right corner of the right enclosure
    :param interaction_time: The interaction time required for a sniffle
    """
    # asking for directory path and save path
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.mp4')
    files = glob.glob(pattern)
    # files = sorted(glob.glob(pattern),
    #                key=lambda filename: [int(name) if name.isdigit() else name for name in re.split('(\d+)', filename)])

    save_path = filedialog.askdirectory()

    # calculate interaction in pixels
    pix_per_cm = int(enclosure_len_pix.get()) / float(enclosure_len_cm.get())
    interact_dist = int(interaction_dist_cm.get()) * pix_per_cm

    # left enclosure
    left_tl_corner = left_enclosure_tl
    left_tr_corner = left_enclosure_tr
    left_bl_corner = left_enclosure_bl
    left_br_corner = left_enclosure_br

    left_tltr_mid, left_blbr_mid, left_trbr_mid, left_tltr_l_mid, left_tltr_r_mid, left_blbr_l_mid, left_blbr_r_mid, \
    left_trbr_u_mid, left_trbr_d_mid = make_midpoints(left_tl_corner, left_tr_corner, left_bl_corner, left_br_corner,
                                                      True)

    l_enclosure = [left_tl_corner, left_tr_corner, left_bl_corner, left_br_corner, left_tltr_mid, left_blbr_mid,
                   left_trbr_mid, left_tltr_l_mid, left_tltr_r_mid, left_blbr_l_mid, left_blbr_r_mid, left_trbr_u_mid,
                   left_trbr_d_mid]

    # right enclosure
    right_tl_corner = right_enclosure_tl
    right_tr_corner = right_enclosure_tr
    right_bl_corner = right_enclosure_bl
    right_br_corner = right_enclosure_br

    right_tltr_mid, right_blbr_mid, right_tlbl_mid, right_tltr_l_mid, right_tltr_r_mid, right_lbr_l_mid, right_blbr_r_mid, \
    right_tlbl_u_mid, right_tlbl_d_mid = make_midpoints(right_tl_corner, right_tr_corner, right_bl_corner,
                                                        right_br_corner, False)
    r_enclosure = [right_tl_corner, right_tr_corner, right_bl_corner, right_br_corner, right_tltr_mid, right_blbr_mid,
                   right_tlbl_mid, right_tltr_l_mid, right_tltr_r_mid, right_lbr_l_mid, right_blbr_r_mid,
                   right_tlbl_u_mid, right_tlbl_d_mid]

    # purple range
    l_range = np.array([130, 100, 100])
    u_range = np.array([145, 255, 255])

    # required amount of frames
    req_frames = int(int(vid_fps.get()) * (int(interaction_time.get()) / 1000))
    cap = cv.VideoCapture(filename=files[0])
    while True:
        ret, frame = cap.read()
        h, w, l = frame.shape
        size = (w, h)
        break
    cap.release()

    for index, file in enumerate(files):
        # counters
        left_sniffle_counter = 0
        left_sniffle_frames = 0
        left_total_frames = 0
        right_sniffle_counter = 0
        right_sniffle_frames = 0
        right_total_frames = 0
        frame_num = 0

        capture = cv.VideoCapture(filename=file)

        codec = cv.VideoWriter_fourcc(*'mp4v')
        frame_rate = int(vid_fps.get())
        video_out = cv2.VideoWriter(os.path.join(save_path, 'trial_' + str(index + 1) + '.mp4'), codec, frame_rate,
                                    size)
        # go through each frame and update counters
        while True:
            ret, frame = capture.read()
            if frame is None:
                break

            left_total_frames, left_sniffle_frames, left_sniffle_counter = update_ctr(left_x_start, left_x_end,
                                                                                      left_y_start, left_y_end, l_range,
                                                                                      u_range, frame, l_enclosure,
                                                                                      interact_dist, left_total_frames,
                                                                                      left_sniffle_frames,
                                                                                      left_sniffle_counter, req_frames)
            cvzone.putTextRect(frame, f'A1 Left Sniffle Counter: {left_sniffle_counter}', (25, 500), 1.5)
            cvzone.putTextRect(frame, f'A1 Left Sniffle Time: {left_total_frames / int(vid_fps.get())}s', (25, 540),
                               1.5)
            cvzone.putTextRect(frame, f'A1 Left Sniffle Frames: {left_total_frames}', (25, 580), 1.5)

            right_total_frames, right_sniffle_frames, right_sniffle_counter = update_ctr(right_x_start, right_x_end,
                                                                                         right_y_start, right_y_end,
                                                                                         l_range,
                                                                                         u_range, frame, r_enclosure,
                                                                                         interact_dist,
                                                                                         right_total_frames,
                                                                                         right_sniffle_frames,
                                                                                         right_sniffle_counter,
                                                                                         req_frames)

            cvzone.putTextRect(frame, f'A2 Right Sniffle Counter: {right_sniffle_counter}', (425, 500), 1.5)
            cvzone.putTextRect(frame, f'A2 Right Sniffle Time: {right_total_frames / int(vid_fps.get())}s', (425, 540),
                               1.5)
            cvzone.putTextRect(frame, f'A2 Right Sniffle Frames: {right_total_frames}', (425, 580), 1.5)
            frame_num += 1
            video_out.write(frame)
        video_out.release()
        capture.release()
        cv.destroyAllWindows()


def convert_frames_to_video(vid_fps):
    """
    A function that converts frames into a .mp4 video file.
    :param vid_fps: The frames per second of the video
    """
    # ask for file path
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.jpg')
    # natural sort the files
    files = sorted(glob.glob(pattern),
                   key=lambda filename: [int(name) if name.isdigit() else name for name in re.split('(\d+)', filename)])

    image_list = []
    # save all the images into a list
    for file in files:
        image = cv.imread(file)
        h, w, l = image.shape
        size = (w, h)
        image_list.append(image)

    save_path = filedialog.asksaveasfilename(defaultextension='.mp4', title='Save the Frame')
    vid_writer = cv.VideoWriter(save_path, cv.VideoWriter_fourcc(*'mp4v'), int(vid_fps.get()), size)

    # write all the images into a video
    for image in range(len(image_list)):
        vid_writer.write(image_list[image])

    vid_writer.release()


def create_live_video_csv(left_x_start, left_x_end, left_y_start, left_y_end, interaction_dist_cm, enclosure_len_pix,
                          enclosure_len_cm, vid_fps, left_enclosure_tl, left_enclosure_tr, left_enclosure_bl,
                          left_enclosure_br, right_x_start, right_x_end, right_y_start, right_y_end,
                          right_enclosure_tl, right_enclosure_tr, right_enclosure_bl, right_enclosure_br,
                          interaction_time):
    """
    A function that analyzes all the live-video counting and puts them in a CSV for each animal
    :param left_x_start: The left starting x position
    :param left_x_end: The left ending x position
    :param left_y_start: The left starting y position
    :param left_y_end: The left ending y position
    :param interaction_dist_cm: The interaction distance in centimeters
    :param enclosure_len_pix: The enclosure length in pixel
    :param enclosure_len_cm: The enclosure length in centimeters
    :param vid_fps: The frames per second in the video
    :param left_enclosure_tl: The top left corner of the left enclosure
    :param left_enclosure_tr: The top right corner of the left enclosure
    :param left_enclosure_bl: The bottom left corner of the left enclosure
    :param left_enclosure_br: The bottom right corner of the left enclosure
    :param right_x_start: The right starting x position
    :param right_x_end: The right ending x position
    :param right_y_start: The right starting y position
    :param right_y_end: The right ending y position
    :param right_enclosure_tl: The top left corner of the right enclosure
    :param right_enclosure_tr: The top right corner of the right enclosure
    :param right_enclosure_bl: The bottom left corner of the right enclosure
    :param right_enclosure_br: The bottom right corner of the right enclosure
    :param interaction_time: The interaction time required for a sniffle
    """
    # setting up file path
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.mp4')
    files = glob.glob(pattern)

    # calculate interaction distance in pixels
    pix_per_cm = int(enclosure_len_pix.get()) / float(enclosure_len_cm.get())
    interact_dist = int(interaction_dist_cm.get()) * pix_per_cm

    # left enclosure
    left_tl_corner = left_enclosure_tl
    left_tr_corner = left_enclosure_tr
    left_bl_corner = left_enclosure_bl
    left_br_corner = left_enclosure_br

    left_tltr_mid, left_blbr_mid, left_trbr_mid, left_tltr_l_mid, left_tltr_r_mid, left_blbr_l_mid, left_blbr_r_mid, \
    left_trbr_u_mid, left_trbr_d_mid = make_midpoints(left_tl_corner, left_tr_corner, left_bl_corner, left_br_corner,
                                                      True)

    l_enclosure = [left_tl_corner, left_tr_corner, left_bl_corner, left_br_corner, left_tltr_mid, left_blbr_mid,
                   left_trbr_mid, left_tltr_l_mid, left_tltr_r_mid, left_blbr_l_mid, left_blbr_r_mid, left_trbr_u_mid,
                   left_trbr_d_mid]

    # right enclosure
    right_tl_corner = right_enclosure_tl
    right_tr_corner = right_enclosure_tr
    right_bl_corner = right_enclosure_bl
    right_br_corner = right_enclosure_br

    right_tltr_mid, right_blbr_mid, right_tlbl_mid, right_tltr_l_mid, right_tltr_r_mid, right_lbr_l_mid, right_blbr_r_mid, \
    right_tlbl_u_mid, right_tlbl_d_mid = make_midpoints(right_tl_corner, right_tr_corner, right_bl_corner,
                                                        right_br_corner, False)
    r_enclosure = [right_tl_corner, right_tr_corner, right_bl_corner, right_br_corner, right_tltr_mid, right_blbr_mid,
                   right_tlbl_mid, right_tltr_l_mid, right_tltr_r_mid, right_lbr_l_mid, right_blbr_r_mid,
                   right_tlbl_u_mid, right_tlbl_d_mid]

    # purple range
    l_range = np.array([130, 100, 100])
    u_range = np.array([145, 255, 255])

    req_frames = int(int(vid_fps.get()) * (int(interaction_time.get()) / 1000))

    mouse_dict = dict()

    # iterate all the video files, update counters, and save to dictionary
    for index, file in enumerate(files):
        capture = cv.VideoCapture(filename=file)
        left_sniffle_counter = 0
        left_sniffle_frames = 0
        left_total_frames = 0
        right_sniffle_counter = 0
        right_sniffle_frames = 0
        right_total_frames = 0
        frame_num = 0

        while True:
            ret, frame = capture.read()
            if frame is None:
                break

            left_total_frames, left_sniffle_frames, left_sniffle_counter = update_ctr(left_x_start, left_x_end,
                                                                                      left_y_start, left_y_end, l_range,
                                                                                      u_range, frame, l_enclosure,
                                                                                      interact_dist, left_total_frames,
                                                                                      left_sniffle_frames,
                                                                                      left_sniffle_counter, req_frames)
            cvzone.putTextRect(frame, f'A1 Left Sniffle Counter: {left_sniffle_counter}', (25, 500), 1.5)
            cvzone.putTextRect(frame, f'A1 Left Sniffle Time: {left_total_frames / int(vid_fps.get())}s', (25, 540),
                               1.5)
            cvzone.putTextRect(frame, f'A1 Left Sniffle Frames: {left_total_frames}', (25, 580), 1.5)

            right_total_frames, right_sniffle_frames, right_sniffle_counter = update_ctr(right_x_start, right_x_end,
                                                                                         right_y_start, right_y_end,
                                                                                         l_range,
                                                                                         u_range, frame, r_enclosure,
                                                                                         interact_dist,
                                                                                         right_total_frames,
                                                                                         right_sniffle_frames,
                                                                                         right_sniffle_counter,
                                                                                         req_frames)

            cvzone.putTextRect(frame, f'A2 Right Sniffle Counter: {right_sniffle_counter}', (425, 500), 1.5)
            cvzone.putTextRect(frame, f'A2 Right Sniffle Time: {right_total_frames / int(vid_fps.get())}s', (425, 540),
                               1.5)
            cvzone.putTextRect(frame, f'A2 Right Sniffle Frames: {right_total_frames}', (425, 580), 1.5)
            # cv.imwrite(f"{save_path}/frame-{frame_num}.jpg", frame)
            frame_num += 1
        mouse_dict['trial_' + str(index + 1) + '_mouse_1'] = [left_sniffle_counter,
                                                              left_total_frames / int(vid_fps.get()), left_total_frames]
        mouse_dict['trial_' + str(index + 1) + '_mouse_2'] = [right_sniffle_counter,
                                                              right_total_frames / int(vid_fps.get()),
                                                              right_total_frames]
        capture.release()
        cv.destroyAllWindows()
    # convert the dictionary into a df and then into a CSV file
    social_interaction_df = pd.DataFrame.from_dict(mouse_dict, orient='index',
                                                   columns=['Total Sniffles', 'Total Sniffle Time',
                                                            'Total Sniffle Frames'])
    save_path = filedialog.asksaveasfilename(defaultextension='.csv', title='save the file')
    social_interaction_df.to_csv(save_path)


def make_extraction_buttons(tk, root):
    """
    Creates all the buttons and UI for the extraction functionalities
    :param tk:
    :param root:
    :return:
    """
    left_x_start_label = tk.Label(root, text='Enter the starting x coordinate')
    left_x_start_entry = tk.Entry(root, width=30, justify='center')
    left_x_start_label.grid(row=0, column=0)
    left_x_start_entry.grid(row=0, column=1)

    left_x_end_label = tk.Label(root, text='Enter the ending x coordinate')
    left_x_end_entry = tk.Entry(root, width=30, justify='center')
    left_x_end_label.grid(row=1, column=0)
    left_x_end_entry.grid(row=1, column=1)

    left_y_start_label = tk.Label(root, text='Enter the starting y coordinate')
    left_y_start_entry = tk.Entry(root, width=30, justify='center')
    left_y_start_label.grid(row=2, column=0)
    left_y_start_entry.grid(row=2, column=1)

    left_y_end_label = tk.Label(root, text='Enter the ending y coordinate')
    left_y_end_entry = tk.Entry(root, width=30, justify='center')
    left_y_end_label.grid(row=3, column=0)
    left_y_end_entry.grid(row=3, column=1)

    extraction_one_btn = tk.Button(root, text='Extract Frame From Video',
                                   command=lambda: extract_one_frame(left_x_start_entry, left_x_end_entry,
                                                                     left_y_start_entry, left_y_end_entry))
    extraction_one_btn.grid(row=4, column=0, columnspan=2)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=5, column=0)

    left_x_start_all_label = tk.Label(root, text='Enter the left starting x coordinate')
    left_x_start_all_entry = tk.Entry(root, width=30, justify='center')
    left_x_start_all_label.grid(row=6, column=0)
    left_x_start_all_entry.grid(row=6, column=1)

    left_x_end_all_label = tk.Label(root, text='Enter the left ending x coordinate')
    left_x_end_all_entry = tk.Entry(root, width=30, justify='center')
    left_x_end_all_label.grid(row=7, column=0)
    left_x_end_all_entry.grid(row=7, column=1)

    left_y_start_all_label = tk.Label(root, text='Enter the left starting y coordinate')
    left_y_start_all_entry = tk.Entry(root, width=30, justify='center')
    left_y_start_all_label.grid(row=8, column=0)
    left_y_start_all_entry.grid(row=8, column=1)

    left_y_end_all_label = tk.Label(root, text='Enter the left ending y coordinate')
    left_y_end_all_entry = tk.Entry(root, width=30, justify='center')
    left_y_end_all_label.grid(row=9, column=0)
    left_y_end_all_entry.grid(row=9, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=10, column=0)

    right_x_start_all_label = tk.Label(root, text='Enter the right starting x coordinate')
    right_x_start_all_entry = tk.Entry(root, width=30, justify='center')
    right_x_start_all_label.grid(row=11, column=0)
    right_x_start_all_entry.grid(row=11, column=1)

    right_x_end_all_label = tk.Label(root, text='Enter the right ending x coordinate')
    right_x_end_all_entry = tk.Entry(root, width=30, justify='center')
    right_x_end_all_label.grid(row=12, column=0)
    right_x_end_all_entry.grid(row=12, column=1)

    right_y_start_all_label = tk.Label(root, text='Enter the right starting y coordinate')
    right_y_start_all_entry = tk.Entry(root, width=30, justify='center')
    right_y_start_all_label.grid(row=13, column=0)
    right_y_start_all_entry.grid(row=13, column=1)

    right_y_end_all_label = tk.Label(root, text='Enter the right ending y coordinate')
    right_y_end_all_entry = tk.Entry(root, width=30, justify='center')
    right_y_end_all_label.grid(row=14, column=0)
    right_y_end_all_entry.grid(row=14, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=15, column=0)

    extraction_all_enclosure_pixel_label = tk.Label(root, text='Enter enclosure length in pixels:')
    extraction_all_enclosure_pixel_label.grid(row=16, column=0)
    extraction_all_enclosure_pixel_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_enclosure_pixel_entry.grid(row=16, column=1)

    extraction_all_enclosure_cm_label = tk.Label(root, text='Enter enclosure length in cm:')
    extraction_all_enclosure_cm_label.grid(row=17, column=0)
    extraction_all_enclosure_cm_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_enclosure_cm_entry.grid(row=17, column=1)

    extraction_all_interaction_dist_label = tk.Label(root, text='Enter interaction distance in cm:')
    extraction_all_interaction_dist_label.grid(row=18, column=0)
    extraction_all_interaction_dist_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_interaction_dist_entry.grid(row=18, column=1)

    extraction_all_fps_label = tk.Label(root, text='Enter the video frames per second:')
    extraction_all_fps_label.grid(row=19, column=0)
    extraction_all_fps_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_fps_entry.grid(row=19, column=1)

    extraction_all_time_label = tk.Label(root, text='Enter the interaction time in ms:')
    extraction_all_time_label.grid(row=20, column=0)
    extraction_all_time_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_time_entry.grid(row=20, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=21, column=0)

    extraction_test_enclosure_left_tl_label = tk.Label(root, text='Enter left-enclosure top-left coordinates as (x,y):')
    extraction_test_enclosure_left_tl_label.grid(row=22, column=0)
    extraction_test_enclosure_left_tl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_tl_entry.grid(row=22, column=1)

    extraction_test_enclosure_left_tr_label = tk.Label(root,
                                                       text='Enter left-enclosure top-right coordinates as (x,y):')
    extraction_test_enclosure_left_tr_label.grid(row=23, column=0)
    extraction_test_enclosure_left_tr_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_tr_entry.grid(row=23, column=1)

    extraction_test_enclosure_left_bl_label = tk.Label(root,
                                                       text='Enter left-enclosure bottom-left coordinates as (x,y):')
    extraction_test_enclosure_left_bl_label.grid(row=24, column=0)
    extraction_test_enclosure_left_bl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_bl_entry.grid(row=24, column=1)

    extraction_test_enclosure_left_br_label = tk.Label(root,
                                                       text='Enter left-enclosure bottom-right coordinates as (x,y):')
    extraction_test_enclosure_left_br_label.grid(row=25, column=0)
    extraction_test_enclosure_left_br_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_br_entry.grid(row=25, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=26, column=0)

    extraction_test_enclosure_right_tl_label = tk.Label(root,
                                                        text='Enter right-enclosure top-left coordinates as (x,y):')
    extraction_test_enclosure_right_tl_label.grid(row=27, column=0)
    extraction_test_enclosure_right_tl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_tl_entry.grid(row=27, column=1)

    extraction_test_enclosure_right_tr_label = tk.Label(root,
                                                        text='Enter right-enclosure top-right coordinates as (x,y):')
    extraction_test_enclosure_right_tr_label.grid(row=28, column=0)
    extraction_test_enclosure_right_tr_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_tr_entry.grid(row=28, column=1)

    extraction_test_enclosure_right_bl_label = tk.Label(root,
                                                        text='Enter right-enclosure bottom-left coordinates as (x,y):')
    extraction_test_enclosure_right_bl_label.grid(row=29, column=0)
    extraction_test_enclosure_right_bl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_bl_entry.grid(row=29, column=1)

    extraction_test_enclosure_right_br_label = tk.Label(root,
                                                        text='Enter right-enclosure bottom-right coordinates as (x,y):')
    extraction_test_enclosure_right_br_label.grid(row=30, column=0)
    extraction_test_enclosure_right_br_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_br_entry.grid(row=30, column=1)

    extraction_test_all_btn = tk.Button(root, text='Create Live Videos',
                                        command=lambda: create_live_video(left_x_start_all_entry,
                                                                          left_x_end_all_entry,
                                                                          left_y_start_all_entry,
                                                                          left_y_end_all_entry,
                                                                          extraction_all_interaction_dist_entry,
                                                                          extraction_all_enclosure_pixel_entry,
                                                                          extraction_all_enclosure_cm_entry,
                                                                          extraction_all_fps_entry,
                                                                          literal_eval(
                                                                              extraction_test_enclosure_left_tl_entry.get()),
                                                                          literal_eval(
                                                                              extraction_test_enclosure_left_tr_entry.get()),
                                                                          literal_eval(
                                                                              extraction_test_enclosure_left_bl_entry.get()),
                                                                          literal_eval(
                                                                              extraction_test_enclosure_left_br_entry.get()),
                                                                          right_x_start_all_entry,
                                                                          right_x_end_all_entry,
                                                                          right_y_start_all_entry,
                                                                          right_y_end_all_entry,
                                                                          literal_eval(
                                                                              extraction_test_enclosure_right_tl_entry.get()),
                                                                          literal_eval(
                                                                              extraction_test_enclosure_right_tr_entry.get()),
                                                                          literal_eval(
                                                                              extraction_test_enclosure_right_bl_entry.get()),
                                                                          literal_eval(
                                                                              extraction_test_enclosure_right_br_entry.get()),
                                                                          extraction_all_time_entry
                                                                          ))
    extraction_test_all_btn.grid(row=31, column=0, columnspan=2)
    extraction_extract_all_btn = tk.Button(root, text='Create Live Video Output CSV',
                                           command=lambda: create_live_video_csv(left_x_start_all_entry,
                                                                                 left_x_end_all_entry,
                                                                                 left_y_start_all_entry,
                                                                                 left_y_end_all_entry,
                                                                                 extraction_all_interaction_dist_entry,
                                                                                 extraction_all_enclosure_pixel_entry,
                                                                                 extraction_all_enclosure_cm_entry,
                                                                                 extraction_all_fps_entry,
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_left_tl_entry.get()),
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_left_tr_entry.get()),
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_left_bl_entry.get()),
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_left_br_entry.get()),
                                                                                 right_x_start_all_entry,
                                                                                 right_x_end_all_entry,
                                                                                 right_y_start_all_entry,
                                                                                 right_y_end_all_entry,
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_right_tl_entry.get()),
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_right_tr_entry.get()),
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_right_bl_entry.get()),
                                                                                 literal_eval(
                                                                                     extraction_test_enclosure_right_br_entry.get()),
                                                                                 extraction_all_time_entry
                                                                                 ))
    extraction_extract_all_btn.grid(row=32, column=0, columnspan=2)
