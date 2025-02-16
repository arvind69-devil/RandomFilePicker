import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

import random_file_picker as rfp

# GUI class
class RandomFilePickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Random File Picker")
        self.root.configure(bg="white")  # Set background to white

        # Maximize the window by default
        self.root.state("zoomed")  # Opens the window in maximized state

        # Load the background image
        try:
            self.bg_image = Image.open("background.jpg")
            self.bg_image = self.bg_image.resize(
                (self.root.winfo_screenwidth(), self.root.winfo_screenheight()),
                Image.Resampling.LANCZOS  # Use LANCZOS instead of ANTIALIAS
            )
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(relwidth=1, relheight=1)  # Cover the entire window
        except FileNotFoundError:
            messagebox.showerror("Error", "background.jpg not found!")

        # Load the spin_the_wheel.gif
        try:
            self.spin_image = Image.open("spin_the_wheel.gif")
            self.spin_frames = []
            try:
                while True:
                    frame = ImageTk.PhotoImage(self.spin_image.copy())
                    self.spin_frames.append(frame)
                    self.spin_image.seek(len(self.spin_frames))  # Move to the next frame
            except EOFError:
                pass
        except FileNotFoundError:
            messagebox.showerror("Error", "spin_the_wheel.gif not found!")
            self.spin_frames = []

        # Create GUI elements
        self.create_widgets()

        # Start GIF animation (only if frames are loaded)
        if self.spin_frames:
            self.current_frame = 0
            self.animate_gif()

    def create_widgets(self):
        # Frame for the center content
        center_frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.RIDGE)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Label for the spin image
        if self.spin_frames:
            self.image_label = tk.Label(center_frame, image=self.spin_frames[0], bg="white")
            self.image_label.pack(pady=10)
        else:
            self.image_label = tk.Label(center_frame, text="No GIF found", bg="white")
            self.image_label.pack(pady=10)

        # Function to create a rounded rectangle button
        def create_rounded_button(canvas, text, command, x, y, width, height, radius, bg, fg, font):
            canvas.create_oval(x, y, x + radius, y + radius, fill=bg, outline=bg)
            canvas.create_oval(x + width - radius, y, x + width, y + radius, fill=bg, outline=bg)
            canvas.create_oval(x, y + height - radius, x + radius, y + height, fill=bg, outline=bg)
            canvas.create_oval(x + width - radius, y + height - radius, x + width, y + height, fill=bg, outline=bg)
            canvas.create_rectangle(x + radius / 2, y, x + width - radius / 2, y + height, fill=bg, outline=bg)
            canvas.create_rectangle(x, y + radius / 2, x + width, y + height - radius / 2, fill=bg, outline=bg)
            button = tk.Button(canvas, text=text, command=command, bg=bg, fg=fg, font=font, relief="flat")
            button.place(x=x + radius / 2, y=y + radius / 2, width=width - radius, height=height - radius)
            return button

        # Create a canvas to draw rounded buttons
        canvas = tk.Canvas(center_frame, bg="white", highlightthickness=0, width=220, height=250)
        canvas.pack(pady=10)

        # Button to select a folder
        self.folder_button = create_rounded_button(
            canvas, "Select Folder", self.select_folder, 10, 10, 200, 50, 20, "#FF6F61", "black", ("Comic Sans MS", 14)
        )

        # Button to spin the wheel
        self.spin_button = create_rounded_button(
            canvas, "Spin the Wheel", self.spin, 10, 70, 200, 50, 20, "#FFB6C1", "black", ("Comic Sans MS", 14)
        )
        self.spin_button.config(state=tk.DISABLED)

        # Label to display the selected file
        self.selected_file_label = tk.Label(
            center_frame, text="No file selected yet.", wraplength=400,
            bg="white", fg="#333333", font=("Comic Sans MS", 14)
        )
        self.selected_file_label.pack(pady=10)

        # Button to view cache
        self.cache_button = create_rounded_button(
            canvas, "View Cache", self.view_cache, 10, 130, 200, 50, 20, "#88B04B", "black", ("Comic Sans MS", 14)
        )

        # Button to clear cache
        self.clear_cache_button = create_rounded_button(
            canvas, "Clear Cache", self.clear_cache, 10, 190, 200, 50, 20, "#FF6F61", "black", ("Comic Sans MS", 14)
        )

        # Center-align the canvas
        canvas.pack(anchor="center", expand=True)

    def animate_gif(self):
        # Update the GIF frame
        self.current_frame = (self.current_frame + 1) % len(self.spin_frames)
        self.image_label.config(image=self.spin_frames[self.current_frame])
        self.root.after(100, self.animate_gif)  # Update every 100ms

    def select_folder(self):
        # Open folder selection dialog
        self.folder_path = filedialog.askdirectory(title="Select a folder to pick a random file from")
        if self.folder_path:
            self.spin_button.config(state=tk.NORMAL)
            self.selected_file_label.config(text="Folder selected. Click 'Spin the Wheel' to pick a file.")

    def spin(self):
        # Pick a random file
        files = [f for f in os.listdir(self.folder_path) if os.path.isfile(os.path.join(self.folder_path, f))]
        if files:
            selected_file = random.choice(files)
            file_path = os.path.join(self.folder_path, selected_file)
            self.selected_file_label.config(text=f"Selected file: {selected_file}")

            # Ask the user what to do with the file
            self.ask_action(file_path, selected_file)
        else:
            messagebox.showwarning("No Files", "No files found in the selected folder.")

    def ask_action(self, file_path, selected_file):
        # Ask the user what action to take
        action = messagebox.askyesno(
            "Action",
            f"Do you want to open this file?\n\nFile: {selected_file}",
            icon="question"
        )
        if action:
            rfp.open_file(file_path)
            rfp.add_to_cache(file_path, "opened")
        else:
            rfp.add_to_cache(file_path, "not opened")

    def view_cache(self):
        # Prevent multiple cache dialogs
        if hasattr(self, "cache_window") and self.cache_window.winfo_exists():
            return

        # Display the cache in a new window
        cache = rfp.get_cached_files()
        self.cache_window = tk.Toplevel(self.root)
        self.cache_window.title("Cache")
        self.cache_window.configure(bg="white")

        # Create a treeview to display the cache
        tree = ttk.Treeview(self.cache_window, columns=("File", "Action"), show="headings")
        tree.heading("File", text="File")
        tree.heading("Action", text="Action")
        tree.pack(fill="both", expand=True)

        # Insert cache data into the treeview
        for file_path, data in cache.items():
            tree.insert("", "end", values=(file_path, data["action"]))

    def clear_cache(self):
        # Clear the cache
        if os.path.exists(rfp.CACHE_FILE):
            os.remove(rfp.CACHE_FILE)
            messagebox.showinfo("Cache Cleared", "The cache has been cleared.")
        else:
            messagebox.showinfo("Cache Cleared", "The cache is already empty.")

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = RandomFilePickerGUI(root)
    root.mainloop()