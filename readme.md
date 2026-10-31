# 👻 Policy Phantom

**Policy Phantom** adalah aplikasi *compliance checker* berbasis *open-source AI* yang dirancang untuk memindai transkrip atau naskah video YouTube secara lokal. Aplikasi ini mendeteksi potensi pelanggaran pedoman monetisasi (seperti *Reused Content*, *Synthetic/AI Content*, hak cipta, dan sensitivitas bahasa) sebelum video diunggah, guna mencegah risiko **demonetisasi** (*Demonetization Graveyard*).

Proyek ini dibangun khusus untuk **Hacktoberfest Challenge Week 4: "Ghost in the Machine"**.

---

## 💡 Why Open Innovation Matters

Pada pembuatan konten digital, isu privasi, keamanan naskah, dan biaya operasional menjadi tantangan utama:

1. **Privasi & Keamanan Konten Terjamin:** Naskah dan transkrip video belum rilis kerap kali berisi ide sensitif atau kekayaan intelektual. Dengan menjalankan pemrosesan analisis secara lokal via *open-weight model*, data konten tidak pernah dikirim ke server pihak ketiga.
2. **Offline-First & Zero API Cost:** Pengguna dapat melakukan pemindaian lengkap tanpa koneksi internet dan tanpa batas kuota/biaya API berbayar.
3. **Fleksibilitas & Transparansi:** Penggunaan model *open-source/open-weight* memungkinkan penyesuaian *system prompt*, penggantian *engine* model secara bebas, dan transparansi penuh atas logika evaluasi kebijakan.

---

## 🛠️ Features & Horror-Themed UI

* **👻 Policy Phantom Engine:** Menganalisis naskah/transkrip video menggunakan model *open-weight* lokal (Llama 3.2 via Ollama).
* **🎙️ Local Audio Transcription:** Ekstraksi dan transkripsi audio dari file video `.mp4` secara otomatis menggunakan OpenAI Whisper lokal.
* **📊 Haunting Risk Meter & Radar Chart:** Visualisasi tingkat risiko demonetisasi (*Safe*, *Haunted*, atau *Demonetized*) beserta matriks breakdown 4 kategori kritis (Hak Cipta, Penggunaan AI, Sensitivitas Bahasa, Metadata).
* **🕯️ Exorcism Suggestions:** Rekomendasi konkret untuk merevisi kata-kata berisiko, melengkapi *disclosure* AI, serta memberikan alternatif naskah yang lebih aman.
* **🔄 Sync Policy Data (Opsional):** Integrasi pendamping via Gemini API untuk memperbarui basis data kebijakan lokal (`youtube_policy.json`) secara terorganisir.
* **🖥️ Retro Terminal Interface:** Antarmuka berbasis Gradio (`hmb/terminal`) dengan kustomisasi CSS bertema *haunted/eerie*.

---

## 🚀 Tech Stack

* **UI Framework:** [Gradio](https://gradio.app/) (`hmb/terminal` theme)
* **Primary Open-Weight LLM:** Gemma 2 (2B) via [Ollama](https://ollama.com/)
* **Audio Transcription:** [OpenAI Whisper](https://github.com/openai/whisper) (`tiny` model)
* **Data Visualization:** Plotly Graph Objects
* **Secondary Sync API (Opsional):** Google GenAI SDK (`gemini-2.5-flash`)
* **Environment Management:** Python-dotenv

---

## 💻 Installation & Local Setup

### Prasyarat

1. **Python 3.10+**
2. **FFmpeg** (Wajib terinstal di sistem operasi untuk mendukung ekstrak audio Whisper)
3. **Ollama** (Sudah terinstal dan berjalan di latar belakang)

### Langkah-Langkah

1. **Clone Repositori:**
```bash
git clone https://github.com/USERNAME/policy-phantom.git
cd policy-phantom

```


2. **Jalankan Model Lokal di Ollama:**
```bash
ollama run gemma2:2b

```


3. **Install Dependencies Python:**
```bash
pip install -r requirements.txt

```


4. **Konfigurasi Environment Variable (Opsional):**
Buat file `.env` di direktori utama jika ingin menggunakan fitur Sync Policy via Gemini:
```env
GEMINI_API_KEY=your_gemini_api_key_here

```


5. **Jalankan Aplikasi:**
```bash
python app.py

```


Buka URL lokal yang muncul di terminal (biasanya `[http://127.0.0.1:7860](http://127.0.0.1:7860)`).

---

## 📄 File Structure

```text
policy-phantom/
├── app.py                   # File utama aplikasi Gradio
├── youtube_policy.json      # Baseline data kebijakan monetisasi YouTube
├── requirements.txt         # Daftar dependency Python
├── .env.example             # Template file environment variable
├── .gitignore               # Pengecualian file sensitif/cache
└── README.md                # Dokumentasi proyek

```

---

## 🎃 Hacktoberfest Submission Context

* **Challenge:** Week 4 — *Ghost in the Machine*
* **Theme Interpretation:** Mengangkat tema roh yang mendiami dokumen kebijakan YouTube (*Policy Phantom*) untuk membantu kreator membebaskan konten mereka dari "kutukan" demonetisasi menggunakan *open-weight AI*.
