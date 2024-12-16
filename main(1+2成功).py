import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# 从相关模块导入类
from User_Registration import UserRegistration  # 确保导入正确
from modules.RestaurantDatabase import RestaurantDatabase  # 确保路径正确
from RestaurantBrowsing import RestaurantBrowsing  # 导入 RestaurantBrowsing 类
from RestaurantFiltering import RestaurantFilter  # 导入 RestaurantFilter 类

# 用户数据存储相关函数
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# 语言文件加载
def load_translations(language="en"):
    with open("languages.json", "r", encoding="utf-8") as f:
        translations = json.load(f)
    return translations.get(language, translations["en"])

class Application(tk.Tk):
    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        self.translations = load_translations(language)
        self.title(self.translations["welcome"])
        self.geometry("800x500")

        # 加载用户数据
        self.user_data = load_users()

        # 初始化相关类
        self.registration = UserRegistration()  # 注册类
        self.registration.users = self.user_data  # 加载已存在的用户数据

        self.database = RestaurantDatabase()  # 初始化餐馆数据库类
        self.browsing = RestaurantBrowsing(self.database)  # 初始化餐馆浏览

        # Initially no user logged in
        self.logged_in_email = None

        # Create initial frame
        self.current_frame = None
        self.show_startup_frame()

    def show_startup_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StartupFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = RegisterFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def login_user(self, email):
        self.logged_in_email = email
        # After login, show main app frame
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, email)
        self.current_frame.pack(fill="both", expand=True)


class StartupFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text=master.translations["welcome"], font=("Arial", 16)).pack(pady=30)
        tk.Button(self, text=master.translations["register"], command=self.go_to_register, width=20).pack(pady=10)
        tk.Button(self, text=master.translations["login"], command=self.go_to_login, width=20).pack(pady=10)

    def go_to_register(self):
        self.master.show_register_frame()

    def go_to_login(self):
        self.master.show_login_frame()


class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text=master.translations["register_new_user"], font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry(master.translations["email"])
        self.pass_entry = self.create_entry(master.translations["password"], show="*")
        self.conf_pass_entry = self.create_entry(master.translations["confirm_password"], show="*")

        tk.Button(self, text=master.translations["register"], command=self.register_user).pack(pady=10)
        tk.Button(self, text=master.translations["back"], command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def register_user(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.conf_pass_entry.get()

        result = self.master.registration.register(email, password, confirm_password)
        if result["success"]:
            # Save the updated users to file
            save_users(self.master.registration.users)
            messagebox.showinfo(self.master.translations["success"], "Registration successful! Please log in.")
            self.master.show_login_frame()
        else:
            messagebox.showerror(self.master.translations["error"], result["error"])

    def go_back(self):
        self.master.show_startup_frame()


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text=master.translations["user_login"], font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry(master.translations["email"])
        self.pass_entry = self.create_entry(master.translations["password"], show="*")

        tk.Button(self, text=master.translations["login"], command=self.login).pack(pady=10)
        tk.Button(self, text=master.translations["back"], command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        # Validate login
        # For simplicity, just check if user exists and password matches
        users = self.master.registration.users
        if email in users and users[email]["password"] == password:
            self.master.login_user(email)
        else:
            messagebox.showerror(self.master.translations["error"], "Invalid email or password")

    def go_back(self):
        self.master.show_startup_frame()


class MainAppFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        self.user_email = user_email
        self.language_var = tk.StringVar(value=master.language)
        lang_menu = ttk.Combobox(self, textvariable=self.language_var, values=["en", "zh"])
        lang_menu.bind("<<ComboboxSelected>>", self.change_language)
        lang_menu.pack(pady=10)

        # Welcome message
        tk.Label(self, text=f"{master.translations['welcome']}, {user_email}", font=("Arial", 14)).pack(pady=10)

    def change_language(self, event):
        new_language = self.language_var.get()
        self.master.language = new_language
        self.master.translations = load_translations(new_language)
        self.master.show_main_app_frame()

if __name__ == "__main__":
    app = Application(language="en")  # 默认使用英文，可以修改为 "zh" 来使用中文
    app.mainloop()
