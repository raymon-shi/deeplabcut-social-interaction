import glob
import math
import os
from tkinter import filedialog
import pandas as pd
from ast import literal_eval


def interaction_zone_area(arena_top_corner, arena_bottom_corner, side, pixel_per_cm, interaction_dist,
                          interaction_width, interaction_length):
    if side == 'left':
        tl_corner = (arena_top_corner[0], int(arena_top_corner[1] + interaction_dist * pixel_per_cm))
        bl_corner = (arena_bottom_corner[0], int(arena_bottom_corner[1] - interaction_dist * pixel_per_cm))
        tr_corner = (int(tl_corner[0] + interaction_width * pixel_per_cm), tl_corner[1])
        br_corner = (int(bl_corner[0] + interaction_width * pixel_per_cm), bl_corner[1])
        return tl_corner, tr_corner, bl_corner, br_corner

    if side == 'right':
        tr_corner = (arena_top_corner[0], int(arena_top_corner[1] + interaction_dist * pixel_per_cm))
        br_corner = (arena_bottom_corner[0], int(arena_bottom_corner[1] - interaction_dist * pixel_per_cm))
        tl_corner = (int(tr_corner[0] - interaction_width * pixel_per_cm), tr_corner[1])
        bl_corner = (int(br_corner[0] - interaction_width * pixel_per_cm), br_corner[1])
        return tl_corner, tr_corner, bl_corner, br_corner


def check_zone(mouse_coord, interaction_zone_corners):
    if interaction_zone_corners[0][0] <= mouse_coord[0] <= interaction_zone_corners[3][0] and \
            interaction_zone_corners[0][
                1] <= mouse_coord[1] <= interaction_zone_corners[3][1]:
        return True
    return False


def update_counters(first_col, second_col, total_frames, interaction_frames,
                    interaction_entries, zone, current_frame):
    mouse_coord = (float(first_col), float(second_col))
    if not math.isnan(mouse_coord[0]) and not math.isnan(mouse_coord[1]):
        total_frames += 1
    if check_zone(mouse_coord, zone):
        interaction_frames += 1
        current_frame += 1
        consecutive = True
    else:
        consecutive = False

    if not consecutive:
        current_frame = 0
    if current_frame == 1:
        interaction_entries += 1

    return interaction_frames, interaction_entries, total_frames, current_frame


def interaction_zone(enclosure_length_cm, enclosure_length_pix, interact_dist, interact_width, interact_length,
                     left_arena_top, left_arena_bot, right_arena_top, right_arena_bot):
    enclosure_len_cm = int(enclosure_length_cm.get())
    enclosure_len_pix = int(enclosure_length_pix.get())
    pix_per_cm = enclosure_len_pix / enclosure_len_cm

    l_arena_top, l_arena_bot = literal_eval(left_arena_top.get()), literal_eval(left_arena_bot.get())
    r_arena_top, r_arena_bot = literal_eval(right_arena_top.get()), literal_eval(right_arena_bot.get())

    la_tl, la_tr, la_bl, la_br = interaction_zone_area(l_arena_top, l_arena_bot, 'left', pix_per_cm,
                                                       int(interact_dist.get()),
                                                       int(interact_width.get()), int(interact_length.get()))
    ra_tl, ra_tr, ra_bl, ra_br = interaction_zone_area(r_arena_top, r_arena_bot, 'right', pix_per_cm,
                                                       int(interact_dist.get()),
                                                       int(interact_width.get()), int(interact_length.get()))

    left_interaction_zone = [la_tl, la_tr, la_bl, la_br]
    right_interaction_zone = [ra_tl, ra_tr, ra_bl, ra_br]

    print(left_interaction_zone, 'left')
    print(right_interaction_zone, 'right')

    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    mouse_entry = dict()
    mouse_entry_missed = dict()

    for index, file in enumerate(files):
        df_csv = pd.read_csv(file, index_col=False)
        left_total_interaction_frames, left_total_interaction_entries, left_total_frames, left_current_frame = 0, 0, 0, 0
        left_missed_total_interaction_frames, left_missed_total_interaction_entries, left_missed_total_frames, left_missed_current_frame = 0, 0, 0, 0
        right_total_interaction_frames, right_total_interaction_entries, right_total_frames, right_current_frame = 0, 0, 0, 0
        right_missed_total_interaction_frames, right_missed_total_interaction_entries, right_missed_total_frames, right_missed_current_frame = 0, 0, 0, 0
        mouse_counter = 1
        for row in df_csv[3:].itertuples():
            left_total_interaction_frames, left_total_interaction_entries, left_total_frames, left_current_frame = update_counters(
                row[14],
                row[15],
                left_total_frames,
                left_total_interaction_frames,
                left_total_interaction_entries,
                left_interaction_zone,
                left_current_frame)
            right_total_interaction_frames, right_total_interaction_entries, right_total_frames, right_current_frame = update_counters(
                row[2],
                row[3],
                right_total_frames,
                right_total_interaction_frames,
                right_total_interaction_entries,
                right_interaction_zone,
                right_current_frame)
            left_missed_total_interaction_frames, left_missed_total_interaction_entries, left_missed_total_frames, left_missed_current_frame = update_counters(
                row[2],
                row[3],
                left_missed_total_frames,
                left_missed_total_interaction_frames,
                left_missed_total_interaction_entries,
                left_interaction_zone,
                left_missed_current_frame)
            right_missed_total_interaction_frames, right_missed_total_interaction_entries, right_missed_total_frames, right_missed_current_frame = update_counters(
                row[14],
                row[15],
                right_missed_total_frames,
                right_missed_total_interaction_frames,
                right_missed_total_interaction_entries,
                right_interaction_zone,
                right_missed_current_frame)
        mouse_entry['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [left_total_interaction_frames / 25,
                                                                                   left_total_interaction_entries]
        mouse_entry_missed['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [
            left_missed_total_interaction_frames / 25,
            left_missed_total_interaction_entries]
        mouse_counter += 1
        mouse_entry['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [right_total_interaction_frames / 25,
                                                                                   right_total_interaction_entries]
        mouse_entry_missed['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [
            right_missed_total_interaction_frames / 25,
            right_missed_total_interaction_entries]
    interaction_zone_df = pd.DataFrame.from_dict(mouse_entry, orient='index',
                                                 columns=['Time in Interaction Zone (s)', 'Entries in Interaction Zone'])
    interaction_zone_filtered_df = interaction_zone_df[(interaction_zone_df['Time in Interaction Zone (s)'] == 0) & (
            interaction_zone_df['Entries in Interaction Zone'] == 0)]
    missed_entries = list(interaction_zone_filtered_df.index)
    interaction_zone_missed_df = pd.DataFrame.from_dict(mouse_entry_missed, orient='index',
                                                        columns=['Time in Interaction Zone (s)',
                                                                 'Entries in Interaction Zone'])
    interaction_zone_missed_series = interaction_zone_missed_df.index.isin(missed_entries)
    interaction_zone_missed_df = interaction_zone_missed_df[interaction_zone_missed_series]
    interaction_zone_df.update(interaction_zone_missed_df)
    save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
    interaction_zone_df.to_csv(save_file_path)


def make_interaction_zone_buttons(tk, root):
    iz_enclosure_pixel_label = tk.Label(root, text='Enter enclosure length in pixels:')
    iz_enclosure_pixel_label.grid(row=0, column=0)
    iz_enclosure_pixel_entry = tk.Entry(root, width=30, justify='center')
    iz_enclosure_pixel_entry.grid(row=0, column=1)

    iz_enclosure_cm_label = tk.Label(root, text='Enter enclosure length in cm:')
    iz_enclosure_cm_label.grid(row=1, column=0)
    iz_enclosure_cm_entry = tk.Entry(root, width=30, justify='center')
    iz_enclosure_cm_entry.grid(row=1, column=1)

    iz_interaction_dist_cm_label = tk.Label(root, text='Enter distance from corner to interaction zone in cm:')
    iz_interaction_dist_cm_label.grid(row=2, column=0)
    iz_interaction_dist_cm_entry = tk.Entry(root, width=30, justify='center')
    iz_interaction_dist_cm_entry.grid(row=2, column=1)

    iz_interaction_width_cm_label = tk.Label(root, text='Enter interaction zone width in cm:')
    iz_interaction_width_cm_label.grid(row=3, column=0)
    iz_interaction_width_cm_entry = tk.Entry(root, width=30, justify='center')
    iz_interaction_width_cm_entry.grid(row=3, column=1)

    iz_interaction_length_cm_label = tk.Label(root, text='Enter interaction zone length in cm:')
    iz_interaction_length_cm_label.grid(row=4, column=0)
    iz_interaction_length_cm_entry = tk.Entry(root, width=30, justify='center')
    iz_interaction_length_cm_entry.grid(row=4, column=1)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=5, column=0)

    iz_left_arena_top_corner_label = tk.Label(root, text='Enter left arena top corner as (x,y):')
    iz_left_arena_top_corner_label.grid(row=6, column=0)
    iz_left_arena_top_corner_entry = tk.Entry(root, width=30, justify='center')
    iz_left_arena_top_corner_entry.grid(row=6, column=1)

    iz_left_arena_bottom_corner_label = tk.Label(root, text='Enter left arena bottom corner as (x,y):')
    iz_left_arena_bottom_corner_label.grid(row=7, column=0)
    iz_left_arena_bottom_corner_entry = tk.Entry(root, width=30, justify='center')
    iz_left_arena_bottom_corner_entry.grid(row=7, column=1)

    iz_right_arena_top_corner_label = tk.Label(root, text='Enter right arena top corner as (x,y):')
    iz_right_arena_top_corner_label.grid(row=8, column=0)
    iz_right_arena_top_corner_entry = tk.Entry(root, width=30, justify='center')
    iz_right_arena_top_corner_entry.grid(row=8, column=1)

    iz_right_arena_bottom_corner_label = tk.Label(root, text='Enter right arena bottom corner as (x,y)')
    iz_right_arena_bottom_corner_label.grid(row=9, column=0)
    iz_right_arena_bottom_corner_entry = tk.Entry(root, width=30, justify='center')
    iz_right_arena_bottom_corner_entry.grid(row=9, column=1)

    iz_button = tk.Button(root, text='Make IZ CSV',
                          command=lambda: interaction_zone(iz_enclosure_cm_entry, iz_enclosure_pixel_entry,
                                                           iz_interaction_dist_cm_entry, iz_interaction_width_cm_entry,
                                                           iz_interaction_length_cm_entry,
                                                           iz_left_arena_top_corner_entry,
                                                           iz_left_arena_bottom_corner_entry,
                                                           iz_right_arena_top_corner_entry,
                                                           iz_right_arena_bottom_corner_entry))
    iz_button.grid(row=10, column=0)
