import serial
import threading
import queue
import tkinter as tk

PORT = "/dev/cu.usbserial-10"   
BAUD = 9600


# App state
data_queue = queue.Queue()

app_data = {
    "state": "Idle",
    "level": "1",
    "last_event": "Waiting",
    "status": "Waiting for Arduino...",
    "button": "-",
}


# Colors / theme
BG = "#0b1020"
CARD = "#111827"
CARD_2 = "#1f2937"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
ACCENT = "#38bdf8"
GREEN = "#22c55e"
YELLOW = "#f59e0b"
RED = "#ef4444"
PURPLE = "#a855f7"
PINK = "#ec4899"
BORDER = "#334155"

BUTTON_NAMES = {
    "0": "Button 0",
    "1": "Button 1",
    "2": "Button 2",
    "3": "Button 3",
    "-": "-"
}

def state_color(state: str) -> str:
    s = state.lower()
    if "idle" in s:
        return ACCENT
    if "show" in s:
        return PURPLE
    if "wait" in s:
        return YELLOW
    if "level" in s:
        return GREEN
    if "reset" in s or "fail" in s:
        return RED
    return ACCENT

def event_color(event: str) -> str:
    e = event.lower()
    if "correct" in e or "level up" in e or "sequence complete" in e:
        return GREEN
    if "wrong" in e or "timeout" in e or "reset" in e:
        return RED
    if "started" in e:
        return ACCENT
    return TEXT

# -------------------------
# Serial thread
# -------------------------
def serial_reader():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        while True:
            raw = ser.readline().decode(errors="ignore").strip()
            if raw:
                data_queue.put(raw)
    except Exception as e:
        data_queue.put(f"MSG:Serial error: {e}")
        data_queue.put("STATE:ERROR")

# -------------------------
# UI update helpers
# -------------------------
def update_badge(label, text, color):
    label.config(text=text, bg=color, fg="white")

def update_value(label, text, color=TEXT):
    label.config(text=text, fg=color)

def process_serial():
    while not data_queue.empty():
        line = data_queue.get()

        if line.startswith("STATE:"):
            app_data["state"] = line.split(":", 1)[1].replace("_", " ").title()

        elif line.startswith("LEVEL:"):
            app_data["level"] = line.split(":", 1)[1]

        elif line.startswith("EVENT:"):
            app_data["last_event"] = line.split(":", 1)[1].replace("_", " ").title()

        elif line.startswith("MSG:"):
            app_data["status"] = line.split(":", 1)[1]

        elif line.startswith("BUTTON:"):
            btn = line.split(":", 1)[1]
            app_data["button"] = BUTTON_NAMES.get(btn, btn)

        else:
            app_data["status"] = line

    # reflect state in UI
    update_badge(state_badge, app_data["state"], state_color(app_data["state"]))
    update_value(level_value, app_data["level"], ACCENT)
    update_value(event_value, app_data["last_event"], event_color(app_data["last_event"]))
    update_value(button_value, app_data["button"], PINK)
    update_value(status_value, app_data["status"], TEXT)

    root.after(100, process_serial)


# UI building helpers
def make_card(parent, title, value_var_row):
    card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    title_label = tk.Label(
        card,
        text=title,
        font=("Helvetica", 12, "bold"),
        fg=MUTED,
        bg=CARD,
        anchor="w"
    )
    title_label.pack(anchor="w", padx=16, pady=(14, 6))

    value_label = tk.Label(
        card,
        text="-",
        font=("Helvetica", 22, "bold"),
        fg=TEXT,
        bg=CARD,
        anchor="w"
    )
    value_label.pack(anchor="w", padx=16, pady=(0, 16))

    card.grid(row=value_var_row[0], column=value_var_row[1], padx=10, pady=10, sticky="nsew")
    return value_label

# -------------------------
# Window
# -------------------------
root = tk.Tk()
root.title("Simon Game Dashboard")
root.geometry("980x620")
root.minsize(900, 560)
root.configure(bg=BG)

# -------------------------
# Header
# -------------------------
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=24, pady=(20, 10))

title = tk.Label(
    header,
    text="Simon Game Dashboard",
    font=("Helvetica", 28, "bold"),
    fg=TEXT,
    bg=BG
)
title.pack(side="left")

state_badge = tk.Label(
    header,
    text="Idle",
    font=("Helvetica", 12, "bold"),
    bg=ACCENT,
    fg="white",
    padx=14,
    pady=8
)
state_badge.pack(side="right")

subtitle = tk.Label(
    root,
    text="BME 393L Final Project | Julia & Sham ",
    font=("Helvetica", 12),
    fg=MUTED,
    bg=BG
)
subtitle.pack(anchor="w", padx=28, pady=(0, 12))

# -------------------------
# Main card grid
# -------------------------
content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=24, pady=8)

for i in range(2):
    content.columnconfigure(i, weight=1)
for i in range(2):
    content.rowconfigure(i, weight=1)

level_value = make_card(content, "Level", (0, 0))
event_value = make_card(content, "Last Event", (0, 1))
button_value = make_card(content, "Last Button", (1, 0))

# large status card
status_card = tk.Frame(content, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
status_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

status_title = tk.Label(
    status_card,
    text="Status",
    font=("Helvetica", 12, "bold"),
    fg=MUTED,
    bg=CARD_2,
    anchor="w"
)
status_title.pack(anchor="w", padx=16, pady=(14, 6))

status_value = tk.Label(
    status_card,
    text="Waiting for Arduino...",
    font=("Helvetica", 18, "bold"),
    fg=TEXT,
    bg=CARD_2,
    justify="left",
    wraplength=380,
    anchor="w"
)
status_value.pack(anchor="w", padx=16, pady=(0, 12))


# Footer bar
footer = tk.Frame(root, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
footer.pack(fill="x", padx=24, pady=(8, 20))

footer_left = tk.Frame(footer, bg=CARD)
footer_left.pack(side="left", padx=16, pady=14)

footer_label = tk.Label(
    footer_left,
    text="Current State",
    font=("Helvetica", 11, "bold"),
    fg=MUTED,
    bg=CARD
)
footer_label.pack(anchor="w")

footer_state = tk.Label(
    footer_left,
    text="Idle",
    font=("Helvetica", 16, "bold"),
    fg=TEXT,
    bg=CARD
)
footer_state.pack(anchor="w")

def sync_footer():
    footer_state.config(text=app_data["state"], fg=state_color(app_data["state"]))
    root.after(100, sync_footer)


# Start serial thread
threading.Thread(target=serial_reader, daemon=True).start()


# Start updates
process_serial()
sync_footer()

root.mainloop()