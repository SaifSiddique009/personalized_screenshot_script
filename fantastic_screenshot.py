"""
This script provides a graphical user interface (GUI) tool for capturing screenshots of specific regions on the screen.

Features:
    - Allows users to select a screen region by clicking and dragging.
    - Provides a global hotkey (Ctrl+D) to initiate region selection from anywhere.
    - Enables dragging the selected region after it has been finalized.
    - Supports moving the selected region using arrow keys.
    - Remembers the dimensions of the last captured region for quick reuse.
    - Saves screenshots as PNG files.

Usage:
    1. Run the script. A small window with buttons will appear.
    2. Press 'Ctrl+D' or click the 'New Region (Ctrl+D)' button to start selecting a region.
    3. The screen will be overlaid. Click and drag to draw a rectangle around the desired area.
    4. Release the mouse button to finalize the region.
    5. You can now:
        - Drag the selected region by clicking inside it and moving the mouse.
        - Move the region pixel by pixel using the arrow keys.
        - Press 'Space' or click 'Take Screenshot (Space)' to capture the selected area.
        - A file dialog will appear, allowing you to choose where to save the screenshot.
        - Press 'Esc' or click 'Close Region (Esc)' to close the selection overlay without taking a screenshot.
    6. Click 'Reuse Last Region' to quickly select the dimensions of the previously captured region.
    7. To close the application, click the 'X' button on the main window.

Dependencies:
    - tkinter: For the graphical user interface.
    - pillow (PIL): For capturing and saving screenshots.
    - keyboard: For registering the global hotkey.

Ensure these libraries are installed before running the script (e.g., `pip install Pillow keyboard`).
"""
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import ImageGrab
import os
import json
import keyboard  # For global hotkeys

class ScreenshotTool:
    """
    The main class for the Fantastic Screenshot Tool.
    Manages the GUI, region selection, and screenshot capture.
    """
    def __init__(self):
        """Initializes the ScreenshotTool application."""
        self.root = tk.Tk()
        self.root.title("Fantastic Screenshot Tool")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle closing the window

        self.last_width = None
        self.last_height = None
        self.last_region = None  # Store the last region coordinates

        self.save_directory = os.getcwd()
        self.category_counters_file = os.path.join(self.save_directory, 'category_counters.json')
        self.category_counters = self.load_category_counters()

        self.selection_window = None
        self.canvas = None
        self.selection_rect = None
        self.rect_width = 0
        self.rect_height = 0
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.region_set = False
        self.movement_step = 1
        self.dimension_label_id = None
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.create_widgets()
        self.setup_global_hotkey()

    def setup_global_hotkey(self):
        """Sets up the global hotkey (Ctrl+D) to start a new region selection."""
        keyboard.add_hotkey('ctrl+d', self.start_new_region)

    def load_category_counters(self):
        """Loads category counters from a JSON file, if it exists."""
        try:
            if os.path.exists(self.category_counters_file):
                with open(self.category_counters_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading counters: {e}")
            return {}

    def save_category_counters(self):
        """Saves category counters to a JSON file."""
        try:
            with open(self.category_counters_file, 'w') as f:
                json.dump(self.category_counters, f)
        except Exception as e:
            print(f"Error saving counters: {e}")

    def create_widgets(self):
        """Creates the GUI elements for the main window."""
        style = ttk.Style(self.root)
        style.theme_use('clam')

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)

        dimension_frame = ttk.Frame(main_frame)
        dimension_frame.pack(fill='x', pady=5)
        ttk.Label(dimension_frame, text="Last Dimension:").pack(side='left')
        self.dimension_display = ttk.Label(dimension_frame, text="None")
        self.dimension_display.pack(side='left', padx=5)
        ttk.Button(dimension_frame, text="Reuse Last Region", command=self.reuse_last_region).pack(side='left', padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=5)
        ttk.Button(button_frame, text="New Region (Ctrl+D)", command=self.start_new_region).pack(fill='x', pady=2)
        self.screenshot_button = ttk.Button(button_frame, text="Take Screenshot (Space)", command=self.take_screenshot)
        self.screenshot_button.pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Close Region (Esc)", command=self.close_region).pack(fill='x', pady=2)

        self.status_label = ttk.Label(main_frame, text="Ready - Press 'Ctrl+D' to select new region")
        self.status_label.pack(pady=10)

    def reuse_last_region(self):
        """Starts a new region selection using the dimensions of the last captured region."""
        if self.last_region:
            self.start_new_region(initial_coords=self.last_region)

    def start_new_region(self, initial_coords=None):
        """
        Creates a top-level window for region selection.

        Args:
            initial_coords (tuple, optional): Coordinates to initialize the selection rectangle.
                                                Used for reusing the last region. Defaults to None.
        """
        if self.selection_window:
            self.selection_window.destroy()

        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title("Select Region")
        self.selection_window.attributes('-topmost', True, '-alpha', 0.3)
        self.selection_window.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.selection_window.overrideredirect(True)

        self.canvas = tk.Canvas(self.selection_window, highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill='both', expand=True)

        self.canvas.bind('<Button-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.end_selection)

        # Keybindings local to the selection window
        self.selection_window.bind('<space>', lambda e: self.take_screenshot())
        self.selection_window.bind('<Escape>', lambda e: self.close_region())
        self.selection_window.bind('<Left>', lambda e: self.move_region('left'))
        self.selection_window.bind('<Right>', lambda e: self.move_region('right'))
        self.selection_window.bind('<Up>', lambda e: self.move_region('up'))
        self.selection_window.bind('<Down>', lambda e: self.move_region('down'))

        if initial_coords:
            self.start_x, self.start_y, end_x, end_y = initial_coords
            self.selection_rect = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline='blue', width=4, fill="", stipple="gray12") # Improved visual
            self.region_set = True
            self.rect_width = abs(end_x - self.start_x)
            self.rect_height = abs(end_y - self.start_y)
            self.update_dimension_label()
            self.selection_window.attributes('-alpha', 0.15)
            self.status_label.config(text=f"Region set ({self.rect_width}x{self.rect_height}). Use mouse or arrow keys to position. Space to capture.")
            self.canvas.bind('<Button-1>', self.start_drag_move) # Bind drag after creation for reused region
        else:
            self.region_set = False
            self.status_label.config(text="Draw a region by clicking and dragging")

    def move_region(self, direction):
        """Moves the selected region by a predefined step in the specified direction."""
        if not self.region_set or not self.selection_rect:
            return

        coords = self.canvas.coords(self.selection_rect)
        dx = dy = 0
        if direction == 'left':
            dx = -self.movement_step
        elif direction == 'right':
            dx = self.movement_step
        elif direction == 'up':
            dy = -self.movement_step
        elif direction == 'down':
            dy = self.movement_step

        self.canvas.move(self.selection_rect, dx, dy)
        self.update_dimension_label()
        self.status_label.config(
            text=f"Region moved {direction} ({int(coords[0] + dx)}, {int(coords[1] + dy)})"
        )

    def start_selection(self, event):
        """Starts the region selection process when the mouse button is pressed."""
        self.start_x = event.x
        self.start_y = event.y
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='blue', width=4, fill="", stipple="gray12", tags="selection_rect" # Improved visual
        )
        self.region_set = True
        self.canvas.bind('<B1-Motion>', self.update_selection)

        self.update_dimension_label()

    def update_selection(self, event):
        """Updates the selection rectangle as the mouse is dragged."""
        if self.selection_rect:
            self.canvas.coords(self.selection_rect, self.start_x, self.start_y, event.x, event.y)
            self.update_dimension_label(event.x, event.y)

    def end_selection(self, event):
        """Finalizes the selection when the mouse button is released."""
        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            self.rect_width = abs(int(coords[2] - coords[0]))
            self.rect_height = abs(int(coords[3] - coords[1]))
            self.canvas.unbind('<B1-Motion>') # Unbind resizing
            self.canvas.bind('<Button-1>', self.start_drag_move) # Enable dragging after selection

    def start_drag_move(self, event):
        """Starts the process of dragging the selected region."""
        if not self.selection_rect:
            return
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.canvas.bind('<B1-Motion>', self.update_drag_move)
        self.canvas.bind('<ButtonRelease-1>', self.end_drag_move)

    def update_drag_move(self, event):
        """Updates the position of the selected region as it is dragged."""
        if not self.selection_rect:
            return
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.canvas.move(self.selection_rect, dx, dy)
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.update_dimension_label()

    def end_drag_move(self, event):
        """Stops the dragging of the selected region."""
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

    def update_dimension_label(self, end_x=None, end_y=None):
        """Updates the label displaying the dimensions of the selected region."""
        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            x1, y1, x2, y2 = coords
            width = abs(int(x2 - x1))
            height = abs(int(y2 - y1))
            dimension_text = f"{width}x{height}"

            label_x = (x1 + x2) / 2
            label_y = min(y1, y2) - 20

            if not self.dimension_label_id:
                # Ensure dimension_label exists before getting bbox
                self.dimension_label_id = self.canvas.create_text(label_x, label_y, text=dimension_text, fill="white", font=('Arial', 10, 'bold'), tags="dimension_label")
                bbox = self.canvas.bbox("dimension_label")
                if bbox:
                    bg_id = self.canvas.create_rectangle(bbox, fill='black', tags="dimension_label_bg", outline="")
                    self.canvas.tag_raise("dimension_label", "dimension_label_bg")
            else:
                self.canvas.itemconfig(self.dimension_label_id, text=dimension_text)
                self.canvas.coords(self.dimension_label_id, label_x, label_y)
                bbox = self.canvas.bbox("dimension_label")
                if bbox:
                    bg_items = self.canvas.find_withtag("dimension_label_bg")
                    if bg_items:
                        self.canvas.coords(bg_items[0], bbox)
                    else:
                        bg_id = self.canvas.create_rectangle(bbox, fill='black', tags="dimension_label_bg", outline="")
                        self.canvas.tag_raise("dimension_label", "dimension_label_bg")

    def take_screenshot(self):
        """Captures the selected region and saves it to a file."""
        if not self.region_set or not self.selection_rect:
            self.status_label.config(text="Please select a region first!")
            return

        coords = self.canvas.coords(self.selection_rect)
        bbox = (
            int(min(coords[0], coords[2])),
            int(min(coords[1], coords[3])),
            int(max(coords[0], coords[2])),
            int(max(coords[1], coords[3]))
        )

        self.selection_window.withdraw()  # Hide the selection window before capture
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                screenshot.save(file_path)
                self.status_label.config(text=f"Saved: {file_path}")
                self.last_region = bbox  # Save the region when screenshot is taken
                self.last_width = self.rect_width
                self.last_height = self.rect_height
                self.dimension_display.config(text=f"{self.last_width}x{self.last_height}")
        except Exception as e:
            self.status_label.config(text=f"Error taking screenshot: {str(e)}")
        finally:
            self.selection_window.deiconify()  # Show the selection window again

    def close_region(self):
        """Closes the region selection window."""
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None
            self.selection_rect = None
            self.region_set = False
            self.status_label.config(text="Region closed. Press 'Ctrl+D' to select new region")

    def run(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()

    def on_closing(self):
        """Handles the event when the main window is closed."""
        self.root.destroy()

if __name__ == "__main__":
    tool = ScreenshotTool()
    tool.run()