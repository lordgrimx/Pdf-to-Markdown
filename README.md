# PDF İşleme Uygulaması

Bu uygulama, PDF dosyalarını görüntülere dönüştürüp, bu görüntüleri Google Gemini AI kullanarak Markdown formatında açıklamalı notlara çevirir. Özellikle Obsidian kullanıcıları için optimize edilmiştir.

## Özellikler

- PDF dosyalarını yüksek kaliteli görüntülere dönüştürme
- Görüntüleri Google Gemini AI ile analiz etme
- Markdown formatında otomatik not oluşturma
- Obsidian uyumlu görüntü referansları (`![[dosya_adi.png]]` formatında)
- Kullanıcı dostu arayüz
- Paralel işleme desteği ile hızlı dönüşüm

## Kurulum

1. En son sürümü [Releases](link-to-releases) sayfasından indirin
2. İndirdiğiniz exe dosyasını istediğiniz bir klasöre çıkarın
3. Uygulamayı çalıştırın

## İlk Kullanım

İlk çalıştırmada uygulama sizden iki önemli bilgi isteyecektir:

1. **Google API Key**: 
   - [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
   - API key oluşturun
   - Oluşturduğunuz API key'i uygulamaya girin

2. **Obsidian Klasörü**:
   - Obsidian vault'unuzun ana klasörünü seçin
   - Bu klasör, görüntü ve Markdown dosyalarının varsayılan konumu olarak kullanılacak

## Kullanım

### PDF'den Görüntüye Dönüştürme

1. "PDF'den Görüntü" sekmesine geçin
2. "PDF Dosyası Seç" butonuna tıklayın ve bir PDF dosyası seçin
3. "Çıktı Klasörünü Seç" butonuna tıklayın
4. "PDF'yi Görüntülere Dönüştür" butonuna tıklayın
5. Görüntüler seçtiğiniz klasörün altında `pdf_images` klasörüne kaydedilecek

### Görüntüleri İşleme

1. "Görüntü İşleme" sekmesine geçin
2. "Görüntü Klasörünü Seç" butonuna tıklayın ve görüntülerin bulunduğu klasörü seçin
3. "Markdown Kayıt Yerini Seç" butonuna tıklayın
4. İsterseniz Markdown dosya adını değiştirin (varsayılan: output.md)
5. "Görüntüleri İşle" butonuna tıklayın
6. İşlem tamamlandığında Markdown dosyanız hazır olacak

## Ayarları Değiştirme

Ayarlarınızı değiştirmek isterseniz:
1. `C:\Users\<kullanıcı>\AppData\Roaming\PDFProcessor\config.json` dosyasını silin
2. Uygulamayı yeniden başlatın
3. Yeni ayarlarınızı girin

## Sistem Gereksinimleri

- Windows 10 veya üzeri
- İnternet bağlantısı (Google Gemini AI için)
- Geçerli bir Google API key
- Obsidian 0.9.0 veya daha yeni
- Python 3.10 veya daha yeni

## Sorun Giderme

1. **API Rate Limit Hatası**: 
   - Bu hata çok sayıda görüntüyü hızlı işlemeye çalıştığınızda oluşabilir
   - Biraz bekleyip tekrar deneyin

2. **Görüntü İşleme Hatası**:
   - Görüntülerin PNG, JPG veya JPEG formatında olduğundan emin olun
   - Görüntü dosyalarının bozuk olmadığını kontrol edin

3. **Uygulama Başlatma Hatası**:
   - AppData klasöründeki config.json dosyasını silip tekrar deneyin
   - Uygulamayı yönetici olarak çalıştırmayı deneyin

## Gizlilik

- API anahtarınız ve Obsidian klasör yolunuz yerel bilgisayarınızda güvenli bir şekilde saklanır
- Görüntüler analiz için Google Gemini AI servisine gönderilir
- Başka hiçbir veri toplanmaz veya paylaşılmaz

## Lisans

Bu uygulama MIT lisansı altında dağıtılmaktadır.
