import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from elgamal import verify_signature_elgamal
from file_processing import split_combined_file


class SignatureVerification(tk.Frame):
    def __init__(self, parent, public_key):
        super().__init__(parent)
        self.public_key = public_key
        self.hash_function = tk.StringVar(value='SHA256')
        self.setup_ui()

    def setup_ui(self):
        self.configure(bg="#F1F1F1")

        tk.Label(self, text="KIỂM TRA CHỮ KÝ", font=("Arial", 18, "bold"), bg="#F1F1F1", fg="#333333").pack(pady=20)

        tk.Button(self, text="Chọn File Văn bản kiểm tra", command=self.choose_file, bg="#4CAF50", fg="white",
                  font=("Arial", 14), relief="raised", width=25).pack(pady=10)

        cknffr = tk.Frame(self, bg="#F1F1F1")
        cknffr.pack()
        tk.Label(cknffr, text="Nội dung văn bản:", bg="#F1F1F1", fg="#333333", font=("Arial", 14), anchor="w").pack(
            pady=5, fill=tk.X)
        self.text_entry = tk.Text(cknffr, width=70, height=10, font=("Arial", 14), bg="#FFFFFF", fg="#333333",
                                  wrap=tk.WORD)
        self.text_entry.pack(pady=10)

        new_frame = tk.Frame(self, bg="#F1F1F1")
        new_frame.pack()

        tk.Label(new_frame, text="Chữ ký:", bg="#F1F1F1", fg="#333333", font=("Arial", 14), anchor="w").pack(pady=5,
                                                                                                             fill=tk.X)
        self.signature_text = tk.Text(new_frame, width=70, height=5, font=("Arial", 14), bg="#FFFFFF", fg="#333333",
                                      wrap=tk.WORD)
        self.signature_text.pack(pady=10)

        frcuoi = tk.Frame(self, bg="#F1F1F1")
        frcuoi.pack()

        tk.Label(frcuoi, text="Chọn hàm băm:", bg="#F1F1F1", fg="#333333", font=("Arial", 14)).pack(pady=5,
                                                                                                    side=tk.LEFT)
        ttk.Combobox(frcuoi, textvariable=self.hash_function, values=['SHA1', 'SHA256', 'SHA384', 'SHA512'],
                     width=20).pack(pady=5, side=tk.LEFT)

        tk.Button(self, text="Kiểm Tra Chữ Ký", command=self.verify_signature, bg="#007BFF", fg="white",
                  font=("Arial", 14), relief="raised", width=25).pack(pady=20)

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                text_content, signature = split_combined_file(file_path)
                self.text_entry.delete("1.0", "end")
                self.text_entry.insert("1.0", text_content)
                self.signature_text.delete("1.0", "end")
                self.signature_text.insert("1.0", f"{signature[0]},{signature[1]}")
            except ValueError as e:
                messagebox.showwarning("Cảnh Báo", str(e))

    def verify_signature(self):
        text_content = self.text_entry.get("1.0", "end").strip()
        if not text_content:
            messagebox.showwarning("Cảnh Báo", "Hãy nhập nội dung!")
            return
        hash_function = self.hash_function.get()
        signature = self.signature_text.get("1.0", "end").strip().split(",")
        if len(signature) != 2:
            messagebox.showwarning("Cảnh Báo", "Chữ ký không hợp lệ!")
            return
        signature = (int(signature[0]), int(signature[1]))
        if verify_signature_elgamal(text_content, signature, self.public_key, hash_function):
            messagebox.showinfo("Thành Công", "Chữ ký khớp, văn bản không bị thay đổi!")
        else:
            messagebox.showerror("Lỗi", "Văn bản đã bị thay đổi!")