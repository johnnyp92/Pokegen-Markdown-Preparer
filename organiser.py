import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import re

class MarkdownTableGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Table Generator")

        self.header = ""
        self.undo_stack = []
        self.redo_stack = []

        self.create_widgets()
        self.create_tags()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        
        header_label = ttk.Label(header_frame, text="Header:")
        header_label.pack(side=tk.LEFT)
        
        self.header_entry = ttk.Entry(header_frame)
        self.header_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        set_header_btn = ttk.Button(header_frame, text="Set Header", command=self.set_header)
        set_header_btn.pack(side=tk.LEFT, padx=5)
        
        self.active_header_label = ttk.Label(header_frame, text="No header set")
        self.active_header_label.pack(side=tk.LEFT, padx=5)
        
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.text_input = tk.Text(text_frame, height=20)
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.text_output = tk.Text(text_frame, height=20, state=tk.DISABLED)
        self.text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.text_input.bind("<KeyRelease>", self.save_undo_state)
        
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        to_upper_btn = ttk.Button(action_frame, text="To Uppercase", command=self.to_uppercase)
        to_upper_btn.pack(side=tk.LEFT, padx=5)
        
        to_lower_btn = ttk.Button(action_frame, text="To Lowercase", command=self.to_lowercase)
        to_lower_btn.pack(side=tk.LEFT, padx=5)
        
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(10, 0))
        
        include_label = ttk.Label(filter_frame, text="Include:")
        include_label.pack(side=tk.LEFT)
        
        self.filter_include_entry = ttk.Entry(filter_frame)
        self.filter_include_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        exclude_label = ttk.Label(filter_frame, text="Exclude:")
        exclude_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.filter_exclude_entry = ttk.Entry(filter_frame)
        self.filter_exclude_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        generate_markdown_btn = ttk.Button(filter_frame, text="Generate Markdown", command=self.generate_markdown)
        generate_markdown_btn.pack(side=tk.LEFT, padx=5)
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(10, 0))
        
        search_label = ttk.Label(search_frame, text="Search:")
        search_label.pack(side=tk.LEFT)
        
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_text)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        replace_btn = ttk.Button(search_frame, text="Replace", command=self.replace_text)
        replace_btn.pack(side=tk.LEFT, padx=5)
        
        self.root.bind_all("<Control-z>", self.undo)
        self.root.bind_all("<Control-y>", self.redo)
    
    def create_tags(self):
        self.text_input.tag_configure('highlight', background='yellow', foreground='black')
        self.text_output.tag_configure('highlight', background='yellow', foreground='black')
    
    def set_header(self):
        self.header = self.header_entry.get().strip()
        if not self.header:
            messagebox.showwarning("Invalid Header", "Header cannot be empty.")
            return
        self.active_header_label.config(text=f"Active Header: {self.header}")
    
    def generate_markdown(self):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        
        input_text = self.text_input.get("1.0", tk.END).strip()
        lines = input_text.split('\n')
        
        if self.header:
            self.text_output.insert(tk.END, f"{self.header}\n")
            header_parts = self.header.split('|')
            self.text_output.insert(tk.END, f"{'|'.join(['---'] * (len(header_parts) - 2))}\n")
        
        include_filter = self.filter_include_entry.get().strip()
        exclude_filter = self.filter_exclude_entry.get().strip()
        
        processed_lines = []
        
        for line in lines:
            line = self.process_line(line)
            if include_filter and include_filter not in line:
                continue
            if exclude_filter and exclude_filter in line:
                continue
            processed_lines.append(line)
        
        self.text_output.insert(tk.END, "\n".join(processed_lines))
        self.text_output.config(state=tk.DISABLED)
    
    def process_line(self, line):
        match = re.match(r'\d+\.\s+(.*?)\s+(\(.*?\))$', line)
        if match:
            name, details = match.groups()
            return f"| {name} | {details} |"
        else:
            return f"| {line} |"
    
    def to_uppercase(self):
        text = self.text_input.get("1.0", tk.END).strip().upper()
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, text)
    
    def to_lowercase(self):
        text = self.text_input.get("1.0", tk.END).strip().lower()
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, text)
    
    def search_text(self):
        self.text_input.tag_remove('highlight', '1.0', tk.END)
        query = self.search_entry.get().strip()
        if not query:
            return
        start_pos = '1.0'
        while True:
            start_pos = self.text_input.search(query, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(query)}c"
            self.text_input.tag_add('highlight', start_pos, end_pos)
            start_pos = end_pos
        self.text_input.see('1.0')
        messagebox.showinfo("Search Results", f"Highlighted occurrences of '{query}'.")
    
    def replace_text(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        replace_with = simpledialog.askstring("Replace Text", f"Replace '{query}' with:")
        if replace_with is not None:
            content = self.text_input.get("1.0", tk.END)
            content = content.replace(query, replace_with)
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert(tk.END, content)
    
    def undo(self, event=None):
        if self.undo_stack:
            self.redo_stack.append(self.text_input.get("1.0", tk.END))
            last_text = self.undo_stack.pop()
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert(tk.END, last_text)
    
    def redo(self, event=None):
        if self.redo_stack:
            self.undo_stack.append(self.text_input.get("1.0", tk.END))
            last_text = self.redo_stack.pop()
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert(tk.END, last_text)
    
    def save_undo_state(self, event=None):
        self.undo_stack.append(self.text_input.get("1.0", tk.END))
        self.redo_stack.clear()

    def pokegen_mode(self):
        input_text = self.text_input.get("1.0", tk.END).strip()
        lines = input_text.split('\n')
        processed_lines = []
        
        for line in lines:
            match = re.match(r'\d+\.\s+(.*?)\s+(\(.*?\))$', line)
            if match:
                name, details = match.groups()
                processed_lines.append(f"| {name} | {details} |")
            else:
                processed_lines.append(f"| {line} |")
        
        markdown_text = "\n".join(processed_lines)
        
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, markdown_text)
        self.text_output.config(state=tk.DISABLED)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1, padx=5, pady=5)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownTableGenerator(root)
    root.mainloop()
