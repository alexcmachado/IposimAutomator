"""Implementation of the terminal UI using a scrolled text widget."""

import logging
import queue
from tkinter.scrolledtext import ScrolledText
import tkinter as tk

logger = logging.getLogger()


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    """

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(
            frame,
            state="disabled",
            height=30,
            width=100,
            bg="black",
            fg="white",
            font="TkFixedFont",
        )
        # self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.pack(fill=tk.BOTH, expand=True)
        # self.scrolled_text.tag_config('INFO', foreground='black')
        # self.scrolled_text.tag_config('DEBUG', foreground='gray')
        # self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config("ERROR", foreground="red")
        # self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        """Display a logging record in the scrolled text widget."""
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state="normal")
        self.scrolled_text.insert(tk.END, msg + "\n", record.levelname)
        self.scrolled_text.configure(state="disabled")
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        """Check every 100ms if there is a new message in the queue to display."""
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)
