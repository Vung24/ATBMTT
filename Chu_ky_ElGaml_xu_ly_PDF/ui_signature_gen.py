import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from elgamal import sign_data_elgamal
from file_processing import extract_text_from_pdf, extract_text_from_docx, combine_file

class SignatureGeneration(tk.Frame):
    def __init__(self, parent, private_key):
        super().__init__(parent)
        self.private_key = private_key
        self.signature = None
        self.hash_function = tk.StringVar(value='SHA256')
        self.setup_ui()

    def setup_ui(self):
        self.configure(bg="#F1F1F1")

        tk.Label(self, text="KÝ VĂN BẢN", font=("Arial", 18, "bold"), bg="#F1F1F1", fg="#333333").pack(pady=20)

        tk.Button(self, text="Chọn File Văn Bản", command=self.choose_file, bg="#4CAF50", fg="white", font=("Arial", 14), relief="raised", width=25).pack(pady=10)

        fdndvb = tk.Frame(self, bg="#F1F1F1")
        fdndvb.pack()

        tk.Label(fdndvb, text="Nội dung văn bản:", bg="#F1F1F1", fg="#333333", font=("Arial", 14), anchor="w").pack(padx=0, fill=tk.X)
        self.text_entry = tk.Text(fdndvb, width=70, height=10, font=("Arial", 14), bg="#FFFFFF", fg="#333333", wrap=tk.WORD)
        self.text_entry.pack(pady=5)

        frchbam = tk.Frame(self, bg="#F1F1F1")
        frchbam.pack()

        fm = tk.Frame(frchbam, bg="#F1F1F1", width=500)
        fm.pack(fill=tk.X, pady=5)
        tk.Label(fm, text="Chữ ký:", bg="#F1F1F1", fg="#333333", font=("Arial", 14), anchor="w").pack(padx=(0, 470), fill=tk.X, side=tk.LEFT)
        tk.Label(fm, text="Chọn hàm băm:", bg="#F1F1F1", fg="#333333", font=("Arial", 14)).pack(padx=0, fill=tk.X, side=tk.LEFT)
        hash_options = ['SHA1', 'SHA256', 'SHA384', 'SHA512']
        ttk.Combobox(fm, textvariable=self.hash_function, values=hash_options, width=10).pack(pady=5, fill=tk.X, side=tk.LEFT)
        fm.pack(fill=tk.X)
        self.signature_text = tk.Text(frchbam, width=70, height=5, font=("Arial", 14), bg="#FFFFFF", fg="#333333", wrap=tk.WORD)
        self.signature_text.pack(pady=10)

        tk.Button(self, text="Tạo Chữ Ký", command=self.generate_signature, bg="#007BFF", fg="white", font=("Arial", 14), relief="raised", width=26).pack(pady=20)
        save_button_frame = tk.Frame(self, bg="#F1F1F1")
        save_button_frame.pack(pady=10)

        tk.Button(save_button_frame, text="Lưu File Văn Bản", command=self.save_combined_file, bg="#E0E0E0", fg="black", font=("Arial", 12), relief="raised", width=15).pack(side="left", padx=5)

        tk.Button(save_button_frame, text="Lưu File Chữ Ký", command=self.save_signature_file, bg="#E0E0E0", fg="black", font=("Arial", 12), relief="raised", width=15).pack(side="left", padx=5)

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Word Files", "*.docx"), ("Text Files", "*.txt")])
        if file_path.endswith(".pdf"):
            content = extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            content = extract_text_from_docx(file_path)
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            messagebox.showwarning("Cảnh Báo", "Định dạng file không được hỗ trợ!")
            return
        self.text_entry.delete("1.0", "end")
        self.text_entry.insert("1.0", content)

    def generate_signature(self):
        text_content = self.text_entry.get("1.0", "end").strip()
        if not text_content:
            messagebox.showwarning("Cảnh Báo", "Hãy nhập nội dung!")
            return
        hash_function = self.hash_function.get()
        self.signature = sign_data_elgamal(text_content, self.private_key, hash_function)
        self.signature_text.delete("1.0", "end")
        self.signature_text.insert("1.0", f"{self.signature[0]},{self.signature[1]}")

    def save_combined_file(self):
        text_content = self.text_entry.get("1.0", "end").strip()
        if not text_content or not self.signature:
            messagebox.showwarning("Cảnh Báo", "Chưa có nội dung hoặc chữ ký!")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not output_path:
            return
        combine_file(text_content, self.signature, output_path)
        messagebox.showinfo("Thành Công", f"File đã lưu tại {output_path}")

    def save_signature_file(self):
        if not self.signature:
            messagebox.showwarning("Cảnh Báo", "Chưa có chữ ký để lưu!")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not output_path:
            return
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"{self.signature[0]},{self.signature[1]}")
        messagebox.showinfo("Thành Công", f"Chữ ký đã được lưu tại {output_path}")