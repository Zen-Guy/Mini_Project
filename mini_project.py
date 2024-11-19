import tkinter as tk
from tkinter import messagebox
import time
import threading
import csv
from datetime import datetime
import matplotlib.pyplot as plt

class ProductivityTimer:
    def __init__(self, root):
        # Initialize basic configurations for the productivity timer
        self.root = root
        self.root.title("Productivity Timer")
        self.running = False
        self.work_duration = 25 * 60  # Default 25 minutes work period
        self.break_duration = 5 * 60  # Default 5 minutes break period
        self.remaining_time = self.work_duration
        self.is_work_time = True
        self.start_time = None
        self.setup_gui()

    def setup_gui(self):
        # Set up the graphical interface
        self.label = tk.Label(self.root, text="Productivity Timer", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.time_label = tk.Label(self.root, text=self.format_time(self.remaining_time), font=("Helvetica", 24))
        self.time_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_timer)
        self.start_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side="left", padx=5)

        self.change_durations_button = tk.Button(self.root, text="Change Durations", command=self.change_durations)
        self.change_durations_button.pack(side="left", padx=5)

        self.analytics_button = tk.Button(self.root, text="Show Analytics", command=self.show_analytics)
        self.analytics_button.pack(pady=10)

    def format_time(self, seconds):
        # Converts seconds into MM:SS format
        minutes, seconds = divmod(seconds, 60)
        # Using leading zeroes for consistency
        return f"{minutes:02d}:{seconds:02d}"

    def timer(self):
        # Timer loop for counting down the time
        while self.running:
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.update_timer_label()
                # Artificial delay to simulate actual countdown behavior
                time.sleep(1)
            else:
                self.running = False
                session_type = "Work" if self.is_work_time else "Break"
                self.log_session(session_type)
                
                # Notify the user that the session has ended
                session_end_message = f"{session_type} session complete! Please start the next session manually."
                messagebox.showinfo("Session Complete", session_end_message)

                # Toggle session type (so next start uses the opposite duration)
                self.is_work_time = not self.is_work_time
                self.remaining_time = self.work_duration if self.is_work_time else self.break_duration
                self.update_timer_label()  # Update UI to reflect the reset timer without starting automatically

    def update_timer_label(self):
        # Updates the timer display
        self.time_label.config(text=self.format_time(self.remaining_time))

    def start_timer(self):
        # Starts the timer thread if it's not already running
        if not self.running:
            self.running = True
            self.start_time = datetime.now()  # Log start time for session
            t = threading.Thread(target=self.timer)
            t.daemon = True  # Ensure thread exits when main GUI closes
            t.start()

    def reset_timer(self):
        # Resets the timer back to work duration
        self.running = False
        self.is_work_time = True
        self.remaining_time = self.work_duration
        self.update_timer_label()  # Immediate UI update

    def change_durations(self):
        # Opens a dialog to change work and break durations
        def set_durations():
            try:
                # Update durations from user input
                self.work_duration = int(work_entry.get()) * 60
                self.break_duration = int(break_entry.get()) * 60
                self.remaining_time = self.work_duration
                self.update_timer_label()
                duration_window.destroy()  # Close the input window
            except ValueError:
                # Display an error message if input is invalid
                messagebox.showerror("Invalid Input", "Please enter valid integers for durations.")

        duration_window = tk.Toplevel(self.root)
        duration_window.title("Change Durations")

        # Input fields for new durations
        tk.Label(duration_window, text="Work Duration (minutes):").pack(pady=5)
        work_entry = tk.Entry(duration_window)
        work_entry.insert(0, str(self.work_duration // 60))  # Populate with current value
        work_entry.pack(pady=5)

        tk.Label(duration_window, text="Break Duration (minutes):").pack(pady=5)
        break_entry = tk.Entry(duration_window)
        break_entry.insert(0, str(self.break_duration // 60))  # Populate with current value
        break_entry.pack(pady=5)

        tk.Button(duration_window, text="Set Durations", command=set_durations).pack(pady=10)

    def log_session(self, session_type):
        # Log session data to a CSV file
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 60  # Convert to minutes
        try:
            with open("productivity_log.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([session_type, self.start_time.strftime("%Y-%m-%d %H:%M:%S"), duration])
        except IOError:
            # Handle file access issues gracefully
            messagebox.showerror("Error", "Could not write to log file.")

    def show_analytics(self):
        # Display analytics for completed sessions
        sessions = {"Work": 0, "Break": 0}
        try:
            with open("productivity_log.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    # Accumulate total times for work/break
                    sessions[row[0]] += float(row[2])
        except FileNotFoundError:
            messagebox.showinfo("No Data", "Log file not found.")
            return

        if sum(sessions.values()) == 0:
            messagebox.showinfo("No Data", "No sessions recorded yet.")
            return

        labels = list(sessions.keys())
        values = list(sessions.values())

        plt.bar(labels, values, color=['blue', 'green'])
        plt.xlabel("Session Type")
        plt.ylabel("Total Time (minutes)")
        plt.title("Productivity Timer Analytics")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityTimer(root)
    root.mainloop()
