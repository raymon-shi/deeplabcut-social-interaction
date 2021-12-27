import tkinter as tk
import webbrowser

import pandas as pd

pd.set_option("display.max_rows", None, "display.max_columns", None)

root = tk.Tk()
root.title('Raymon Shi - DLC SI App')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


def display_frame(frame_page):
    frame_page.tkraise()


main_page_frame = tk.Frame(root)
main_page_frame.grid(row=0, column=0, sticky='nsew')
main_page_frame.columnconfigure(0, weight=1)

accuracy_frame = tk.Frame(root)
accuracy_frame.grid(row=0, column=0, sticky='nsew')
accuracy_frame.columnconfigure(0, weight=1)

social_interaction_frame = tk.Frame(root)
social_interaction_frame.grid(row=0, column=0, sticky='nsew')
social_interaction_frame.columnconfigure(0, weight=1)


def main_page_frame_buttons():
    accuracy_btn = tk.Button(main_page_frame, text='Dropped Frames / Accuracy',
                             command=lambda: display_frame(accuracy_frame))
    accuracy_btn.grid(row=1, column=0)
    social_interaction_btn = tk.Button(main_page_frame, text='Social Interaction',
                                       command=lambda: display_frame(social_interaction_frame))
    social_interaction_btn.grid(row=2, column=0)
    github_code_btn = tk.Button(main_page_frame, text='Github Code Page', command=lambda: webbrowser.open(
        'https://github.com/raymon-shi/deeplabcut-social-interaction'))
    github_code_btn.grid(row=3, column=0)


def main_menu_buttons(tk, frame):
    main_menu_btn = tk.Button(frame, text='Main Menu', command=lambda: display_frame(main_page_frame), width=30)
    spacer_btn = tk.Label(frame, text='')
    spacer_btn.grid(row=15, column=0)
    main_menu_btn.grid()


main_menu_buttons(tk, accuracy_frame)
main_menu_buttons(tk, social_interaction_frame)

display_frame(main_page_frame)
main_page_frame_buttons()
root.mainloop()
