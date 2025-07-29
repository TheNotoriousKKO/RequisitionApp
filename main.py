import tkinter as tk
import json, os, threading
from welcome import show_welcome_screen
from ui import RequisitionApp, prompt_for_username_initial, prompt_for_csv_url_initial, on_close
from utils import load_metadata, load_items, META_FILE


if __name__ == "__main__":
    # Ensure metadata exists
    if not os.path.exists(META_FILE):
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": "", "personal_items": []}, f, indent=2)

    meta = load_metadata()
    if not meta.get("username"):
        prompt_for_username_initial()
        meta = load_metadata()
    if not meta.get("csv_url"):
        prompt_for_csv_url_initial()
        meta = load_metadata()

    username = meta.get("username", "Player")

    # Flags to track completion
    data_ready = {"download": False, "timer": False}

    # Start background download immediately
    preloaded = {"items": None}

    def preload_data():
        preloaded["items"] = load_items()  # triggers the request and caching
        data_ready["download"] = True
        check_and_start()

    def check_and_start():
        if data_ready["download"] and data_ready["timer"]:
            launch_main_app()

    def start_timer():
        data_ready["timer"] = True
        check_and_start()

    def launch_main_app():
        app_root = tk.Tk()
        app = RequisitionApp(app_root, preloaded_items=preloaded["items"])
        app_root.protocol("WM_DELETE_WINDOW", lambda: on_close(app_root))
        app_root.mainloop()

    threading.Thread(target=preload_data, daemon=True).start()
    show_welcome_screen(username, start_timer)