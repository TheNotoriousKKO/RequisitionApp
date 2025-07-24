import tkinter as tk
from tkinter import ttk, messagebox
import csv
import json
import os

GRENADE_LIMIT = 2
WEAPON_WEIGHT_LIMIT = 3
ARMOR_LIMIT = 1

CSV_FILE = "items.csv"
META_FILE = "metadata.json"

# Define constants for categories
ALL_CATEGORIES = ["Armor", "Grenade", "Utility", "Other", "Pistol", "Ranged", "Heavy Ranged", "Melee", "Heavy Melee"]
WEAPON_CATEGORIES = ["Pistol", "Ranged", "Melee", "Heavy Ranged", "Heavy Melee"]


def load_items():
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_metadata():
    if not os.path.exists(META_FILE):
        return {"username": "Player", "personal_items": []}
    with open(META_FILE, encoding='utf-8') as f:
        return json.load(f)


def save_metadata(meta):
    with open(META_FILE, "w", encoding='utf-8') as f:
        json.dump(meta, f, indent=2)


class RequisitionApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Requisition Planner")

        self.items = load_items()
        self.meta = load_metadata()
        self.username = self.meta.get("username", "Player")

        self.sort_column = None
        self.sort_reverse = False

        self.items.extend(self.meta.get("personal_items", []))
        self.cart = []
        self.build_ui()

        self.sort_column = None
        self.sort_reverse = False

    def build_ui(self):
        # Dark theme styling
        self.root.configure(bg="#121212")
        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background="#121212", foreground="#00ff88", fieldbackground="#121212", font=("Courier", 10))
        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="#00ff88",
                        fieldbackground="#1e1e1e",
                        bordercolor="#121212",
                        borderwidth=0,
                        rowheight=24,
                        font=("Courier", 10))
        style.configure("Treeview.Heading",
                        background="#333333",
                        foreground="#00ff88",
                        relief="flat",
                        font=("Courier", 10, "bold"))
        style.map("Treeview",
                  background=[('selected', '#00ff88')],
                  foreground=[('selected', '#000000')])

        style.configure("TButton", background="#1e1e1e", foreground="#00ff88", font=("Courier", 10))
        style.map("TButton", background=[("active", "#00ff88")], foreground=[("active", "#000000")])

        self.tree = ttk.Treeview(self.root, columns=("Name", "Category", "Points"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))

        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for item in self.items:
            self.tree.insert("", "end", iid=item["Name"], values=(item["Name"], item["Category"], item["Points"]))

        self.tree.bind("<Double-1>", self.show_item_details)

        ttk.Button(self.root, text="Add Selected Item", command=self.add_selected_item).grid(row=1, column=0, sticky="ew", padx=10)
        ttk.Button(self.root, text="Add Personal Item", command=self.add_personal_item).grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.cart_listbox = tk.Listbox(self.root, width=50, bg="#1e1e1e", fg="#00ff88", selectbackground="#00ff88", selectforeground="#000000", font=("Courier", 10))
        self.cart_listbox.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Button(self.root, text="Remove Selected", command=self.remove_selected_cart_item).grid(row=2, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.status_label = ttk.Label(self.root, text="Total: 0 pts", font=("Courier", 10))
        self.status_label.grid(row=3, column=0, columnspan=2)

        ttk.Button(self.root, text="Export Loadout", command=self.export).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    def show_welcome(self):
        msg = f""">> SERVITOR-ACCESS VERIFIED
    >> WELCOME, {self.username.upper()}
    >> PREPARE FOR DEPLOYMENT"""
        top = tk.Toplevel(self.root)
        top.title("Deployment Protocol")
        top.configure(bg="#121212")
        top.geometry("350x150")
        label = tk.Label(top, text=msg, fg="#00ff88", bg="#121212", font=("Courier", 10), justify="left")
        label.pack(expand=True, fill="both", padx=20, pady=20)
        top.after(2000, top.destroy)  # Auto-close after 4s

    def add_selected_item(self):
        selected = self.tree.focus()
        if not selected:
            return
        item = next((i for i in self.items if i["Name"] == selected), None)
        if not item:
            return

        if self.would_violate_category_limits(item):
            return

        self.cart.append(item)
        self.cart_listbox.insert("end", f'{item["Name"]} ({item["Points"]} pts)')
        self.update_status()

    def remove_selected_cart_item(self):
        idx = self.cart_listbox.curselection()
        if not idx:
            return
        del self.cart[idx[0]]
        self.cart_listbox.delete(idx)
        self.update_status()

    def update_status(self):
        total = sum(int(i["Points"]) for i in self.cart)
        grenade_count = sum(1 for i in self.cart if i["Category"] == "Grenade")
        weapon_weight = sum(
        2 if i["Category"] in ["Heavy Ranged", "Heavy Melee"] else 1
        for i in self.cart
        if i["Category"] in WEAPON_CATEGORIES
        )

        armor_count = sum(1 for i in self.cart if i["Category"] == "Armor")

        self.status_label.config(
            text=f"Total: {total} pts | Grenades: {grenade_count}/3 | Weapons: {weapon_weight}/3 | Armor: {armor_count}/1"
        )


        

    def would_violate_category_limits(self, item):
        cat = item["Category"]

        if cat == "Grenade":
            grenade_count = sum(1 for i in self.cart if i["Category"] == "Grenade")
            if grenade_count >= GRENADE_LIMIT:
                messagebox.showwarning("Grenade Limit", "Maximum 3 grenade items allowed.")
                return True

        if cat in WEAPON_CATEGORIES:
            current_weight = sum(
                2 if i["Category"] in ["Heavy Ranged", "Heavy Melee"] else 1
                for i in self.cart
                if i["Category"] in WEAPON_CATEGORIES
            )
            new_weight = 2 if cat in ["Heavy Ranged", "Heavy Melee"] else 1
            if current_weight + new_weight > WEAPON_WEIGHT_LIMIT:
                messagebox.showwarning("Weapon Limit", "Exceeded weapon weight limit (max 3).")
                return True

        if cat == "Armor":
            armor_count = sum(1 for i in self.cart if i["Category"] == "Armor")
            if armor_count >= ARMOR_LIMIT:
                messagebox.showwarning("Armor Limit", "You may only equip one suit of armor.")
                return True

        return False

    def export(self):
        from collections import defaultdict

        total = sum(int(i["Points"]) for i in self.cart)

        weapon_weight = sum(
        2 if i["Category"] in ["Heavy Ranged", "Heavy Melee"] else 1
        for i in self.cart
        if i["Category"] in WEAPON_CATEGORIES
        )

        grenade_count = sum(1 for i in self.cart if i["Category"] == "Grenade")


        # Group items by category
        categorized = defaultdict(list)
        for item in self.cart:
            categorized[item["Category"]].append(item)

        # Define the desired category order
        category_order = ALL_CATEGORIES

        lines = [f"Requisition Loadout for {self.username}:\n"]

        for cat in category_order:
            if categorized[cat]:
                lines.append(f"\n== {cat.upper()} ==")
                for item in categorized[cat]:
                    lines.append(f"- {item['Name']} ({item['Points']} pts)")

        # Catch any unexpected/uncategorized items
        for cat in categorized:
            if cat not in category_order:
                lines.append(f"\n== {cat.upper()} ==")
                for item in categorized[cat]:
                    lines.append(f"- {item['Name']} ({item['Points']} pts)")

        lines.append(f"\nTotal: {total} pts")
        lines.append(f"Grenades Used: {grenade_count} / {GRENADE_LIMIT}")
        lines.append(f"Weapon Weight Used: {weapon_weight} / {WEAPON_WEIGHT_LIMIT}")
        lines.append("Praise the Emperor!")

        output = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        messagebox.showinfo("Exported", "Loadout copied to clipboard.")


    def show_item_details(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        item = next((i for i in self.items if i["Name"] == selected), None)
        if not item:
            return

        top = tk.Toplevel(self.root)
        top.title(item["Name"])
        top.geometry("400x300")
        top.configure(bg="#121212")

        label_opts = {"fg": "#00ff88", "bg": "#121212", "anchor": "w", "padx": 10, "pady": 5, "font": ("Courier", 10)}
        tk.Label(top, text=f"Name: {item['Name']}", **label_opts).pack(fill="x")
        tk.Label(top, text=f"Category: {item['Category']}", **label_opts).pack(fill="x")
        tk.Label(top, text=f"Points: {item['Points']}", **label_opts).pack(fill="x")
        tk.Label(top, text="Description:", **label_opts).pack(fill="x")

        desc = tk.Text(
            top,
            wrap="word",
            height=10,
            bg="#1e1e1e",
            fg="#00ff88",
            insertbackground="#00ff88",
            font=("Courier", 10)
        )
        desc.pack(fill="both", expand=True, padx=10, pady=5)
        desc.insert("1.0", item.get("Description", "No description provided."))
        desc.config(state="disabled")


    def add_personal_item(self):
        def submit():
            name = name_entry.get().strip()
            cat = category_var.get()
            points = points_entry.get().strip()
            desc = desc_entry.get().strip()

            if not name or not points.isdigit():
                messagebox.showerror("Invalid Input", "Please fill all fields correctly.")
                return

            new_item = {
                "Name": name,
                "Category": cat,
                "Points": int(points),
                "Description": desc
            }

            self.meta["personal_items"].append(new_item)
            save_metadata(self.meta)
            self.items.append(new_item)
            self.tree.insert("", "end", iid=name, values=(name, cat, points))
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Add Personal Item")
        top.configure(bg="#121212")  # Dark background

        label_opts = {"fg": "#00ff88", "bg": "#121212", "font": ("Courier", 10), "anchor": "w", "padx": 10, "pady": 5}
        entry_opts = {"bg": "#1e1e1e", "fg": "#00ff88", "insertbackground": "#00ff88", "font": ("Courier", 10)}

        tk.Label(top, text="Name", **label_opts).grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(top, **entry_opts)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(top, text="Category", **label_opts).grid(row=1, column=0, sticky="w")
        category_var = tk.StringVar(value="Utility")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TCombobox",
            fieldbackground="#1e1e1e",
            background="#1e1e1e",
            foreground="#00ff88",
            selectforeground="#000000",
            selectbackground="#00ff88",
            bordercolor="#121212",
            lightcolor="#1e1e1e",
            darkcolor="#1e1e1e",
            arrowcolor="#00ff88"
        )


        category_menu = ttk.Combobox(
            top,
            textvariable=category_var,
            values=ALL_CATEGORIES,
            font=("Courier", 10),
            style="Dark.TCombobox"
        )
        category_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(top, text="Points", **label_opts).grid(row=2, column=0, sticky="w")
        points_entry = tk.Entry(top, **entry_opts)
        points_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(top, text="Description", **label_opts).grid(row=3, column=0, sticky="w")
        desc_entry = tk.Entry(top, **entry_opts)
        desc_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(top, text="Cancel", command=top.destroy, style="TButton").grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(top, text="Add Item", command=submit, style="TButton").grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        top.grid_columnconfigure(1, weight=1)

    def sort_by_column(self, col):
        self.sort_reverse = not self.sort_reverse if self.sort_column == col else False
        self.sort_column = col

        # sort self.items (does not affect cart or metadata)
        def sort_key(item):
            val = item[col]
            if col == "Points":
                try:
                    return int(val)
                except ValueError:
                    return float("inf")  # fallback for weird input
            else:
                return str(val).lower()


        self.items.sort(key=sort_key, reverse=self.sort_reverse)

        # Rebuild the treeview
        self.tree.delete(*self.tree.get_children())
        for item in self.items:
            self.tree.insert("", "end", iid=item["Name"], values=(item["Name"], item["Category"], item["Points"]))


def launch_main_app():
    root.deiconify()
    RequisitionApp(root)
    
def prompt_for_username_initial():
    def submit():
        name = entry.get().strip()
        if not name:
            messagebox.showerror("Invalid", "Please enter a valid name.")
            return
        meta["username"] = name
        save_metadata(meta)
        top.destroy()

    top = tk.Tk()
    top.title("BROTHER UNRECOGNIZED")
    top.configure(bg="#121212")
    top.geometry("350x150")

    label = tk.Label(top, text="IDENTIFY YOURSELF:", bg="#121212", fg="#00ff88", font=("Courier", 10))
    label.pack(pady=(20, 5))

    entry = tk.Entry(top, bg="#1e1e1e", fg="#00ff88", insertbackground="#00ff88", font=("Courier", 10))
    entry.pack(padx=20, pady=5)
    entry.focus()

    style = ttk.Style(top)
    style.theme_use("default")
    style.configure("TButton", background="#1e1e1e", foreground="#00ff88", font=("Courier", 10))
    style.map("TButton",
            background=[("active", "#00ff88")],
            foreground=[("active", "#000000")])


    button = ttk.Button(top, text="Confirm", command=submit)
    button.configure(style="TButton")
    button.pack(pady=10)

    top.mainloop()

def on_close():
    root.quit()
    root.destroy()

if __name__ == "__main__":
    if not os.path.exists(META_FILE):
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": "", "personal_items": []}, f, indent=2)

    meta = load_metadata()
    if not meta.get("username"):
        prompt_for_username_initial()
        meta = load_metadata()  # reload after possible save

    username = meta.get("username", "Player").upper()

    root = tk.Tk()
    root.withdraw()

    welcome = tk.Toplevel()
    welcome.title("Deployment Protocol")
    welcome.configure(bg="#121212")
    welcome.geometry("350x150")

    msg = f""">> SERVITOR-ACCESS VERIFIED
>> WELCOME, BROTHER {username}
>> PREPARE FOR DEPLOYMENT"""

    tk.Label(welcome, text=msg, fg="#00ff88", bg="#121212", font=("Courier", 10), justify="left").pack(expand=True, fill="both", padx=20, pady=20)

    welcome.after(2000, lambda: (welcome.destroy(), launch_main_app()))

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
