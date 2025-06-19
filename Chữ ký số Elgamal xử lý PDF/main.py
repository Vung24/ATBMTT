import tkinter as tk
from tkinter import ttk
from elgamal import generate_keys_elgamal
from ui_signature_gen import SignatureGeneration
from ui_signature_verify import SignatureVerification


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nhóm 14 ATBMTT")
        self.geometry("850x860")
        self.private_key, self.public_key = generate_keys_elgamal()
        self.tab_control = ttk.Notebook(self)

        self.tab_generation = SignatureGeneration(self.tab_control, self.private_key)
        self.tab_control.add(self.tab_generation, text="Ký văn bản")

        self.tab_verification = SignatureVerification(self.tab_control, self.public_key)
        self.tab_control.add(self.tab_verification, text="Kiểm Tra Chữ Ký")

        self.tab_control.pack(expand=1, fill="both")


if __name__ == "__main__":
    app = App()
    app.mainloop()