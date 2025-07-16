
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import os
import json
import requests
import subprocess
import sys
from dotenv import load_dotenv

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import yt_dlp
except ImportError:
    install("yt-dlp")
    import yt_dlp
import threading

class YoutubeSummarizer:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Summarizer")
        self.root.geometry("700x600")

        load_dotenv() # Load environment variables

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam') # You can try 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'

        # URL Input
        self.url_label = tk.Label(root, text="YouTube URL or Playlist URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        # Download and Summarize Button
        self.summarize_button = tk.Button(root, text="Download and Summarize", command=self.start_summarize_thread)
        self.summarize_button.pack()

        # Summary Display
        self.summary_label = tk.Label(root, text="Summary:")
        self.summary_label.pack()
        self.summary_text = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
        self.summary_text.pack()

        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack_forget() # Hide initially

        # Action Buttons
        self.action_frame = tk.Frame(root)
        self.action_frame.pack()
        self.copy_button = tk.Button(self.action_frame, text="Copy Summary", command=self.copy_summary)
        self.copy_button.pack(side=tk.LEFT)
        self.save_button = tk.Button(self.action_frame, text="Save to Markdown", command=self.save_to_markdown)
        self.save_button.pack(side=tk.LEFT)

        # Settings Button
        self.settings_button = tk.Button(root, text="Settings", command=self.open_settings)
        self.settings_button.pack()

        # Settings variables
        self.config_file = "config.json"
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.user_prompt = "Summarize the following transcript:"
        self.system_prompt = "You are a helpful assistant that summarizes YouTube video transcripts:"
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    self.user_prompt = settings.get("user_prompt", "Summarize the following transcript:")
                    self.system_prompt = settings.get("system_prompt", "You are a helpful assistant that summarizes YouTube video transcripts.")
                    self.context_prompt = settings.get("context_prompt", "")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Could not read settings from config.json. File might be corrupted.")
                self.user_prompt = "Summarize the following transcript:"
                self.system_prompt = "You are a helpful assistant that summarizes YouTube video transcripts."
                self.context_prompt = ""
        else:
            self.user_prompt = "Summarize the following transcript:"
            self.system_prompt = "You are a helpful assistant that summarizes YouTube video transcripts."
            self.context_prompt = ""

    def start_summarize_thread(self):
        thread = threading.Thread(target=self.summarize)
        thread.start()

    def summarize(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        if not self.api_key:
            messagebox.showerror("Error", "Please enter your OpenRouter API key in the settings.")
            return

        self.summary_text.delete(1.0, tk.END)
        self.progress_bar.pack()
        self.progress_bar.start()
        self.root.update_idletasks()

        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'vtt',
                'skip_download': True,
                'outtmpl': '%(id)s.%(ext)s',
                'nocheckcertificate': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [info])
                
                self.summary_text.delete(1.0, tk.END)

                for entry in entries:
                    video_id = entry.get("id")
                    video_title = entry.get("title", "Unknown Title")
                    
                    
                    ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                    transcript_file = f"{video_id}.en.vtt"
                    
                    if os.path.exists(transcript_file):
                        with open(transcript_file, 'r', encoding='utf-8') as f:
                            transcript = f.read()
                        
                        os.remove(transcript_file)

                        

                        summary = self.get_summary(transcript)
                        self.summary_text.insert(tk.END, f"\n--- Summary for: {video_title} ---\n\n")
                        self.summary_text.insert(tk.END, summary)
                        self.summary_text.insert(tk.END, "\n\n")
                    else:
                        self.summary_text.insert(tk.END, f"Could not find transcript for: {video_title}\n\n")

            self.progress_bar.stop()
            self.progress_bar.pack_forget()


        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            messagebox.showerror("Error", f"An error occurred: {e}")


    def get_summary(self, transcript):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        final_system_prompt = self.system_prompt
        if self.context_prompt:
            final_system_prompt = f"{self.context_prompt}\n\n{self.system_prompt}"

        data = {
            "model": "google/gemini-2.5-flash",
            "messages": [
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": f"{self.user_prompt}\n\n{transcript}"}
            ]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"

    def copy_summary(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.summary_text.get(1.0, tk.END))

    def save_to_markdown(self):
        summary_content = self.summary_text.get(1.0, tk.END)
        if not summary_content.strip():
            messagebox.showerror("Error", "There is no summary to save.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.* painters")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)

    def open_settings(self):
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.transient(self.root) # Make settings window appear on top
        self.settings_window.grab_set() # Disable interaction with the main window

        settings_frame = ttk.Frame(self.settings_window, padding="10 10 10 10")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # API Key
        ttk.Label(settings_frame, text="OpenRouter API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(settings_frame, width=50, show="*")
        self.api_key_entry.insert(0, self.api_key)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # User Prompt
        ttk.Label(settings_frame, text="User Prompt:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_prompt_entry = scrolledtext.ScrolledText(settings_frame, width=60, height=5, wrap=tk.WORD)
        self.user_prompt_entry.insert(tk.END, self.user_prompt)
        self.user_prompt_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # System Prompt
        ttk.Label(settings_frame, text="System Prompt:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.system_prompt_entry = scrolledtext.ScrolledText(settings_frame, width=60, height=5, wrap=tk.WORD)
        self.system_prompt_entry.insert(tk.END, self.system_prompt)
        self.system_prompt_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Context Prompt
        ttk.Label(settings_frame, text="Context (prepended to System Prompt):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.context_prompt_entry = scrolledtext.ScrolledText(settings_frame, width=60, height=5, wrap=tk.WORD)
        self.context_prompt_entry.insert(tk.END, self.context_prompt)
        self.context_prompt_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Save Button
        ttk.Button(settings_frame, text="Save", command=self.save_settings).grid(row=4, column=0, columnspan=2, pady=10)

        settings_frame.grid_columnconfigure(1, weight=1)

    def save_settings(self):
        self.user_prompt = self.user_prompt_entry.get("1.0", tk.END).strip()
        self.system_prompt = self.system_prompt_entry.get("1.0", tk.END).strip()
        self.context_prompt = self.context_prompt_entry.get("1.0", tk.END).strip()

        settings = {
            "user_prompt": self.user_prompt,
            "system_prompt": self.system_prompt,
            "context_prompt": self.context_prompt
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Could not save settings to config.json. Error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while saving settings. Error: {e}")
        
        self.settings_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeSummarizer(root)
    root.mainloop()
