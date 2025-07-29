import tkinter as tk
from tkinter import ttk, messagebox
from utils import load_items, load_metadata, save_metadata, ALL_CATEGORIES, WEAPON_CATEGORIES

GRENADE_LIMIT = 2
WEAPON_WEIGHT_LIMIT = 3
ARMOR_LIMIT = 1


class RequisitionApp:
    def __init__(self, root, preloaded_items=None):
        self.root = root
        self.root.title("Requisition Planner")
        self.items = preloaded_items if preloaded_items is not None else load_items()
        self.meta = load_metadata()
        self.username = self.meta.get("username", "Player")
        self.items.extend(self.meta.get("personal_items", []))
        self.cart = []
        self.sort_column = None
        self.sort_reverse = False
        self.build_ui()

    def build_ui(self):
        self.root.configure(bg="#121212")
        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background="#121212", foreground="#00ff88", fieldbackground="#121212", font=("Courier", 10))
        style.configure("Treeview", background="#1e1e1e", foreground="#00ff88", fieldbackground="#1e1e1e",
                        bordercolor="#121212", borderwidth=0, rowheight=24, font=("Courier", 10))
        style.configure("Treeview.Heading", background="#333333", foreground="#00ff88",
                        relief="flat", font=("Courier", 10, "bold"))
        style.map("Treeview", background=[('selected', '#00ff88')], foreground=[('selected', '#000000')])
        style.configure("TButton", background="#1e1e1e", foreground="#00ff88", font=("Courier", 10))
        style.map("TButton", background=[("active", "#00ff88")], foreground=[("active", "#000000")])

        self.tree = ttk.Treeview(self.root, columns=("Name", "Category", "Points"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=120)
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        for item in self.items:
            self.tree.insert("", "end", iid=item["Name"], values=(item["Name"], item["Category"], item["Points"]))
        self.tree.bind("<Double-1>", self.show_item_details)

        ttk.Button(self.root, text="Add Selected Item", command=self.add_selected_item).grid(row=1, column=0, sticky="ew", padx=10)
        ttk.Button(self.root, text="Add Personal Item", command=self.add_personal_item).grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.cart_listbox = tk.Listbox(self.root, width=50, bg="#1e1e1e", fg="#00ff88",
                                       selectbackground="#00ff88", selectforeground="#000000", font=("Courier", 10))
        self.cart_listbox.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        ttk.Button(self.root, text="Remove Selected", command=self.remove_selected_cart_item).grid(row=2, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.status_label = ttk.Label(self.root, text="Total: 0 pts", font=("Courier", 10))
        self.status_label.grid(row=3, column=0, columnspan=2)

        ttk.Button(self.root, text="Export Loadout", command=self.export).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def add_selected_item(self):
        selected = self.tree.focus()
        if not selected:
            return
        item = next((i for i in self.items if i["Name"] == selected), None)
        if not item or self.would_violate_category_limits(item):
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
        weapon_weight = sum(2 if i["Category"] in ["Heavy Ranged", "Heavy Melee"] else 1
                            for i in self.cart if i["Category"] in WEAPON_CATEGORIES)
        armor_count = sum(1 for i in self.cart if i["Category"] == "Armor")
        self.status_label.config(text=f"Total: {total} pts | Grenades: {grenade_count}/2 | Weapons: {weapon_weight}/3 | Armor: {armor_count}/1")

    def would_violate_category_limits(self, item):
        cat = item["Category"]
        if cat == "Grenade":
            if sum(1 for i in self.cart if i["Category"] == "Grenade") >= GRENADE_LIMIT:
                messagebox.showwarning("Grenade Limit", "Maximum 2 grenade items allowed.")
                return True
        if cat in WEAPON_CATEGORIES:
            current_weight = sum(2 if i["Category"] in ["Heavy Ranged", "Heavy Melee"] else 1
                                 for i in self.cart if i["Category"] in WEAPON_CATEGORIES)
            if current_weight + (2 if cat in ["Heavy Ranged", "Heavy Melee"] else 1) > WEAPON_WEIGHT_LIMIT:
                messagebox.showwarning("Weapon Limit", "Exceeded weapon weight limit (max 3).")
                return True
        if cat == "Armor" and sum(1 for i in self.cart if i["Category"] == "Armor") >= ARMOR_LIMIT:
            messagebox.showwarning("Armor Limit", "You may only equip one suit of armor.")
            return True
        return False

    def export(self):
        from collections import defaultdict
        total = sum(int(i["Points"]) for i in self.cart)
        weapon_weight = sum(2 if i["Category"] in ["Heavy Ranged", "Heavy Melee"] else 1
                            for i in self.cart if i["Category"] in WEAPON_CATEGORIES)
        grenade_count = sum(1 for i in self.cart if i["Category"] == "Grenade")

        categorized = defaultdict(list)
        for item in self.cart:
            categorized[item["Category"]].append(item)

        lines = [f"Requisition Loadout for {self.username}:\n"]
        for cat in ALL_CATEGORIES:
            if categorized[cat]:
                lines.append(f"\n== {cat.upper()} ==")
                for item in categorized[cat]:
                    lines.append(f"- {item['Name']} ({item['Points']} pts)")
        for cat in categorized:
            if cat not in ALL_CATEGORIES:
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
        desc = tk.Text(top, wrap="word", height=10, bg="#1e1e1e", fg="#00ff88", insertbackground="#00ff88", font=("Courier", 10))
        desc.insert("1.0", item.get("Description", "No description provided."))
        desc.config(state="disabled")
        desc.pack(fill="both", expand=True, padx=10, pady=5)

    def add_personal_item(self):
        def submit():
            name = name_entry.get().strip()
            cat = category_var.get()
            points = points_entry.get().strip()
            desc = desc_entry.get().strip()
            if not name or not points.isdigit():
                messagebox.showerror("Invalid Input", "Please fill all fields correctly.")
                return
            new_item = {"Name": name, "Category": cat, "Points": int(points), "Description": desc}
            self.meta["personal_items"].append(new_item)
            save_metadata(self.meta)
            self.items.append(new_item)
            self.tree.insert("", "end", iid=name, values=(name, cat, points))
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Add Personal Item")
        top.configure(bg="#121212")
        label_opts = {"fg": "#00ff88", "bg": "#121212", "font": ("Courier", 10), "anchor": "w", "padx": 10, "pady": 5}
        entry_opts = {"bg": "#1e1e1e", "fg": "#00ff88", "insertbackground": "#00ff88", "font": ("Courier", 10)}

        tk.Label(top, text="Name", **label_opts).grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(top, **entry_opts)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(top, text="Category", **label_opts).grid(row=1, column=0, sticky="w")
        category_var = tk.StringVar(value="Utility")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TCombobox", fieldbackground="#1e1e1e", background="#1e1e1e", foreground="#00ff88",
                        selectforeground="#000000", selectbackground="#00ff88")
        category_menu = ttk.Combobox(top, textvariable=category_var, values=ALL_CATEGORIES, font=("Courier", 10), style="Dark.TCombobox")
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

        def sort_key(item):
            val = item[col]
            if col == "Points":
                try:
                    return int(val)
                except ValueError:
                    return float("inf")
            return str(val).lower()

        self.items.sort(key=sort_key, reverse=self.sort_reverse)
        self.tree.delete(*self.tree.get_children())
        for item in self.items:
            self.tree.insert("", "end", iid=item["Name"], values=(item["Name"], item["Category"], item["Points"]))


def prompt_for_username_initial():
    def submit():
        name = entry.get().strip()
        if not name:
            messagebox.showerror("Invalid", "Please enter a valid name.")
            return
        meta["username"] = name
        save_metadata(meta)
        top.destroy()

    meta = load_metadata()
    top = tk.Tk()
    top.title("BROTHER UNRECOGNIZED")
    top.configure(bg="#121212")
    top.geometry("350x150")

    tk.Label(top, text="IDENTIFY YOURSELF:", bg="#121212", fg="#00ff88", font=("Courier", 10)).pack(pady=(20, 5))
    entry = tk.Entry(top, bg="#1e1e1e", fg="#00ff88", insertbackground="#00ff88", font=("Courier", 10))
    entry.pack(padx=20, pady=5)
    entry.focus()

    style = ttk.Style(top)
    style.theme_use("default")
    style.configure("TButton", background="#1e1e1e", foreground="#00ff88", font=("Courier", 10))
    style.map("TButton", background=[("active", "#00ff88")], foreground=[("active", "#000000")])

    ttk.Button(top, text="Confirm", command=submit, style="TButton").pack(pady=10)
    top.mainloop()

def prompt_for_csv_url_initial():
    def submit():
        url = entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Invalid", "Please enter a valid URL.")
            return

        # ✅ Detect Google Drive "file/d/<id>/view" format and convert
        import re
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
        if match:
            file_id = match.group(1)
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

        meta["csv_url"] = url
        save_metadata(meta)
        top.destroy()


    meta = load_metadata()
    top = tk.Tk()
    top.title("CLOUD DATA MISSING")
    top.configure(bg="#121212")
    top.geometry("400x150")

    tk.Label(top, text="Provide Google Drive CSV Link:", bg="#121212", fg="#00ff88", font=("Courier", 10))\
        .pack(pady=(20, 5))
    entry = tk.Entry(top, bg="#1e1e1e", fg="#00ff88", insertbackground="#00ff88", font=("Courier", 10))
    entry.pack(padx=20, pady=5, fill="x")
    entry.focus()

    style = ttk.Style(top)
    style.theme_use("default")
    style.configure("TButton", background="#1e1e1e", foreground="#00ff88", font=("Courier", 10))
    style.map("TButton", background=[("active", "#00ff88")], foreground=[("active", "#000000")])

    ttk.Button(top, text="Confirm", command=submit, style="TButton").pack(pady=10)
    top.mainloop()

def on_close(root):
    root.quit()
    root.destroy()
