import customtkinter as ctk
from tkinter import filedialog, messagebox
import os


# Set appearance mode for CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class HexEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Main window configuration
        self.title("Hex Editor")
        self.geometry("1000x600")

        # Default text size
        self.text_size = 12
        self.chunk_size = 5000  # Size of the data loaded at once (in bytes)

        # Control panel
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=10, padx=10, fill="x")

        # File selection button
        self.select_file_button = ctk.CTkButton(
            self.control_frame, text="Select File", command=self.open_file
        )
        self.select_file_button.pack(side="left", padx=10)

        # Create new file button
        self.create_file_button = ctk.CTkButton(
            self.control_frame, text="Create New File", command=self.create_new_file
        )
        self.create_file_button.pack(side="left", padx=10)

        # Save file button
        self.save_file_button = ctk.CTkButton(
            self.control_frame, text="Save Changes", command=self.save_file
        )
        self.save_file_button.pack(side="left", padx=10)

        # Text size setting
        self.text_size_label = ctk.CTkLabel(self.control_frame, text="Text Size:")
        self.text_size_label.pack(side="left", padx=(20, 5))

        self.text_size_entry = ctk.CTkEntry(self.control_frame, width=50)
        self.text_size_entry.insert(0, str(self.text_size))
        self.text_size_entry.pack(side="left")

        # Add event to confirm text size change on Enter key press
        self.text_size_entry.bind("<Return>", self.change_text_size)

        # Split the window into two frames (left for editor, right for hex view)
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Textbox for displaying file content (left)
        self.textbox = ctk.CTkTextbox(self.left_frame, wrap="word", state="normal")
        self.textbox.pack(expand=True, fill="both")

        # Textbox for displaying hexadecimal data (right)
        self.hex_viewer = ctk.CTkTextbox(self.right_frame, wrap="word", state="normal")
        self.hex_viewer.pack(expand=True, fill="both")

        # Set the style of the text boxes
        self.update_textbox_font()

        # Variables for file management
        self.file_path = None
        self.file_data = None
        self.current_pos = 0

        # Hold info about selected text and hex for highlighting
        self.selected_text = None
        self.selected_hex = None

        # Bind events for selecting text in both the left and right panels
        self.textbox.bind("<ButtonRelease-1>", self.on_text_select)
        self.hex_viewer.bind("<ButtonRelease-1>", self.on_hex_select)

        # Keyboard shortcut for saving (CTRL+S)
        self.bind("<Control-s>", self.save_file)

        # Monitor text changes
        self.textbox.bind("<KeyRelease>", self.on_text_change)
        self.hex_viewer.bind("<KeyRelease>", self.on_hex_change)

    def open_file(self):
        """Opens file dialog to select and display the file content."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path = file_path
            self.current_pos = 0
            self.load_next_chunk()

    def create_new_file(self):
        """Creates a new file and opens it for editing."""
        file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All files", "*.*")])
        if file_path:
            # Create an empty file
            with open(file_path, "wb") as new_file:
                pass  # Just create an empty file
            # Set the file path for editing
            self.file_path = file_path
            self.current_pos = 0
            self.load_next_chunk()

    def load_next_chunk(self):
        """Loads part of the file as raw data (binary content)."""
        if not self.file_path:
            return

        try:
            with open(self.file_path, "rb") as file:
                file.seek(self.current_pos)  # Move to the current position in the file
                chunk = file.read(self.chunk_size)  # Load the next chunk of the file

                if chunk:
                    # Show binary data as hex string
                    raw_hex = chunk.hex()  # Convert binary data to hex format
                    display_text = " ".join([raw_hex[i:i+2] for i in range(0, len(raw_hex), 2)])

                    # Display the data in the left textbox as text
                    self.textbox.delete("1.0", "end")
                    self.textbox.insert("1.0", chunk.decode(errors="ignore"))  # Show as text

                    # Display hex data in the right textbox
                    self.hex_viewer.delete("1.0", "end")
                    self.hex_viewer.insert("1.0", display_text)  # Show hex text

                    self.current_pos += len(chunk)  # Move position forward for the next chunk
                else:
                    self.textbox.delete("1.0", "end")
                    self.textbox.insert("1.0", "End of file.")
                    self.hex_viewer.delete("1.0", "end")
                    self.hex_viewer.insert("1.0", "End of file.")
        except Exception as e:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", f"Error loading file: {e}")
            self.hex_viewer.delete("1.0", "end")
            self.hex_viewer.insert("1.0", f"Error loading file: {e}")

    def save_file(self, event=None):
        """Saves the modified hex data back to the file."""
        if not self.file_path:
            return

        try:
            hex_data = self.hex_viewer.get("1.0", "end-1c")  # Get hex text
            hex_data = hex_data.replace(" ", "")  # Remove spaces between hex values
            if len(hex_data) % 2 != 0:
                raise ValueError("Hex data must have an even number of characters.")
            
            # Convert hex data back to bytes
            byte_data = bytes.fromhex(hex_data)

            # File dialog to choose where to save the file
            save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All files", "*.*")])

            if save_path:
                with open(save_path, "wb") as file:
                    file.write(byte_data)

                # Confirmation that the file has been saved
                messagebox.showinfo("Saved", "File has been successfully saved.")

                # Reload the file that was just saved so the user can continue editing
                self.file_path = save_path
                self.current_pos = 0
                self.load_next_chunk()

        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")

    def change_text_size(self, event=None):
        """Changes the text size based on user input."""
        try:
            new_size = int(self.text_size_entry.get())
            if new_size > 0:
                self.text_size = new_size
                self.update_textbox_font()
            else:
                raise ValueError("Text size must be greater than 0.")
        except ValueError:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", "Error: Invalid text size.")

    def update_textbox_font(self):
        """Updates the font of the textboxes based on the text size."""
        self.textbox.configure(font=("Courier New", self.text_size))
        self.hex_viewer.configure(font=("Courier New", self.text_size))

    def on_text_change(self, event=None):
        """Handles changes in the text field and updates hex display."""
        text_content = self.textbox.get("1.0", "end-1c")
        updated_hex = text_content.encode("utf-8").hex()
        self.hex_viewer.delete("1.0", "end")
        self.hex_viewer.insert("1.0", " ".join([updated_hex[i:i+2] for i in range(0, len(updated_hex), 2)]))

    def on_hex_change(self, event=None):
        """Handles changes in the hex field and updates the text display."""
        hex_content = self.hex_viewer.get("1.0", "end-1c")
        hex_content = hex_content.replace(" ", "")  # Remove spaces
        try:
            updated_text = bytes.fromhex(hex_content).decode(errors="ignore")
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", updated_text)
        except ValueError:
            pass  # Ignore invalid hex content

    def on_text_select(self, event=None):
        """Handles selecting text in the regular text area."""
        selected_text = self.textbox.get("sel.first", "sel.last")
        if selected_text:
            self.selected_text = selected_text
            self.highlight_in_hex(selected_text)

    def on_hex_select(self, event=None):
        """Handles selecting hex text in the hex view."""
        selected_hex = self.hex_viewer.get("sel.first", "sel.last")
        if selected_hex:
            self.selected_hex = selected_hex
            self.highlight_in_text(selected_hex)

    def highlight_in_text(self, selected_hex):
        """Highlights the corresponding text bytes."""
        self.textbox.tag_remove("highlight", "1.0", "end")
        selected_text = bytes.fromhex(selected_hex).decode(errors="ignore")
        start_idx = self.textbox.search(selected_text, "1.0", "end", regexp=True)
        if start_idx:
            end_idx = f"{start_idx}+{len(selected_text)}c"
            self.textbox.tag_add("highlight", start_idx, end_idx)
            self.textbox.tag_config("highlight", background="yellow")

    def highlight_in_hex(self, selected_text):
        """Highlights the corresponding hex bytes."""
        self.hex_viewer.tag_remove("highlight", "1.0", "end")
        selected_hex = selected_text.encode("utf-8").hex()
        start_idx = self.hex_viewer.search(selected_hex, "1.0", "end", regexp=True)
        if start_idx:
            end_idx = f"{start_idx}+{len(selected_hex)}c"
            self.hex_viewer.tag_add("highlight", start_idx, end_idx)
            self.hex_viewer.tag_config("highlight", background="yellow")


if __name__ == "__main__":
    app = HexEditorApp()
    app.mainloop()
