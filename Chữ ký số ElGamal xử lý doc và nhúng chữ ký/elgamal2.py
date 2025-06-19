import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import hashlib
import fitz  # PyMuPDF
import os
import random
import sympy
from sympy import isprime

# ===== ElGamal Functions =====
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def generate_large_prime(bits=64):
    while True:
        p = random.getrandbits(bits)
        if isprime(p): return p

def generate_keys():
    # Tạo khóa ElGamal
    p = generate_large_prime(32)     # Số nguyên tố lớn
    g = random.randint(2, p-2)        # Cơ sở
    x = random.randint(1, p-2)        # Private key
    y = pow(g, x, p)                  # Public key
    return (p, g, y), (x, p)               # public_key, private_key

def elgamal_encrypt(message: str, public_key):
    p, g, y = public_key
    m = int(hashlib.sha256(message.encode()).hexdigest(), 16) % p  # mã hóa hash dạng số
    k = random.randint(1, p-2)
    c1 = pow(g, k, p)
    c2 = (m * pow(y, k, p)) % p
    return (c1, c2)

def elgamal_decrypt(ciphertext, private_key):
    c1, c2 = ciphertext
    x,p = private_key
    if p is None:
        raise ValueError("Cần truyền `p` để giải mã ElGamal.")
    s = pow(c1, x, p)
    s_inv = pow(s, -1, p)
    m = (c2 * s_inv) % p
    # Chuyển ngược về bytes (để so sánh)
    return m

# ===== Digital Signature App =====
class DigitalSignatureApp:
    def __init__(self, root):
        self.root = root
        self.signature_list = []
        self.signature_image = None
        self.signature_preview = None
        self.signature_data = {}
        self.public_key, self.private_key = generate_keys()
        self.last_signature = None
        self.loaded_path = None
        self.signature_position = None
        self.ready_to_sign = False

        self.root.title("ElGamal Digital Signature App")
        self.root.geometry("1000x800")

        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=19)
        self.root.columnconfigure(0, weight=1)

        self.content_text = tk.Text(root, height=3)
        self.content_text.grid(row=1, column=0, sticky="nsew")

        # Cuộn được vùng canvas hiển thị PDF
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.grid(row=2, column=0, sticky="nsew")

        self.canvas_scroll = tk.Scrollbar(self.canvas_frame, orient="vertical")
        self.canvas_scroll.pack(side="right", fill="y")

        self.image_canvas = tk.Canvas(self.canvas_frame, bg="white", yscrollcommand=self.canvas_scroll.set)
        self.image_canvas.pack(side="left", fill="both", expand=True)

        self.canvas_scroll.config(command=self.image_canvas.yview)

        self.image_canvas.bind("<Motion>", self.track_signature)
        self.image_canvas.bind("<Button-1>", self.confirm_position)

        # Cuộn canvas bằng con lăn chuột
        self.image_canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows, macOS

        self.init_buttons()

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.image_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.image_canvas.yview_scroll(1, "units")
        
        self.update_current_page_index()

    def init_buttons(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=0, column=0, sticky="ew")
        actions = [
            ("Tạo chữ ký", self.open_signature_dialog),
            ("Chọn file PDF", self.load_pdf),
            ("Ký số", self.enable_signature_drag),
            ("Mã hóa & ký nội dung", self.sign_document),
            ("Xác minh chữ ký", self.verify_signature),
            ("Lưu tài liệu", self.save_signed_pdf),
        ]
        for text, command in actions:
            ttk.Button(btn_frame, text=text, command=command).pack(side="left", padx=5, pady=5)

    def open_signature_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Thông tin chữ ký")
        dialog.grab_set()

        frame = ttk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        labels = ["Tên chữ ký", "Họ tên người ký", "Chiều rộng ảnh", "Chiều cao ảnh"]
        entries = []
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label + ":").grid(row=i, column=0, sticky="e")
            entry = ttk.Entry(frame)
            entry.grid(row=i, column=1)
            entries.append(entry)

        signature_preview_canvas = tk.Canvas(frame, width=200, height=100, bg="lightgray")
        signature_preview_canvas.grid(row=0, column=2, rowspan=4, padx=10)

        def select_image():
            filepath = filedialog.askopenfilename(title="Chọn hình ảnh chữ ký")
            if not filepath:
                return
            try:
                img_raw = Image.open(filepath)
                img = img_raw.resize((200, 100))
                self.signature_image = ImageTk.PhotoImage(img)
                self.signature_preview = img_raw
                self.selected_image_path = filepath
                signature_preview_canvas.create_image(100, 50, image=self.signature_image)
            except Exception as e:
                messagebox.showerror("Lỗi ảnh", f"Không thể mở ảnh: {str(e)}")

        ttk.Button(frame, text="Chọn hình ảnh chữ ký", command=select_image).grid(row=4, column=2, pady=5)

        def on_submit():
            try:
                name, signer, width, height = (e.get() for e in entries)
                width, height = int(width), int(height)
                if not self.signature_image:
                    raise ValueError("Chưa chọn hình ảnh chữ ký")
                signature = {
                    'name': name, 'signer': signer, 'width': width, 'height': height,
                    'img_path': self.selected_image_path
                }
                self.signature_list.append(signature)
                self.signature_data = signature
                messagebox.showinfo("Thành công", "Đã thêm chữ ký!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

        ttk.Button(frame, text="Thêm chữ ký số", command=on_submit).grid(row=5, column=0, columnspan=3, pady=10)

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        self.page_positions = []

        if not path:
            return
        try:
            self.image_canvas.delete("all")
            doc = fitz.open(path)
            self.loaded_path = path
            self.loaded_doc = doc

            self.pdf_images = []
            y_position = 0

            for page in doc:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                photo = ImageTk.PhotoImage(img)
                self.pdf_images.append(photo)

                self.image_canvas.create_image(0, y_position, anchor="nw", image=photo)
                self.page_positions.append((y_position, pix.height))
                y_position += pix.height + 20  # Khoảng cách giữa các trang

            self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
        except Exception as e:
            messagebox.showerror("Lỗi tải PDF", str(e))

    def update_current_page_index(self):
        # Lấy tọa độ y hiện tại đang xem của canvas
        y_view = self.image_canvas.canvasy(0)

        # Duyệt qua các trang để tìm trang đầu tiên trong vùng hiển thị
        for idx, (start_y, height) in enumerate(self.page_positions):
            end_y = start_y + height
            if start_y <= y_view < end_y:
                self.current_page_index = idx
                return

        # Nếu không khớp (cuộn quá xa), mặc định là trang cuối
        self.current_page_index = len(self.page_positions) - 1

    def enable_signature_drag(self):
        if not self.signature_image:
            messagebox.showwarning("Cảnh báo", "Chưa có ảnh chữ ký!")
            return
        self.ready_to_sign = True
        self.image_canvas.delete("sig")
        messagebox.showinfo("Chế độ Ký số", "Di chuyển chuột và nhấp trái để đặt chữ ký số.")

    def track_signature(self, event):
        if self.ready_to_sign and self.signature_image:
            self.image_canvas.delete("sig")
            canvas_x = self.image_canvas.canvasx(event.x)
            canvas_y = self.image_canvas.canvasy(event.y)
            self.image_canvas.create_image(canvas_x, canvas_y, image=self.signature_image, tags="sig")

    def confirm_position(self, event):
        if self.ready_to_sign and self.signature_image:
            canvas_x = self.image_canvas.canvasx(event.x)
            canvas_y = self.image_canvas.canvasy(event.y)
            self.signature_position = (canvas_x, canvas_y)
            self.image_canvas.create_image(canvas_x, canvas_y, image=self.signature_image)
            self.image_canvas.delete("sig")
            self.ready_to_sign = False  # Chỉ cho phép 1 lần
            self.embed_signature_image_to_pdf(event.x, event.y)
            messagebox.showinfo("Đã gắn", "Ảnh chữ ký đã gắn vào vị trí đã chọn.")

    def embed_signature_image_to_pdf(self, x, y):
        if not self.signature_data or not self.loaded_path:
            return
        try:
            doc = fitz.open(self.loaded_path)

            page_index = max(0, min(self.current_page_index, len(doc) - 1))
            page = doc[page_index]

            zoom = 2  # hoặc scale từ pix.width/height và page.rect
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            ratio_x = page.rect.width / pix.width
            ratio_y = page.rect.height / pix.height

            real_x = x * ratio_x
            real_y = y * ratio_y

            img_rect = fitz.Rect(real_x, real_y,
                             real_x + self.signature_data['width'],
                             real_y + self.signature_data['height'])

            page.insert_image(img_rect, filename=self.signature_data['img_path'])
            temp_path = "signed_temp.pdf"
            doc.save(temp_path)
            self.loaded_path = temp_path
        except Exception as e:
            messagebox.showerror("Lỗi nhúng ảnh", f"Không thể nhúng ảnh: {e}")

    def sign_document(self):
        if not self.loaded_path or not self.signature_data:
            messagebox.showwarning("Thiếu thông tin", "Chưa chọn tài liệu hoặc chưa có chữ ký.")
            return

        try:
            # 1. Đọc lại ảnh chữ ký từ file ảnh đã chèn
            with open(self.signature_data['img_path'], "rb") as f:
                image_bytes = f.read()

            # 2. Băm ảnh
            hash_value = hashlib.sha256(image_bytes).hexdigest()

            # 3. Mã hóa giá trị băm bằng ElGamal
            public_key = self.public_key  # (p, g, y)
            signature = elgamal_encrypt(hash_value, public_key)

            # 4. Ghi chữ ký số vào file (tùy chọn: ghi vào metadata hoặc lưu riêng)
            self.signature_data['encrypted_hash'] = signature

            # 5. Hiển thị
            messagebox.showinfo("Đã ký số", f"Giá trị băm:\n{hash_value}\n\nChữ ký ElGamal:\n{signature}")

        except Exception as e:
            messagebox.showerror("Lỗi khi ký", str(e))

    def verify_signature(self):
        if not self.signature_data or 'encrypted_hash' not in self.signature_data:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có chữ ký số để xác minh.")
            return

        try:
            # 1. Đọc lại ảnh chữ ký từ file ảnh
            with open(self.signature_data['img_path'], "rb") as f:
                image_bytes = f.read()

            # 2. Băm lại ảnh
            _, p = self.private_key
            hash_value = hashlib.sha256(image_bytes).hexdigest()
            original_hash = int(hashlib.sha256(hash_value.encode()).hexdigest(), 16) % p

            # 3. Giải mã chữ ký đã lưu bằng khóa bí mật
            private_key = self.private_key  # (p, x)
            decrypted_hash = elgamal_decrypt(self.signature_data['encrypted_hash'], private_key)

            # 4. So sánh
            if decrypted_hash == original_hash:
                messagebox.showinfo("Xác minh thành công", "Chữ ký hợp lệ. Dữ liệu không bị thay đổi.")
            else:
                messagebox.showerror("Xác minh thất bại", "Chữ ký không hợp lệ hoặc dữ liệu đã bị thay đổi.")

        except Exception as e:
            messagebox.showerror("Lỗi khi xác minh", str(e))

    def save_signed_pdf(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not save_path:
            return
        try:
            doc = fitz.open(self.loaded_path)
            doc.save(save_path)
            messagebox.showinfo("Lưu thành công", f"Đã lưu tại:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

# === Main ===
if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalSignatureApp(root)
    root.mainloop()