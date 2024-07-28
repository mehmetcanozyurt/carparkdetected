import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

def detect_parking_spaces(image_path, lower_hsv, upper_hsv):
    # Dosya yolunun mevcut olup olmadığını kontrol edin
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return [], None
    
    # Görüntüyü yükleyin
    image = cv2.imread(image_path)
    
    # Görüntünün başarıyla yüklenip yüklenmediğini kontrol edin
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return [], None
    
    # Görüntüyü yeniden boyutlandırın (isteğe bağlı)
    image = cv2.resize(image, (800, 600))
    
    # Görüntüyü HSV renk uzayına dönüştürün
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Belirtilen renk aralığında maske oluşturun
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
    
    # Kenar tespiti ile konturları bulun
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    parking_spaces = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        parking_spaces.append((x, y, w, h))
    
    return parking_spaces, image

# Mor renk aralığını belirleyelim
lower_purple = np.array([130, 50, 50])
upper_purple = np.array([160, 255, 255])

# Park yerlerini kontrol edelim
image_path = 'otopark.jpg'
parking_spaces, image = detect_parking_spaces(image_path, lower_purple, upper_purple)

if image is not None:
    print(parking_spaces)

    # Tespit edilen park yerlerini görselleştirelim
    for (x, y, w, h) in parking_spaces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)  # Mor renk ile çiz
    cv2.imshow('Otopark Sistemi', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Görüntü yüklenemedi, dosya yolunu kontrol edin.")

class ParkingSystemGUI:
    def __init__(self, master, image_path, parking_spaces):
        self.master = master
        self.master.title("Otopark Sistemi")
        
        self.parking_spaces = parking_spaces
        self.image_path = image_path
        
        # Canvas oluşturma
        self.canvas = Canvas(master, width=800, height=600)
        self.canvas.pack()
        
        # Görüntüyü yükleyip yeniden boyutlandıralım
        self.image = Image.open(image_path)
        self.image = self.image.resize((800, 600), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # Park yerlerini çizelim
        self.rectangles = []
        for (x, y, w, h) in self.parking_spaces:
            rect = self.canvas.create_rectangle(x, y, x + w, y + h, outline='purple', width=2)
            self.rectangles.append(rect)
        
        # Araç yerleştirme butonu
        self.add_button = tk.Button(master, text="Araç Yerleştir", command=self.add_vehicle)
        self.add_button.pack()
        
        # Boş park yerlerinin oranını gösterelim
        self.status_label = tk.Label(master, text="")
        self.status_label.pack()
        
        # Park yeri durumlarını takip edelim
        self.parking_status = ['boş' for _ in self.parking_spaces]
        
        # Boş park yerlerinin oranını güncelleyelim
        self.update_status()
        
    def update_canvas(self):
        for idx, (x, y, w, h) in enumerate(self.parking_spaces):
            color = 'purple' if self.parking_status[idx] == 'boş' else 'blue'
            self.canvas.itemconfig(self.rectangles[idx], outline=color)
        
    def update_status(self):
        empty_count = self.parking_status.count('boş')
        total_count = len(self.parking_status)
        ratio = empty_count / total_count * 100
        self.status_label.config(text=f"Boş Park Yerleri Oranı: {ratio:.2f}% ({empty_count}/{total_count})")
        
    def add_vehicle(self):
        # Boş park yerlerini bul
        empty_spaces = [idx for idx, status in enumerate(self.parking_status) if status == 'boş']
        
        if empty_spaces:
            idx = empty_spaces[0]  # İlk boş park yerine araç yerleştir
            self.parking_status[idx] = 'dolu'  # Park yerini dolu olarak güncelle
            self.update_canvas()
            self.update_status()
        else:
            print("Tüm park yerleri dolu!")

if image is not None:
    # GUI'yi başlatalım
    root = tk.Tk()
    app = ParkingSystemGUI(root, image_path, parking_spaces)
    root.mainloop()
else:
    print("Görüntü yüklenemedi, GUI başlatılamadı.")
