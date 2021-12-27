import math
import os
import glob
import tkinter.filedialog as filedialog
import pandas as pd


def accuracy(p_value_input, beginning_frames_dropped_input):
    file_path = filedialog.askdirectory()
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    # dlc model settings
    p_value = float(p_value_input.get())
    beginning_frames_dropped_left = int(beginning_frames_dropped_input.get())
    beginning_frames_dropped_right = int(beginning_frames_dropped_input.get())

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


def make_accuracy_buttons(tk, root):
    accuracy_p_value_label = tk.Label(root, text='Enter the p-value as a decimal:')
    accuracy_p_value_label.grid(row=0, column=0)
    accuracy_p_value_entry = tk.Entry(root, width=30, justify='center')
    accuracy_p_value_entry.grid(row=0, column=1)

    accuracy_dropped_frames_label = tk.Label(root, text='Enter the initial frames to drop as a number:')
    accuracy_dropped_frames_label.grid(row=1, column=0)
    accuracy_dropped_frames_entry = tk.Entry(root, width=30, justify='center')
    accuracy_dropped_frames_entry.grid(row=1, column=1)

    accuracy_csv_btn = tk.Button(root, text='Make Dropped Frames / Accuracy CSV',
                                 command=lambda: accuracy(accuracy_p_value_entry, accuracy_dropped_frames_entry),
                                 width=30)
    accuracy_csv_btn.grid(row=2, column=0, columnspan=2)
