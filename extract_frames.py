import math
import numpy as np
import glob
import tkinter.filedialog as filedialog
import cv2 as cv
import os
import re
from ast import literal_eval
import cvzone


def extract_one_frame(left_x_start, left_x_end, left_y_start, left_y_end):
    file_path = filedialog.askopenfilename()
    capture = cv.VideoCapture(filename=file_path)
    save_path = filedialog.asksaveasfilename(defaultextension='.jpg', title='Save the Frame')

    # reads the first frame
    exist, frame = capture.read()
    # writes the first frame to save path
    cv.imwrite(save_path,
               frame[int(left_y_start.get()):int(left_y_end.get()), int(left_x_start.get()):int(left_x_end.get())])


def extract_test_frames(left_x_start, left_x_end, left_y_start, left_y_end, interaction_dist_cm, enclosure_len_pix,
                        enclosure_len_cm, vid_fps, left_enclosure_tl, left_enclosure_tr, left_enclosure_bl,
                        left_enclosure_br, right_x_start, right_x_end, right_y_start, right_y_end, right_enclosure_tl,
                        right_enclosure_tr, right_enclosure_bl, right_enclosure_br):
    file_path = filedialog.askopenfilename()
    capture = cv.VideoCapture(filename=file_path)
    save_path = filedialog.askdirectory()

    pix_per_cm = int(enclosure_len_pix.get()) / float(enclosure_len_cm.get())
    interact_dist = int(interaction_dist_cm.get()) * pix_per_cm

    left_tl_corner = left_enclosure_tl
    left_tr_corner = left_enclosure_tr
    left_bl_corner = left_enclosure_bl
    left_br_corner = left_enclosure_br

    right_tl_corner = right_enclosure_tl
    right_tr_corner = right_enclosure_tr
    right_bl_corner = right_enclosure_bl
    right_br_corner = right_enclosure_br

    left_sniffle_counter = 0
    left_sniffle_frames = 0
    left_total_frames = 0
    right_sniffle_counter = 0
    right_sniffle_frames = 0
    right_total_frames = 0
    frame_num = 0

    # purple range
    l_range = np.array([130, 100, 100])
    u_range = np.array([145, 255, 255])

    while True:
        ret, frame = capture.read()
        cvzone.putTextRect(frame, f'A1 Left Sniffle Counter: {left_sniffle_counter}', (25, 500), 1.5)
        cvzone.putTextRect(frame, f'A1 Left Sniffle Time: {left_total_frames / int(vid_fps.get())}s', (25, 540), 1.5)
        cvzone.putTextRect(frame, f'A1 Left Sniffle Frames: {left_total_frames}', (25, 580), 1.5)

        cvzone.putTextRect(frame, f'A2 Right Sniffle Counter: {right_sniffle_counter}', (425, 500), 1.5)
        cvzone.putTextRect(frame, f'A2 Right Sniffle Time: {right_total_frames / int(vid_fps.get())}s', (425, 540), 1.5)
        cvzone.putTextRect(frame, f'A2 Right Sniffle Frames: {right_total_frames}', (425, 580), 1.5)
        if frame is None:
            break

        left_area_of_interest = frame[int(left_y_start.get()):int(left_y_end.get()),
                                int(left_x_start.get()):int(left_x_end.get())]
        left_hsv = cv.cvtColor(left_area_of_interest, cv.COLOR_BGR2HSV)
        left_mask = cv.inRange(left_hsv, l_range, u_range)
        left_contours, _ = cv.findContours(left_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        for contour in left_contours:
            area = cv.contourArea(contour)
            if area > 10:
                x, y, w, h = cv.boundingRect(contour)
                if math.dist((x + .5 * w, y + .5 * h), left_tl_corner) <= interact_dist or math.dist(
                        (x + .5 * w, y + .5 * h), left_tr_corner) <= interact_dist or math.dist(
                    (x + .5 * w, y + .5 * h), left_bl_corner) <= interact_dist or math.dist(
                    (x + .5 * w, y + .5 * h), left_br_corner) <= interact_dist:
                    cv.rectangle(left_area_of_interest, (x, y), (x + w, y + h), (0, 0, 255, 2))
                    left_sniffle_consecutive = True
                    left_sniffle_frames += 1
                    left_total_frames += 1
                else:
                    left_sniffle_consecutive = False
                    cv.rectangle(left_area_of_interest, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if not left_sniffle_consecutive:
                    left_sniffle_frames = 0
                if left_sniffle_frames == 12:
                    left_sniffle_counter += 1
            break

        right_area_of_interest = frame[int(right_y_start.get()):int(right_y_end.get()),
                                 int(right_x_start.get()):int(right_x_end.get())]
        right_hsv = cv.cvtColor(right_area_of_interest, cv.COLOR_BGR2HSV)
        right_mask = cv.inRange(right_hsv, l_range, u_range)
        right_contours, _ = cv.findContours(right_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for contour in right_contours:
            area = cv.contourArea(contour)
            if area > 10:
                x, y, w, h = cv.boundingRect(contour)
                if math.dist((x + .5 * w, y + .5 * h), right_tl_corner) <= interact_dist or math.dist(
                        (x + .5 * w, y + .5 * h), right_tr_corner) <= interact_dist or math.dist(
                    (x + .5 * w, y + .5 * h), right_bl_corner) <= interact_dist or math.dist(
                    (x + .5 * w, y + .5 * h), right_br_corner) <= interact_dist:
                    cv.rectangle(right_area_of_interest, (x, y), (x + w, y + h), (0, 0, 255, 2))
                    right_sniffle_consecutive = True
                    right_sniffle_frames += 1
                    right_total_frames += 1
                else:
                    right_sniffle_consecutive = False
                    cv.rectangle(right_area_of_interest, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if not right_sniffle_consecutive:
                    right_sniffle_frames = 0
                if right_sniffle_frames == 12:
                    right_sniffle_counter += 1
            break

        cv.imwrite(f"{save_path}/frame-{frame_num}.jpg", frame)
        frame_num += 1
    capture.release()
    cv.destroyAllWindows()


def convert_frames_to_video(vid_fps):
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.jpg')
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


def make_extraction_buttons(tk, root):
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

    extraction_one_btn = tk.Button(root, text='Extract First Frame',
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

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=20, column=0)

    extraction_test_enclosure_left_tl_label = tk.Label(root, text='Enter left-enclosure top-left coordinates as (x,y):')
    extraction_test_enclosure_left_tl_label.grid(row=21, column=0)
    extraction_test_enclosure_left_tl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_tl_entry.grid(row=21, column=1)

    extraction_test_enclosure_left_tr_label = tk.Label(root,
                                                       text='Enter left-enclosure top-right coordinates as (x,y):')
    extraction_test_enclosure_left_tr_label.grid(row=22, column=0)
    extraction_test_enclosure_left_tr_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_tr_entry.grid(row=22, column=1)

    extraction_test_enclosure_left_bl_label = tk.Label(root,
                                                       text='Enter left-enclosure bottom-left coordinates as (x,y):')
    extraction_test_enclosure_left_bl_label.grid(row=23, column=0)
    extraction_test_enclosure_left_bl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_bl_entry.grid(row=23, column=1)

    extraction_test_enclosure_left_br_label = tk.Label(root,
                                                       text='Enter left-enclosure bottom-right coordinates as (x,y):')
    extraction_test_enclosure_left_br_label.grid(row=24, column=0)
    extraction_test_enclosure_left_br_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_left_br_entry.grid(row=24, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=25, column=0)

    extraction_test_enclosure_right_tl_label = tk.Label(root,
                                                        text='Enter right-enclosure top-left coordinates as (x,y):')
    extraction_test_enclosure_right_tl_label.grid(row=26, column=0)
    extraction_test_enclosure_right_tl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_tl_entry.grid(row=26, column=1)

    extraction_test_enclosure_right_tr_label = tk.Label(root,
                                                        text='Enter right-enclosure top-right coordinates as (x,y):')
    extraction_test_enclosure_right_tr_label.grid(row=27, column=0)
    extraction_test_enclosure_right_tr_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_tr_entry.grid(row=27, column=1)

    extraction_test_enclosure_right_bl_label = tk.Label(root,
                                                        text='Enter right-enclosure bottom-left coordinates as (x,y):')
    extraction_test_enclosure_right_bl_label.grid(row=28, column=0)
    extraction_test_enclosure_right_bl_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_bl_entry.grid(row=28, column=1)

    extraction_test_enclosure_right_br_label = tk.Label(root,
                                                        text='Enter right-enclosure bottom-right coordinates as (x,y):')
    extraction_test_enclosure_right_br_label.grid(row=29, column=0)
    extraction_test_enclosure_right_br_entry = tk.Entry(root, width=30, justify='center')
    extraction_test_enclosure_right_br_entry.grid(row=29, column=1)

    extraction_test_all_btn = tk.Button(root, text='Extract Test Frames',
                                        command=lambda: extract_test_frames(left_x_start_all_entry,
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
                                                                                extraction_test_enclosure_right_br_entry.get())
                                                                            ))
    extraction_test_all_btn.grid(row=30, column=0, columnspan=2)
    extraction_convert_img_to_vid_btn = tk.Button(root, text='Convert Images to Video',
                                                  command=lambda: convert_frames_to_video(extraction_all_fps_entry))
    extraction_convert_img_to_vid_btn.grid(row=31, column=0, columnspan=2)