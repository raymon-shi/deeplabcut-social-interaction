import math
import os
import glob
import tkinter.filedialog as filedialog
import pandas as pd


def accuracy():
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    # dlc model settings
    p_value = 0.8
    beginning_frames_dropped_left = 181
    beginning_frames_dropped_right = 247

    # calculate dropped frames / model accuracy
    percent_dropped = dict()

    for index, file in enumerate(files):
        df_csv = pd.read_csv(file, index_col=False)
        dropped_frames_mouse_left = 0
        dropped_frames_mouse_right = 0
        mouse_counter = 1
        for row in df_csv[3:].itertuples():
            if math.isnan(float(row[16])) or float(row[16]) < p_value:
                dropped_frames_mouse_left += 1
            if math.isnan(float(row[4])) or float(row[4]) < p_value:
                dropped_frames_mouse_right += 1
        # get rid of frames where mice not there in beginning
        dropped_frames_mouse_left -= beginning_frames_dropped_left
        dropped_frames_mouse_right -= beginning_frames_dropped_right
        if dropped_frames_mouse_left < 0:
            dropped_frames_mouse_left = 0
        if dropped_frames_mouse_right < 0:
            dropped_frames_mouse_right = 0

        left_dropped_percent = (dropped_frames_mouse_left / (len(df_csv[3:]) - beginning_frames_dropped_left)) * 100
        right_dropped_percent = (dropped_frames_mouse_right / (len(df_csv[3:]) - beginning_frames_dropped_right)) * 100
        percent_dropped['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [left_dropped_percent,
                                                                                       100 - left_dropped_percent]
        mouse_counter += 1
        percent_dropped['trial_' + str(index + 1) + '_mouse_' + str(mouse_counter)] = [right_dropped_percent,
                                                                                       100 - right_dropped_percent]

    all_dropped_percent = [value[0] for value in list(percent_dropped.values())]
    all_accuracy_percent = [value[1] for value in list(percent_dropped.values())]

    average_dropped_frames_percent = (sum(all_dropped_percent) / len(all_dropped_percent))
    average_accuracy_percent = sum(all_accuracy_percent) / len(all_accuracy_percent)

    percent_dropped['average_trials'] = [average_dropped_frames_percent, average_accuracy_percent]

    accuracy_df = pd.DataFrame.from_dict(percent_dropped, orient='index',
                                         columns=['Dropped Frames Percent', 'Accuracy Percent'])

    save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
    accuracy_df.to_csv(save_file_path)

