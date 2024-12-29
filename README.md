# Fantastic Screenshot Tool

A personalized Python-based screenshot tool for capturing specific screen regions.

## What it Does

This script provides a simple graphical interface to:

* **Select a region:** Click and drag on your screen to define the capture area.
* **Move the selection:** Drag the outlined region after it's created or nudge it with arrow keys.
* **Capture screenshots:** Save the selected area as a PNG image.
* **Reuse last region:** Quickly reselect the dimensions of your previous capture.
* **Use global hotkey:** Press `Ctrl+D` from anywhere to start a new selection.

## How to Use

1. **Prerequisites:** Ensure you have Python installed along with the following libraries:
   ```bash
   pip install Pillow keyboard tkinter
   ```
2. **Run the script:** Execute the Python file (e.g., `python your_script_name.py`).
3. **Interface:** A small window will appear with control buttons.
4. **Select Region:**
   - Click the "New Region (Ctrl+D)" button or press `Ctrl+D`.
   - The screen will be overlaid. Click and drag to draw a rectangle.
   - Release the mouse button to finalize the selection.
5. **Manipulate Selection:**
   - **Drag:** Click inside the blue outline and drag to reposition.
   - **Nudge:** Use arrow keys (Left, Right, Up, Down) for fine-tuning.
6. **Take Screenshot:**
   - Press the "Take Screenshot (Space)" button or the `Space` key.
   - A file dialog will appear to save your PNG image.
7. **Reuse Last Region:**
   - Click the "Reuse Last Region" button to select the dimensions of the previously captured area.
8. **Close Selection:**
   - Press the "Close Region (Esc)" button or the `Esc` key to close the selection overlay without saving.
9. **Exit:** Close the main application window.

## Capabilities

* Capture any rectangular area of your screen.
* Precisely adjust the capture region before saving.
* Quickly capture the same region dimensions repeatedly.
* Initiate screenshot selection without having the main window in focus.

## Note

This is a personal use script and may not have all the features of full-fledged screenshot applications.
