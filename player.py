from tkinter import *
import pygame
import os
from tkinter import filedialog
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk


class dirs:
    direction = os.path.abspath(__file__)
    direction = os.path.dirname(direction)


class MP3Player:
    def __init__(self, win):
        self.paused = False
        self.stopped = False
        self.song_len = 0

        win.title('MP3 Player')
        win.iconbitmap(os.path.join(dirs.direction, r'images\icon.ico'))
        win.geometry("460x330")
        win.resizable(width=False, height=False)

        self.base_dir = os.path.join(dirs.direction, 'audio')

        # Initialize Pygame Mixer
        pygame.mixer.init()

        # Create the main frame
        self.master_frame = Frame(root)
        self.master_frame.pack(pady=20)

        # Create the playlist box
        self.song_box = Listbox(self.master_frame, width=60)
        self.song_box.grid(row=0, column=0)

        # Define images for the player control buttons
        self.back_btn_img = PhotoImage(file='images/back.png')
        self.forward_btn_img = PhotoImage(file='images/forward.png')
        self.play_btn_img = PhotoImage(file='images/play.png')
        self.pause_btn_img = PhotoImage(file='images/pause.png')
        self.stop_btn_img = PhotoImage(file='images/stop.png')

        # Create the player control frame
        self.controls_frame = Frame(self.master_frame)
        self.controls_frame.grid(row=1, column=0, pady=20)

        # Create the volume control frame
        self.volume_frame = LabelFrame(self.master_frame, text="Volume")
        self.volume_frame.grid(row=0, column=1, rowspan=2, padx=40)

        # Create the player control buttons
        self.back_button = Button(self.controls_frame, image=self.back_btn_img, borderwidth=0,
                                  command=self.previous_song)
        self.forward_button = Button(self.controls_frame, image=self.forward_btn_img, borderwidth=0,
                                     command=self.next_song)
        self.play_button = Button(
            self.controls_frame, image=self.play_btn_img, borderwidth=0, command=self.play)
        self.pause_button = Button(self.controls_frame, image=self.pause_btn_img, borderwidth=0,
                                   command=lambda: self.pause(self.paused))
        self.stop_button = Button(
            self.controls_frame, image=self.stop_btn_img, borderwidth=0, command=self.stop)

        self.back_button.grid(row=0, column=0, padx=10)
        self.pause_button.grid(row=0, column=1, padx=10)
        self.play_button.grid(row=0, column=2, padx=10)
        self.stop_button.grid(row=0, column=3, padx=10)
        self.forward_button.grid(row=0, column=4, padx=10)

        # Create the status bar
        self.status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
        self.status_bar.pack(fill=X, side=BOTTOM, ipady=2)

        # Create the music position slider
        self.song_slider = ttk.Scale(self.master_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=self.slide,
                                     length=360)
        self.song_slider.grid(row=2, column=0, pady=10)

        # Create the volume slider
        self.volume_slider = ttk.Scale(self.volume_frame, from_=1, to=0, orient=VERTICAL, value=0.5,
                                       command=self.volume,
                                       length=200)
        self.volume_slider.pack(pady=10)

        # Create the menu
        self.my_menu = Menu(root)
        win.config(menu=self.my_menu)

        # Create the add songs menu
        self.add_song_menu = Menu(self.my_menu)
        self.my_menu.add_cascade(label="Add Songs", menu=self.add_song_menu)
        self.add_song_menu.add_command(
            label="Add One Song to Playlist", command=self.add_song)
        # Add multiple songs to the playlist
        self.add_song_menu.add_command(
            label="Add Multiple Songs to Playlist", command=self.add_many_songs)

        # Create the remove songs menu
        self.remove_song_menu = Menu(self.my_menu)
        self.my_menu.add_cascade(label="Remove Songs",
                                 menu=self.remove_song_menu)
        self.remove_song_menu.add_command(
            label="Remove One Song from Playlist", command=self.delete_song)
        self.remove_song_menu.add_command(
            label="Remove All Songs from Playlist", command=self.delete_all_songs)

    # Function to play song time
    def play_time(self):
        # Check for double time
        if self.stopped:
            return
        # Get the current time of the song
        current_time = pygame.mixer.music.get_pos() / 1000

        # Get the song title from the playlist
        song = self.song_box.get(ACTIVE)
        # Add the directory structure and mp3 to the song title
        song = f'{self.base_dir}/{song}.mp3'
        # Load the song using Mutagen
        song_mut = MP3(song)
        # Get the length of the song
        self.song_len = song_mut.info.length
        # Convert to time format
        converted_song_len = time.strftime('%M:%S', time.gmtime(self.song_len))

        # Increase the current time by 1 second
        current_time += 1

        if int(self.song_slider.get()) == int(self.song_len):
            self.status_bar.config(
                text=f'Elapsed Time: {converted_song_len} of {converted_song_len}')
        elif self.paused:
            pass
        elif int(self.song_slider.get()) == int(current_time):
            # Update the slider position
            slider_position = int(self.song_len)
            self.song_slider.config(
                to=slider_position, value=int(current_time))

        else:
            # Update the slider position
            slider_position = int(self.song_len)
            self.song_slider.config(
                to=slider_position, value=int(self.song_slider.get()))

            # Convert to time format
            converted_current_time = time.strftime(
                '%M:%S', time.gmtime(int(self.song_slider.get())))

            # Display the time in the status bar
            self.status_bar.config(
                text=f'Elapsed Time: {converted_current_time} of {converted_song_len}')

            # Move the slider one second forward
            next_time = int(self.song_slider.get()) + 1
            self.song_slider.config(value=next_time)

        # Update the time
        self.status_bar.after(1000, self.play_time)

    # Play the selected song
    def play(self):
        if self.paused:
            # Resume playback
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            # Set the stop variable to False to allow playback
            self.stopped = False
            song = self.song_box.get(ACTIVE)
            song = f'{self.base_dir}/{song}.mp3'

            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0)

            # Call the play_time function to get the duration of the song
            self.play_time()

    def stop(self):
        # Reset the slider and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)
        # Stop the song
        pygame.mixer.music.stop()
        self.song_box.selection_clear(ACTIVE)

        # Clear the status bar
        self.status_bar.config(text='')

        # Set the stop variable to True
        self.stopped = True

    # Play the next song in the playlist
    def next_song(self):
        # Reset the slider and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)

        # Get the current song number in the tuple
        next_one = self.song_box.curselection()
        # Add one to the current song number
        next_one = next_one[0] + 1
        # Get the song title from the playlist
        song = self.song_box.get(next_one)
        # Add the directory structure and mp3 to the song title
        song = f'{self.base_dir}/{song}.mp3'
        # Load and play the song
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)

        # Clear the active line in the playlist
        self.song_box.selection_clear(0, END)

        # Activate the new song line
        self.song_box.activate(next_one)

        # Set the active line to the next song
        self.song_box.selection_set(next_one, last=None)

    # Play the previous song in the playlist
    def previous_song(self):
        # Reset the slider and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)
        # Get the current song number in the tuple
        next_one = self.song_box.curselection()
        # Subtract one from the current song number
        next_one = next_one[0] - 1
        # Get the song title from the playlist
        song = self.song_box.get(next_one)
        # Add the directory structure and mp3 to the song title
        song = f'{self.base_dir}/{song}.mp3'
        # Load and play the song
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)

        # Clear the active line in the playlist
        self.song_box.selection_clear(0, END)

        # Activate the new song line
        self.song_box.activate(next_one)

        # Set the active line to the next song
        self.song_box.selection_set(next_one, last=None)

    # Pause the current song
    def pause(self, is_paused):
        self.paused = is_paused

        if self.paused:
            # Resume playback
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            # Pause playback
            pygame.mixer.music.pause()
            self.paused = True

    # Add a single song to the playlist
    def add_song(self):
        song = filedialog.askopenfilename(initialdir=self.base_dir, title="Choose A Song",
                                          filetypes=(("mp3 Files", "*.mp3"),))
        # Remove the directory structure from the song name
        song = os.path.basename(song)
        song = song.replace(".mp3", "")

        # Add the song to the playlist
        self.song_box.insert(END, song)

    # Add multiple songs to the playlist
    def add_many_songs(self):
        songs = filedialog.askopenfilenames(initialdir=self.base_dir, title="Choose A Song",
                                            filetypes=(("mp3 Files", "*.mp3"),))

        for song in songs:
            # Remove the directory structure from the song name
            song = os.path.basename(song)
            song = song.replace(".mp3", "")

            # Add the song to the playlist
            self.song_box.insert(END, song)

    # Delete the selected song from the playlist
    def delete_song(self):
        self.stop()
        # Delete the selected song
        self.song_box.delete(ANCHOR)

    # Delete all songs from the playlist
    def delete_all_songs(self):
        self.stop()
        # Delete all songs
        self.song_box.delete(0, END)

    # Slide to the selected part of the song
    def slide(self, x):
        song = self.song_box.get(ACTIVE)
        song = f'{self.base_dir}/{song}.mp3'

        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0, start=int(self.song_slider.get()))

    # Control the volume
    def volume(self, x):
        pygame.mixer.music.set_volume(self.volume_slider.get())


root = Tk()
MP3Player(root)
root.mainloop()
