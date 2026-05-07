import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from config import HOST, PORT


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LocalCrypt — Encrypted Chat")
        self.root.geometry("900x600")
        self.sock = None
        self.running = False
        self.setup_login_screen()

    # ---------------- LOGIN UI ----------------
    def setup_login_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.configure(bg="#0f0f0f")

        container = tk.Frame(self.root, bg="#0f0f0f")
        container.pack(expand=True)

        box = tk.Frame(container, bg="#1a1a1a", padx=30, pady=30)
        box.pack()

        tk.Label(box, text="Localcrypt",
                 font=("Segoe UI", 22, "bold"),
                 fg="#00ff88", bg="#1a1a1a").pack(pady=(0, 5))

        tk.Label(box, text="secure chat",
                 font=("Segoe UI", 10),
                 fg="#777", bg="#1a1a1a").pack(pady=(0, 20))

        tk.Label(box, text="Username", fg="#aaa", bg="#1a1a1a").pack(anchor="w")
        self.username_entry = tk.Entry(box, bg="#2a2a2a", fg="white",
                                       insertbackground="white", relief="flat", width=30)
        self.username_entry.pack(pady=(5, 15), ipady=6)

        tk.Label(box, text="Password", fg="#aaa", bg="#1a1a1a").pack(anchor="w")
        self.password_entry = tk.Entry(box, show="*", bg="#2a2a2a", fg="white",
                                       insertbackground="white", relief="flat", width=30)
        self.password_entry.pack(pady=(5, 15), ipady=6)

        tk.Label(box, text="Room", fg="#aaa", bg="#1a1a1a").pack(anchor="w")
        self.room_entry = tk.Entry(box, bg="#2a2a2a", fg="white",
                                   insertbackground="white", relief="flat", width=30)
        self.room_entry.insert(0, "general")
        self.room_entry.pack(pady=(5, 20), ipady=6)

        btn_frame = tk.Frame(box, bg="#1a1a1a")
        btn_frame.pack()

        tk.Button(btn_frame, text="Login",
                  bg="#00ff88", fg="#0f0f0f",
                  relief="flat", padx=15, pady=6,
                  command=lambda: self.connect("2")).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Register",
                  bg="#333", fg="#00ff88",
                  relief="flat", padx=15, pady=6,
                  command=lambda: self.connect("1")).pack(side="left", padx=5)

    # ---------------- CONNECT ----------------
    def connect(self, mode):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        room = self.room_entry.get().strip()

        if not username or not password or not room:
            messagebox.showerror("Error", "All fields required")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.running = True

            def handle_server():
                buffer = ""
                state = "choice"

                while self.running:
                    try:
                        data = self.sock.recv(4096).decode()
                        if not data:
                            break

                        buffer += data

                        # -------- FLOW --------
                        if state == "choice" and "Choice" in buffer:
                            self.sock.send((mode + "\n").encode())
                            buffer = ""
                            state = "reg_user" if mode == "1" else "login_user"

                        elif state == "reg_user" and "Username" in buffer:
                            self.sock.send((username + "\n").encode())
                            buffer = ""
                            state = "reg_pass"

                        elif state == "reg_pass" and "Password" in buffer:
                            self.sock.send((password + "\n").encode())
                            buffer = ""
                            state = "reg_done"

                        elif state == "reg_done":
                            if "exists" in buffer:
                                messagebox.showerror("Error", "Username exists")
                                return
                            if "Registered" in buffer:
                                buffer = ""
                                state = "login_user"

                        elif state == "login_user" and "Username" in buffer:
                            self.sock.send((username + "\n").encode())
                            buffer = ""
                            state = "login_pass"

                        elif state == "login_pass" and "Password" in buffer:
                            self.sock.send((password + "\n").encode())
                            buffer = ""
                            state = "room"

                        elif state == "room" and "Room" in buffer:
                            self.sock.send((room + "\n").encode())
                            buffer = ""
                            state = "chat"

                        # -------- ENTER CHAT --------
                        elif state == "chat":
                            if "Invalid" in buffer:
                                messagebox.showerror("Error", "Invalid credentials")
                                return

                            if "Connected" in buffer or "Welcome" in buffer or "joined" in buffer:
                                self.root.after(0, lambda: self.setup_chat_screen(username, room))
                                self.root.after(0, lambda b=buffer: self.append_message(b))
                                buffer = ""
                                state = "messages"

                        # -------- RECEIVE MESSAGES --------
                        elif state == "messages":
                            if buffer.strip():
                                self.root.after(0, lambda b=buffer: self.append_message(b))
                                buffer = ""

                    except:
                        break

            threading.Thread(target=handle_server, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    # ---------------- CHAT UI ----------------
    def setup_chat_screen(self, username, room):
        self.username = username

        for w in self.root.winfo_children():
            w.destroy()

        self.root.configure(bg="#121212")

        top = tk.Frame(self.root, bg="#1e1e1e", height=40)
        top.pack(fill="x")

        tk.Label(top, text=f"{room}", fg="#00ff88", bg="#1e1e1e",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=10)

        tk.Label(top, text=username, fg="#aaa", bg="#1e1e1e").pack(side="right", padx=10)

        self.chat_area = scrolledtext.ScrolledText(
            self.root,
            bg="#121212",
            fg="#e4e6eb",
            font=("Segoe UI", 11),
            insertbackground="white",
            relief="flat",
            state="disabled",
            padx=10,
            pady=10
        )
        self.chat_area.pack(fill="both", expand=True)

        self.chat_area.tag_config("own", foreground="#4caf50")
        self.chat_area.tag_config("other", foreground="#e4e6eb")
        self.chat_area.tag_config("system", foreground="#888")

        bottom = tk.Frame(self.root, bg="#1e1e1e")
        bottom.pack(fill="x")

        self.msg_entry = tk.Entry(
            bottom,
            bg="#2a2a2a",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.msg_entry.bind("<Return>", self.send_message)

        tk.Button(bottom, text="Send",
                  bg="#00ff88", fg="#0f0f0f",
                  relief="flat", padx=10,
                  command=self.send_message).pack(side="right", padx=10)

    # ---------------- DISPLAY ----------------
    def append_message(self, text):
        self.chat_area.config(state="normal")

        for line in text.split("\n"):
            if not line.strip():
                continue

            if line.startswith(f"{self.username}:"):
                self.chat_area.insert("end", line + "\n", "own")

            elif line.startswith("Online:") or line.startswith("[+]") or line.startswith("[-]"):
                self.chat_area.insert("end", line + "\n", "system")

            else:
                self.chat_area.insert("end", line + "\n", "other")

        self.chat_area.config(state="disabled")
        self.chat_area.see("end")

    # ---------------- SEND ----------------
    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        if msg == "/quit":
            self.sock.send("/quit\n".encode())
            self.running = False
            self.root.after(0, self.setup_login_screen)
        else:
            try:
                self.sock.send(f"{msg}\n".encode())
            except:
                pass

        self.msg_entry.delete(0, "end")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()