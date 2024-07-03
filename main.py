import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os
import webbrowser
import requests
import threading
import psutil

class DjangoServerManager:
    def __init__(self, master):
        self.master = master
        master.title("Server Manager")
        master.geometry("400x350")  # Встановлення розміру вікна
        master.minsize(400, 350)  # Мінімальний розмір вікна
        master.maxsize(400, 350)  # Максимальний розмір вікна

        self.select_project_button = tk.Button(master, text="Select Project", command=self.select_project ,bg='#FFE933')
        self.select_project_button.pack(pady=10)

        self.start_button = tk.Button(master, text="Start Server", command=self.start_server, bg="green", fg="white")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Server", command=self.stop_server, bg="red", fg="white")
        self.stop_button.pack(pady=10)

        self.open_browser_button = tk.Button(master, text="Open in Browser", command=self.open_in_browser, bg="blue", fg="white")
        self.open_browser_button.pack(pady=10)

        self.status_label = tk.Label(master, text="Server Status:")
        self.status_label.pack(pady=10)

        self.status_canvas = tk.Canvas(master, width=20, height=20)
        self.status_canvas.pack(pady=10)
        self.status_indicator = self.status_canvas.create_oval(5, 5, 20, 20, fill="red")

        self.server_process = None

        self.project_path = None

        self.project_path_label = tk.Label(master, text="Project Path:")
        self.project_path_label.pack(pady=10)
        self.project_path_entry = tk.Entry(master, state='readonly', width=30)
        self.project_path_entry.pack(pady=10)

        self.load_project_path()

    def select_project(self):
        self.project_path = filedialog.askdirectory()
        if self.project_path:
            if not os.listdir(self.project_path):  # Перевірка, чи папка не пуста
                messagebox.showwarning("Warning", "Selected folder is empty.")
                self.project_path = None
            else:
                self.save_project_path()
                self.project_path_entry.config(state='normal')
                self.project_path_entry.delete(0, tk.END)
                self.project_path_entry.insert(0, self.project_path)
                self.project_path_entry.config(state='readonly')

    def load_project_path(self):
        try:
            with open("link.txt", "r") as file:
                self.project_path = file.read().strip()
                if self.project_path:
                    self.project_path_entry.config(state='normal')
                    self.project_path_entry.insert(0, self.project_path)
                    self.project_path_entry.config(state='readonly')
        except FileNotFoundError:
            pass

    def save_project_path(self):
        with open("link.txt", "w") as file:
            file.write(self.project_path)

    def start_server(self):
        if self.server_process is None and self.project_path:
            self.start_button.config(state="disabled")
            self.server_process = subprocess.Popen(['python', os.path.join(self.project_path, 'manage.py'), 'runserver'], cwd=self.project_path)
            threading.Thread(target=self.check_server_status).start()

    def check_server_status(self):
        while True:
            try:
                response = requests.get('http://127.0.0.1:8000')
                if response.status_code == 200:
                    self.master.after(0, self.server_started)
                    break
            except requests.ConnectionError:
                pass

    def server_started(self):
        self.status_canvas.itemconfig(self.status_indicator, fill="green")
        self.start_button.config(state="normal")
        messagebox.showinfo("Info", "Server started")

    def stop_server(self):
        if self.server_process is not None:
            try:
                parent = psutil.Process(self.server_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                gone, still_alive = psutil.wait_procs([parent], timeout=5)
                for p in still_alive:
                    p.kill()

                self.server_process.wait()  # Дочекаємось завершення основного процесу
                self.server_process = None
                self.status_canvas.itemconfig(self.status_indicator, fill="red")
                messagebox.showinfo("Info", "Server stopped")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop server: {e}")
        else:
            messagebox.showwarning("Warning", "Server is not running")

    def open_in_browser(self):
        address = 'http://127.0.0.1:8000'
        webbrowser.open(address)

if __name__ == "__main__":
    root = tk.Tk()
    django_server_manager = DjangoServerManager(root)
    root.mainloop()