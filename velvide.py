import io
import cv2
import customtkinter as ctk
from PIL import Image, ImageOps
from tkinter import filedialog
from google import genai
from google.genai import types

API_KEY = "get api here"
client = genai.Client(api_key=API_KEY)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#1A1B2F"
COLOR_PANEL = "#262846"
COLOR_ACCENT = "#9D4EDD"
COLOR_ACCENT_HOVER = "#7B2CBF"
COLOR_TEXT = "#E0E1DD"
COLOR_ALERT = "#E63946"

class HaliMotifApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ametist - Halı Motifi Tanıma")
        self.geometry("900x600")
        self.configure(fg_color=COLOR_BG)

        self.cap = None
        self.is_camera_open = False
        self.current_pil_image = None

        self.setup_ui()

    def setup_ui(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        left_panel = ctk.CTkFrame(main_container, fg_color=COLOR_PANEL, corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.image_label = ctk.CTkLabel(left_panel, text="Görsel Seçin veya Kamera Açın", fg_color="#151625", corner_radius=8, text_color="#8D99AE")
        self.image_label.pack(fill="both", expand=True, padx=12, pady=12)

        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkButton(btn_frame, text="📁 Resim", command=self.load_image_file, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER).pack(side="left", expand=True, padx=3)
        self.btn_cam = ctk.CTkButton(btn_frame, text="📷 Kamera", command=self.toggle_camera, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.btn_cam.pack(side="left", expand=True, padx=3)
        ctk.CTkButton(btn_frame, text="⚡ Analiz", command=self.analyze_motif, fg_color="#5A189A", hover_color="#3C096C").pack(side="left", expand=True, padx=3)

        right_panel = ctk.CTkFrame(main_container, fg_color=COLOR_PANEL, corner_radius=12)
        right_panel.pack(side="right", fill="both", expand=True, padx=(8, 0))

        ctk.CTkLabel(right_panel, text="Sonuç", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT).pack(anchor="w", padx=12, pady=(12, 4))
        
        self.result_text = ctk.CTkTextbox(right_panel, fg_color="#151625", text_color=COLOR_TEXT, font=ctk.CTkFont(size=13), corner_radius=8, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.result_text.insert("1.0", "Hazır.")

    def load_image_file(self):
        if self.is_camera_open: self.stop_camera()
        path = filedialog.askopenfilename(filetypes=[("Tüm Görseller", "*.*")])
        if path:
            try:
                img = Image.open(path)
                img = ImageOps.exif_transpose(img)
                self.current_pil_image = img
                self.display_image(img)
            except Exception as e:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", f"Dosya okuma hatası: {str(e)}")

    def toggle_camera(self):
        if self.is_camera_open:
            self.stop_camera()
        else:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_camera_open = True
                self.btn_cam.configure(text="🛑 Durdur", fg_color=COLOR_ALERT)
                self.update_camera_frame()

    def update_camera_frame(self):
        if self.is_camera_open and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.current_pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                self.display_image(self.current_pil_image)
            self.after(30, self.update_camera_frame)

    def stop_camera(self):
        self.is_camera_open = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_cam.configure(text="📷 Kamera", fg_color=COLOR_ACCENT)

    def display_image(self, img):
        img_copy = img.copy()
        img_copy.thumbnail((400, 400))
        ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        self.image_label.configure(image=ctk_img, text="")

    def analyze_motif(self):
        if not self.current_pil_image:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "Görsel yok.")
            return

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "Analiz ediliyor...")
        self.update()

        try:
            # P, RGBA, LA gibi modları JPEG uyumlu RGB'ye çevirerek hatayı önler
            img_rgb = self.current_pil_image.convert('RGB')
            img_byte_arr = io.BytesIO()
            img_rgb.save(img_byte_arr, format='JPEG')
            
            prompt = "Görsel bir halı/kilim motifi değilse sadece 'REDDEDİLDİ' yaz. Motifse kısa ve net şekilde: 1. Adı, 2. Anlamı, 3. Yöresi formatında yaz."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg'), prompt]
            )

            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", response.text)
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Hata: {str(e)}")

if __name__ == "__main__":
    app = HaliMotifApp()
    app.mainloop()
