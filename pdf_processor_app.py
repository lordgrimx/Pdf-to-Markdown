import sys
import os
import json
import google.generativeai as genai
from PIL import Image
import re
import fitz
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                           QVBoxLayout, QWidget, QFileDialog, QProgressBar,
                           QLineEdit, QTextEdit, QTabWidget, QHBoxLayout,
                           QDialog, QMessageBox)
from PyQt5.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Uygulama Ayarları')
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # API Key
        api_layout = QHBoxLayout()
        api_label = QLabel('Google API Key:')
        self.api_input = QLineEdit()
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        layout.addLayout(api_layout)
        
        # Obsidian Yolu
        obsidian_layout = QHBoxLayout()
        obsidian_label = QLabel('Obsidian Klasörü:')
        self.obsidian_input = QLineEdit()
        self.obsidian_button = QPushButton('Seç')
        self.obsidian_button.clicked.connect(self.select_obsidian_path)
        obsidian_layout.addWidget(obsidian_label)
        obsidian_layout.addWidget(self.obsidian_input)
        obsidian_layout.addWidget(self.obsidian_button)
        layout.addLayout(obsidian_layout)
        
        # Kaydet butonu
        self.save_button = QPushButton('Kaydet')
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        
    def select_obsidian_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Obsidian Klasörünü Seç")
        if folder:
            self.obsidian_input.setText(folder)
            
class PDFProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.initUI()
        
    def get_config_path(self):
        """Config dosyasının yolunu döndürür"""
        app_data = os.getenv('APPDATA')
        app_folder = os.path.join(app_data, 'PDFProcessor')
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)
        return os.path.join(app_folder, 'config.json')
        
    def load_config(self):
        """Yapılandırma dosyasını yükle veya oluştur"""
        config_path = self.get_config_path()
        
        if not os.path.exists(config_path):
            self.show_config_dialog()
        else:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
                    self.obsidian_path = config.get('obsidian_path')
                    
                if not self.api_key or not self.obsidian_path:
                    self.show_config_dialog()
            except:
                self.show_config_dialog()
                
    def show_config_dialog(self):
        """Yapılandırma dialogunu göster"""
        dialog = ConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.api_key = dialog.api_input.text().strip()
            self.obsidian_path = dialog.obsidian_input.text().strip()
            
            # Yapılandırmayı kaydet
            config_path = self.get_config_path()
            with open(config_path, 'w') as f:
                json.dump({
                    'api_key': self.api_key,
                    'obsidian_path': self.obsidian_path
                }, f)
        else:
            QMessageBox.critical(self, 'Hata', 'Uygulama ayarları yapılandırılmadı!')
            sys.exit(1)
        
    def initUI(self):
        self.setWindowTitle('PDF İşleme Uygulaması')
        self.setGeometry(100, 100, 1000, 700)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Tab widget oluştur
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # PDF'den Görüntü tab'i
        pdf_tab = QWidget()
        pdf_layout = QVBoxLayout(pdf_tab)
        
        # PDF dosya seçimi
        pdf_file_layout = QHBoxLayout()
        self.pdf_file_button = QPushButton('PDF Dosyası Seç')
        self.pdf_file_button.clicked.connect(self.select_pdf_file)
        self.pdf_file_label = QLabel('Henüz dosya seçilmedi')
        pdf_file_layout.addWidget(self.pdf_file_button)
        pdf_file_layout.addWidget(self.pdf_file_label)
        pdf_layout.addLayout(pdf_file_layout)
        
        # Çıktı klasörü seçimi
        output_folder_layout = QHBoxLayout()
        self.output_folder_button = QPushButton('Çıktı Klasörünü Seç')
        self.output_folder_button.clicked.connect(self.select_output_folder)
        self.output_folder_label = QLabel('Henüz klasör seçilmedi')
        output_folder_layout.addWidget(self.output_folder_button)
        output_folder_layout.addWidget(self.output_folder_label)
        pdf_layout.addLayout(output_folder_layout)
        
        # PDF işlem çubuğu
        self.pdf_progress = QProgressBar()
        pdf_layout.addWidget(self.pdf_progress)
        
        # PDF dönüştür butonu
        self.convert_button = QPushButton('PDF\'yi Görüntülere Dönüştür')
        self.convert_button.clicked.connect(self.convert_pdf)
        self.convert_button.setEnabled(False)
        pdf_layout.addWidget(self.convert_button)
        
        # PDF durum mesajları
        self.pdf_status = QTextEdit()
        self.pdf_status.setReadOnly(True)
        pdf_layout.addWidget(self.pdf_status)
        
        tabs.addTab(pdf_tab, "PDF'den Görüntü")
        
        # Gemini tab'i
        gemini_tab = QWidget()
        gemini_layout = QVBoxLayout(gemini_tab)
        
        # Görüntü klasörü seçimi
        gemini_folder_layout = QHBoxLayout()
        self.gemini_folder_button = QPushButton('Görüntü Klasörünü Seç')
        self.gemini_folder_button.clicked.connect(self.select_gemini_folder)
        self.gemini_folder_label = QLabel('Henüz klasör seçilmedi')
        gemini_folder_layout.addWidget(self.gemini_folder_button)
        gemini_folder_layout.addWidget(self.gemini_folder_label)
        gemini_layout.addLayout(gemini_folder_layout)
        
        # Markdown dosyası kaydetme yeri seçimi
        md_save_layout = QHBoxLayout()
        self.md_save_button = QPushButton('Markdown Kayıt Yerini Seç')
        self.md_save_button.clicked.connect(self.select_md_save_location)
        self.md_save_label = QLabel('Henüz kayıt yeri seçilmedi')
        md_save_layout.addWidget(self.md_save_button)
        md_save_layout.addWidget(self.md_save_label)
        gemini_layout.addLayout(md_save_layout)
        
        # Markdown dosya adı
        md_file_layout = QHBoxLayout()
        md_file_label = QLabel('Markdown Dosya Adı:')
        self.md_file_input = QLineEdit('output.md')
        md_file_layout.addWidget(md_file_label)
        md_file_layout.addWidget(self.md_file_input)
        gemini_layout.addLayout(md_file_layout)
        
        # Gemini işlem çubuğu
        self.gemini_progress = QProgressBar()
        gemini_layout.addWidget(self.gemini_progress)
        
        # Gemini işle butonu
        self.process_button = QPushButton('Görüntüleri İşle')
        self.process_button.clicked.connect(self.process_images)
        self.process_button.setEnabled(False)
        gemini_layout.addWidget(self.process_button)
        
        # Gemini durum mesajları
        self.gemini_status = QTextEdit()
        self.gemini_status.setReadOnly(True)
        gemini_layout.addWidget(self.gemini_status)
        
        tabs.addTab(gemini_tab, "Görüntü İşleme")
        
        # Değişkenler
        self.pdf_file = None
        self.output_folder = None
        self.gemini_folder = None
        self.md_save_location = None
        
    def select_pdf_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF Dosyası Seç",
            "",
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_file = file_path
            self.pdf_file_label.setText(f'Seçilen dosya: {os.path.basename(file_path)}')
            self.update_convert_button()
            
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Çıktı Klasörünü Seç",
            self.obsidian_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(f'Seçilen klasör: {folder}')
            self.update_convert_button()
            
    def select_md_save_location(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Markdown Kayıt Yerini Seç",
            self.obsidian_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.md_save_location = folder
            self.md_save_label.setText(f'Seçilen kayıt yeri: {folder}')
            self.update_process_button()
            
    def select_gemini_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Görüntü Klasörünü Seç",
            self.obsidian_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.gemini_folder = folder
            self.gemini_folder_label.setText(f'Seçilen klasör: {folder}')
            self.update_process_button()
            
    def update_convert_button(self):
        self.convert_button.setEnabled(bool(self.pdf_file and self.output_folder))
            
    def update_process_button(self):
        self.process_button.setEnabled(bool(self.gemini_folder and self.md_save_location))
            
    def convert_pdf(self):
        try:
            # PDF dosyasını aç
            pdf_document = fitz.open(self.pdf_file)
            total_pages = len(pdf_document)
            
            # pdf_images klasörünü oluştur
            pdf_images_dir = os.path.join(self.output_folder, "pdf_images")
            if not os.path.exists(pdf_images_dir):
                os.makedirs(pdf_images_dir)
            
            # İlerleme çubuğunu ayarla
            self.pdf_progress.setMaximum(total_pages)
            
            # Her sayfa için
            for page_num in range(total_pages):
                # Sayfayı al
                page = pdf_document[page_num]
                
                # Sayfayı görüntüye dönüştür
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI çözünürlük
                
                # Görüntüyü pdf_images klasörüne kaydet
                image_path = os.path.join(pdf_images_dir, f"page_{page_num + 1}.png")
                pix.save(image_path)
                
                # İlerlemeyi güncelle
                self.pdf_progress.setValue(page_num + 1)
                self.pdf_status.append(f"Sayfa {page_num + 1}/{total_pages} dönüştürüldü")
                QApplication.processEvents()
            
            # PDF'i kapat
            pdf_document.close()
            
            self.pdf_status.append(f"Dönüştürme tamamlandı! Görüntüler {pdf_images_dir} klasörüne kaydedildi.")
            
        except Exception as e:
            self.pdf_status.append(f"Hata: {str(e)}")
            
    def fix_image_references(self, content, image_folder, image_file):
        """Görüntü referanslarını düzeltir"""
        # Önce tüm üçlü kapanış parantezlerini düzelt
        content = content.replace(']]]', ']]')
        
        # Resim yolunu oluştur
        image_path = f"{image_folder}/{image_file}"
        
        # Çift köşeli parantezli referansları düzelt
        pattern = r'!\[\[(.*?)\]\]'
        content = re.sub(pattern, f'![[{image_path}]]', content)
        
        # Tek köşeli parantezli referansları düzelt
        pattern = r'!\[(.*?)\](?!\])'
        content = re.sub(pattern, f'![[{image_path}]]', content)
        
        return content
            
    def process_single_image(self, image_file, image_folder_name, model):
        """Tek bir görüntüyü işler"""
        try:
            # API rate limit'e takılmamak için kısa bir bekleme
            time.sleep(1)
            
            image_path = os.path.join(self.gemini_folder, image_file)
            
            # Görüntüyü PIL ile yükle
            img = Image.open(image_path)
            
            # Gemini'ye gönder
            prompt = """
            Bu görüntü bir PowerPoint slaytından alınmış bir sayfadır. 
            Lütfen içeriği önce Sadece Türkçeye çevir sonra analiz edip aşağıdaki formatta bir Markdown çıktısı oluştur:

            ### [Slaytın başlığı]
            ![[DOSYAADI]]
            - Türkçe çeviri ve açıklamalar: [Görüntüdeki her ifadenin Türkçe çevirisi ve açıklaması]

            >Not: [Slayttaki içeriğin kısa özeti ve açıklaması]
            """
            
            # DOSYAADI placeholder'ını gerçek dosya adıyla değiştir
            prompt = prompt.replace('DOSYAADI', f"{image_folder_name}/{image_file}")
            
            # API hatası durumunda 3 kez deneme yap
            max_retries = 3
            retry_delay = 2  # saniye
            
            for attempt in range(max_retries):
                try:
                    response = model.generate_content([prompt, img])
                    break
                except Exception as e:
                    if attempt < max_retries - 1:  # Son deneme değilse
                        time.sleep(retry_delay)  # Bekle ve tekrar dene
                        retry_delay *= 2  # Her denemede bekleme süresini iki katına çıkar
                    else:
                        raise e  # Son denemeyse hatayı yukarı fırlat
            
            # Yanıtı düzelt
            md_content = self.fix_image_references(response.text, image_folder_name, image_file)
            
            # Görüntüyü kapat
            img.close()
            
            return image_file, md_content
            
        except Exception as e:
            return image_file, f"Hata ({image_file}): {str(e)}\n\n"
            
    def process_images(self):
        if not self.gemini_folder or not self.md_save_location:
            self.gemini_status.append("Lütfen görüntü klasörünü ve Markdown kayıt yerini seçin!")
            return
            
        try:
            # API'yi yapılandır
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Görüntü klasörünün adını al
            image_folder_name = os.path.basename(self.gemini_folder)
            
            # Görüntü dosyalarını bul ve sırala (sayfa numarasına göre)
            image_files = sorted([f for f in os.listdir(self.gemini_folder) 
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
                               key=lambda x: int(re.search(r'(\d+)', x).group()))
            
            if not image_files:
                self.gemini_status.append("Klasörde görüntü dosyası bulunamadı!")
                return
                
            self.gemini_progress.setMaximum(len(image_files))
            
            # Markdown dosyasını seçilen konuma oluştur
            md_file_path = os.path.join(self.md_save_location, self.md_file_input.text())
            
            # Sonuçları saklayacak sözlük
            results = {}
            
            # ThreadPoolExecutor ile parallel işleme (worker sayısını 2'ye düşürdük)
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Tüm görevleri başlat
                future_to_image = {
                    executor.submit(self.process_single_image, img_file, image_folder_name, model): img_file 
                    for img_file in image_files
                }
                
                # Tamamlanan görevleri takip et
                completed = 0
                for future in as_completed(future_to_image):
                    image_file = future_to_image[future]
                    try:
                        img_file, content = future.result()
                        results[img_file] = content
                        
                        # İlerlemeyi güncelle
                        completed += 1
                        self.gemini_progress.setValue(completed)
                        self.gemini_status.append(f"İşlenen görüntü {completed}/{len(image_files)}: {img_file}")
                        QApplication.processEvents()
                        
                    except Exception as e:
                        self.gemini_status.append(f"Hata ({image_file}): {str(e)}")
            
            # Sonuçları sıralı şekilde dosyaya yaz
            with open(md_file_path, 'w', encoding='utf-8') as md_file:
                for image_file in image_files:
                    if image_file in results:
                        md_file.write(results[image_file] + "\n\n")
            
            self.gemini_status.append(f"\nİşlem tamamlandı! Çıktı dosyası: {md_file_path}")
            
        except Exception as e:
            self.gemini_status.append(f"Hata: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = PDFProcessorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
