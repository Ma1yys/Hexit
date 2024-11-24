import customtkinter as ctk
from tkinter import filedialog, messagebox
import os


class HexEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration
        self.title("Hex Editor")
        self.geometry("560x600")
        self.text_size = 14
        self.current_file = None
        self.updating = False  # Lock for preventing cyclic updates
        self.bytes_per_line = 16  # Number of bytes per line for hex and text display

        self.create_widgets()

    def create_widgets(self):
        """Creates and lays out all widgets."""
        # Control frame
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", pady=5, padx=5)

        self.open_file_button = ctk.CTkButton(self.control_frame, text="Open File", command=self.open_file)
        self.open_file_button.pack(side="left", padx=5)

        self.save_file_button = ctk.CTkButton(self.control_frame, text="Save File", command=self.save_file)
        self.save_file_button.pack(side="left", padx=5)

        # Text size controls
        self.text_size_label = ctk.CTkLabel(self.control_frame, text="Text Size:")
        self.text_size_label.pack(side="left", padx=(20, 5))

        self.text_size_entry = ctk.CTkEntry(self.control_frame, width=50)
        self.text_size_entry.insert(0, str(self.text_size))
        self.text_size_entry.pack(side="left", padx=5)
        self.text_size_entry.bind("<Return>", lambda e: self.change_text_size())

        # Hex and text viewer layout
        self.viewer_frame = ctk.CTkFrame(self)
        self.viewer_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Hex viewer
        self.hex_viewer = ctk.CTkTextbox(self.viewer_frame, wrap="none", width=400)
        self.hex_viewer.pack(side="left", fill="y", padx=(0, 5))
        self.hex_viewer.bind("<KeyRelease>", self.on_hex_change)

        # Text viewer
        self.textbox = ctk.CTkTextbox(self.viewer_frame, wrap="none", width=400)
        self.textbox.pack(side="right", fill="y", padx=(5, 0))
        self.textbox.bind("<KeyRelease>", self.on_text_change)

        # Configure text appearance
        self.update_textbox_font()

    def open_file(self):
        """Opens a file dialog to select a file and loads its content."""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    data = file.read()
                self.current_file = file_path
                self.load_content(data)
                self.title(f"Hex Editor - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        """Saves the current content to a file."""
        file_path = filedialog.asksaveasfilename()
        if file_path:
            try:
                with open(file_path, "wb") as file:
                    data = self.textbox.get("1.0", "end-1c").encode("latin1")
                    file.write(data)
                self.current_file = file_path
                self.load_content(data)  # Reload the saved file
                messagebox.showinfo("Saved", f"File saved successfully to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def load_content(self, data):
        """Loads content into the hex and text views."""
        hex_data = self.to_hex(data)
        text_data = self.to_text(data)

        self.hex_viewer.delete("1.0", "end")
        self.hex_viewer.insert("1.0", hex_data)

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text_data)

    def to_hex(self, data):
        """Converts binary data to a formatted hex string with multiple lines."""
        lines = []
        for i in range(0, len(data), self.bytes_per_line):
            # Extract one line of bytes
            chunk = data[i:i + self.bytes_per_line]
            # Convert to hex
            hex_part = " ".join(f"{byte:02X}" for byte in chunk)
            # Add padding to align
            hex_part = f"{hex_part:<{self.bytes_per_line * 3}}"
            lines.append(hex_part)
        return "\n".join(lines)

    def to_text(self, data):
        """Converts binary data to a formatted text string with multiple lines."""
        lines = []
        for i in range(0, len(data), self.bytes_per_line):
            # Extract one line of bytes
            chunk = data[i:i + self.bytes_per_line]
            # Convert to text, replace non-printable characters with '.'
            text_part = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
            # Add padding to align
            text_part = f"{text_part:<{self.bytes_per_line}}"
            lines.append(text_part)
        return "\n".join(lines)

    def from_hex(self, hex_data):
        """Converts a hex string back to binary data."""
        try:
            return bytes.fromhex(hex_data.replace(" ", ""))
        except ValueError:
            return None

    def on_hex_change(self, event):
        """Updates the text view when hex view changes."""
        if self.updating:
            return
        self.updating = True
        hex_data = self.hex_viewer.get("1.0", "end-1c")
        binary_data = self.from_hex(hex_data)
        if binary_data is not None:
            text_data = self.to_text(binary_data)
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", text_data)
        self.updating = False

    def on_text_change(self, event):
        """Updates the hex view when text view changes."""
        if self.updating:
            return
        self.updating = True
        text_data = self.textbox.get("1.0", "end-1c")
        binary_data = text_data.encode("latin1", errors="replace")
        hex_data = self.to_hex(binary_data)
        self.hex_viewer.delete("1.0", "end")
        self.hex_viewer.insert("1.0", hex_data)
        self.updating = False

    def change_text_size(self):
        """Changes the text size."""
        try:
            new_size = int(self.text_size_entry.get())
            if new_size > 0:
                self.text_size = new_size
                self.update_textbox_font()
        except ValueError:
            messagebox.showerror("Error", "Invalid text size.")

    def update_textbox_font(self):
        """Updates the font size of the text views."""
        self.hex_viewer.configure(font=("Courier", self.text_size))
        self.textbox.configure(font=("Courier", self.text_size))


if __name__ == "__main__":
    app = HexEditorApp()
    app.mainloop()

