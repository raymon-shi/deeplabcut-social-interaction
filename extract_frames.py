import glob
import tkinter.filedialog as filedialog
import cv2 as cv
import os
import re
from ast import literal_eval


def extract_one():
    file_path = filedialog.askopenfilename()
    capture = cv.VideoCapture(filename=file_path)
    save_path = filedialog.asksaveasfilename(defaultextension='.png', title='Save the Frame')

    # reads the first frame
    exist, frame = capture.read()
    # writes the first frame to save path
    cv.imwrite(save_path, frame)


def extract_all(left_top_left_coords, left_bottom_right_coords, right_top_left_coords,
                right_bottom_right_coords, interaction_dist_cm, enclosure_len_pix, enclosure_len_cm):
    pix_per_cm = int(enclosure_len_pix.get()) / float(enclosure_len_cm.get())
    add_dist = int(interaction_dist_cm.get()) * pix_per_cm

    left_top_left_x, left_top_left_y = left_top_left_coords[0], int(left_top_left_coords[1] - add_dist)
    left_bottom_right_x, left_bottom_right_y = int(left_bottom_right_coords[0] + add_dist), int(
        left_bottom_right_coords[1] + add_dist)

    right_top_left_x, right_top_left_y = int(right_top_left_coords[0] - add_dist), int(
        right_top_left_coords[1] - add_dist)
    right_bottom_right_x, right_bottom_right_y = right_bottom_right_coords[0], int(
        right_bottom_right_coords[1] + add_dist)

    file_path = filedialog.askopenfilename()
    capture = cv.VideoCapture(filename=file_path)
    save_path = filedialog.askdirectory()
    frame_num = 0
    # reads all the frames in the video
    while True:
        exist, frame = capture.read()
        if not exist:
            capture.release()
            break
        # draw left enclosure rough interaction zone
        image = cv.rectangle(frame, (left_top_left_x, left_top_left_y), (left_bottom_right_x, left_bottom_right_y),
                             (255, 255, 255), 2)
        # draw right enclosure rough interaction zone
        image = cv.rectangle(image, (right_top_left_x, right_top_left_y), (right_bottom_right_x, right_bottom_right_y),
                             (255, 255, 255), 2)
        # save all the images to file path
        cv.imwrite(f"{save_path}/frame-{frame_num}.jpg", image)
        frame_num += 1


def convert_frames_to_video():
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
    vid_writer = cv.VideoWriter(save_path, cv.VideoWriter_fourcc(*'mp4v'), 25, size)

    # write all the images into a video
    for image in range(len(image_list)):
        vid_writer.write(image_list[image])

    vid_writer.release()


def make_extraction_buttons(tk, root):
    extraction_one_btn = tk.Button(root, text='Extract First Frame', command=lambda: extract_one())
    extraction_one_btn.grid(row=0, column=0, columnspan=2)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=1, column=0)

    extraction_all_enclosure_pixel_label = tk.Label(root, text='Enter enclosure length in pixels:')
    extraction_all_enclosure_pixel_label.grid(row=2, column=0)
    extraction_all_enclosure_pixel_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_enclosure_pixel_entry.grid(row=2, column=1)

    extraction_all_enclosure_cm_label = tk.Label(root, text='Enter enclosure length in cm:')
    extraction_all_enclosure_cm_label.grid(row=3, column=0)
    extraction_all_enclosure_cm_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_enclosure_cm_entry.grid(row=3, column=1)

    extraction_all_interaction_dist_label = tk.Label(root, text='Enter interaction distance in cm:')
    extraction_all_interaction_dist_label.grid(row=4, column=0)
    extraction_all_interaction_dist_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_interaction_dist_entry.grid(row=4, column=1)

    spacer_btn_2 = tk.Label(root, text='')
    spacer_btn_2.grid(row=5, column=0)

    extraction_all_left_tl_coord_label = tk.Label(root, text='Enter the left-enclosure top left coordinates as (x,y):')
    extraction_all_left_tl_coord_label.grid(row=6, column=0)
    extraction_all_left_tl_coord_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_left_tl_coord_entry.grid(row=6, column=1)

    extraction_all_left_br_coord_label = tk.Label(root,
                                                  text='Enter the left-enclosure bottom right coordinates as (x,y):')
    extraction_all_left_br_coord_label.grid(row=7, column=0)
    extraction_all_left_br_coord_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_left_br_coord_entry.grid(row=7, column=1)

    extraction_all_right_tl_coord_label = tk.Label(root,
                                                   text='Enter the right-enclosure top left coordinates as (x,y):')
    extraction_all_right_tl_coord_label.grid(row=8, column=0)
    extraction_all_right_tl_coord_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_right_tl_coord_entry.grid(row=8, column=1)

    extraction_all_right_br_coord_label = tk.Label(root,
                                                   text='Enter the right-enclosure bottom right coordinates as (x,y):')
    extraction_all_right_br_coord_label.grid(row=9, column=0)
    extraction_all_right_br_coord_entry = tk.Entry(root, width=30, justify='center')
    extraction_all_right_br_coord_entry.grid(row=9, column=1)

    extraction_all_btn = tk.Button(root, text='Extract All Frames',
                                   command=lambda: extract_all(literal_eval(extraction_all_left_tl_coord_entry.get()),
                                                               literal_eval(extraction_all_left_br_coord_entry.get()),
                                                               literal_eval(extraction_all_right_tl_coord_entry.get()),
                                                               literal_eval(extraction_all_right_br_coord_entry.get()),
                                                               extraction_all_interaction_dist_entry,
                                                               extraction_all_enclosure_pixel_entry,
                                                               extraction_all_enclosure_cm_entry))
    extraction_all_btn.grid(row=10, column=0, columnspan=2)

    spacer_btn_3 = tk.Label(root, text='')
    spacer_btn_3.grid(row=11, column=0)

    extraction_convert_img_to_vid_btn = tk.Button(root, text='Convert Images to Video',
                                                  command=lambda: convert_frames_to_video())
    extraction_convert_img_to_vid_btn.grid(row=12, column=0, columnspan=2)
