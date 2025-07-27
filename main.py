import tkinter as tk
import json
import os
from ui import RequisitionApp, prompt_for_username_initial, on_close
from utils import load_metadata, save_metadata, META_FILE


def launch_main_app():
    app_root = tk.Tk()
    app = RequisitionApp(app_root)
    app_root.protocol("WM_DELETE_WINDOW", lambda: on_close(app_root))
    app_root.mainloop()


if __name__ == "__main__":
    # Ensure metadata exists
    if not os.path.exists(META_FILE):
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": "", "personal_items": []}, f, indent=2)

    meta = load_metadata()
    if not meta.get("username"):
        prompt_for_username_initial()
        meta = load_metadata()

    username = meta.get("username", "Player").upper()

    # Initial welcome screen
    root = tk.Tk()
    root.withdraw()
    welcome = tk.Toplevel()
    welcome.title("Deployment Protocol")
    welcome.configure(bg="#121212")
    welcome.geometry("350x150")

    msg = f""">> SERVITOR-ACCESS VERIFIED
>> WELCOME, BROTHER {username}
>> PREPARE FOR DEPLOYMENT"""

    tk.Label(welcome, text=msg, fg="#00ff88", bg="#121212", font=("Courier", 10), justify="left")\
        .pack(expand=True, fill="both", padx=20, pady=20)

    # After delay, close welcome and launch main UI
    def start_app():
        welcome.destroy()
        root.destroy()
        launch_main_app()

    welcome.after(2000, start_app)
    root.mainloop()
