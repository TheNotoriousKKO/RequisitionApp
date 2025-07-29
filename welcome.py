import tkinter as tk

def show_welcome_screen(username, on_finish):
    root = tk.Tk()
    root.withdraw()
    welcome = tk.Toplevel()
    welcome.title("Deployment Protocol")
    welcome.configure(bg="#121212")
    welcome.geometry("350x150")

    msg = f""">> SERVITOR-ACCESS VERIFIED
>> WELCOME, BROTHER {username.upper()}
>> PREPARE FOR DEPLOYMENT"""

    tk.Label(
        welcome,
        text=msg,
        fg="#00ff88",
        bg="#121212",
        font=("Courier", 10),
        justify="left"
    ).pack(expand=True, fill="both", padx=20, pady=20)

    def close_and_continue():
        welcome.destroy()
        root.destroy()
        on_finish()

    welcome.after(2000, close_and_continue)
    root.mainloop()
