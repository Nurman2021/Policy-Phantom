import gradio as gr
import requests
import json
import os
import whisper
import re
from datetime import datetime
import plotly.graph_objects as go
from google import genai
from dotenv import load_dotenv
import time

# ====================== LOAD ENV ======================
load_dotenv()

POLICY_FILE = "youtube_policy.json"

print("Memuat model Whisper...")
whisper_model = whisper.load_model("tiny")

def load_policy():
    if not os.path.exists(POLICY_FILE):
        return {
            "last_updated": "No Data",
            "rules": ["File youtube_policy.json not found! Click Sync Policy button."]
        }
    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ====================== TRANSLATION DICTIONARY ======================
I18N = {
    "en": {
        "title": "👻 Policy Phantom",
        "subtitle": "The ghost in YouTube policy docs saving your content from the demonetization graveyard.",
        "badge": "*Runs entirely locally using open-weight models*",
        "sync_btn": "🔄 Sync Policy Data (via Gemini — Optional)",
        "label_video": "Upload Video File (.mp4)",
        "label_script": "Or Paste Script Text",
        "placeholder_script": "Paste script here...",
        "chk_voice": "Uses AI Voiceover",
        "chk_visual": "Uses AI Images / Avatars",
        "chk_third": "Uses Third-Party Clips",
        "btn_submit": "👻 Summon Policy Phantom",
        "radar_title": "Haunting Risk Radar",
        "label_breakdown": "Haunting Category Breakdown",
        "cat_ai": "AI Usage & Disclosure",
        "cat_meta": "Metadata & Third-Party Clips",
        "cat_copy": "Copyright & Visuals",
        "cat_lang": "Language Sensitivity",
        "status_safe": "SAFE (CURSE FREE)",
        "status_haunted": "HAUNTED (EXORCISM NEEDED)",
        "status_demonetized": "DEMONETIZED (HEAVY CURSE)",
        "msg_waking": "👻 **Policy Phantom is waking up... (Initiating scan)**",
        "msg_extracting": "👻 **Policy Phantom is extracting audio from your video...**",
        "msg_deliberating": "👻 **Policy Phantom is consulting local LLM to evaluate the curse...**",
        "msg_no_input": "💡 *Please upload a video or paste a script first!*",
        "msg_error_audio": "⚠️ **Failed to extract audio!**\n\n`Error: {e}`",
        "msg_error_ollama": "❌ **Failed to connect to Ollama.**\n\n`Error: {e}`",
        "msg_waiting": "*Policy Phantom awaits your command...*",
        "prompt_role": "You are Policy Phantom — a spirit living inside YouTube policy documents.",
        "prompt_task": "Your task is to examine if a video will be haunted by demonetization.",
        "prompt_lang_instruction": "Respond entirely in English.",
        "prompt_format": """
MUST include estimated risk percentage values in the first lines with EXACT format:
SKOR_TOTAL: [0-100]%
SKOR_HAK_CIPTA: [0-100]%
SKOR_AI: [0-100]%
SKOR_BAHASA: [0-100]%
SKOR_METADATA: [0-100]%

Continue with report in the following Markdown format:

### 👻 Detected Transcript
> "(Display first 1-2 sentences of transcript)"

### 🔍 Haunting Indications
- **Risk Point 1:** [Detailed explanation]
- **Risk Point 2:** [Detailed explanation if any]

### 🕯️ Exorcism Suggestions
1. **Word/Sentence Adjustments:** [Concrete suggestions]
2. **Disclosure & Metadata:** [Suggestions regarding AI / clips]

### 🛡️ Safer Alternative Version
> "[Provide 1-2 safer alternative sentences]"
"""
    },
    "id": {
        "title": "👻 Policy Phantom",
        "subtitle": "Roh yang membaca kebijakan YouTube supaya channelmu tidak dihantui demonetisasi.",
        "badge": "*Berjalan sepenuhnya lokal menggunakan open-weight model*",
        "sync_btn": "🔄 Sync Policy Data (via Gemini — Opsional)",
        "label_video": "Unggah File Video (.mp4)",
        "label_script": "Atau Tempelkan Naskah Teks",
        "placeholder_script": "Tempelkan naskah di sini...",
        "chk_voice": "Menggunakan Suara AI (AI Voiceover)",
        "chk_visual": "Menggunakan Gambar / Avatar AI",
        "chk_third": "Menggunakan Klip Pihak Ketiga",
        "btn_submit": "👻 Panggil Policy Phantom",
        "radar_title": "Radar Matriks Haunting",
        "label_breakdown": "Breakdown Kategori Haunting",
        "cat_ai": "Penggunaan AI & Disclosure",
        "cat_meta": "Metadata & Klip Pihak Ketiga",
        "cat_copy": "Hak Cipta & Visual",
        "cat_lang": "Sensitivitas Bahasa",
        "status_safe": "AMAN (BEBAS KUTUKAN)",
        "status_haunted": "HAUNTED (PERLU EXORCISM)",
        "status_demonetized": "DEMONETIZED (KUTUKAN BERAT)",
        "msg_waking": "👻 **Policy Phantom sedang bangun... (Menginisiasi pemindaian)**",
        "msg_extracting": "👻 **Policy Phantom sedang mengekstrak suara videomu...**",
        "msg_deliberating": "👻 **Policy Phantom sedang berunding dengan LLM lokal untuk mengevaluasi kutukan...**",
        "msg_no_input": "💡 *Harap unggah video atau tempelkan naskah terlebih dahulu!*",
        "msg_error_audio": "⚠️ **Gagal mengekstrak audio!**\n\n`Error: {e}`",
        "msg_error_ollama": "❌ **Gagal terhubung ke Ollama.**\n\n`Error: {e}`",
        "msg_waiting": "*Policy Phantom menunggu perintahmu...*",
        "prompt_role": "Kamu adalah Policy Phantom — roh yang hidup di dalam dokumen kebijakan YouTube.",
        "prompt_task": "Tugasmu adalah memeriksa apakah sebuah video akan dihantui oleh demonetisasi.",
        "prompt_lang_instruction": "Jawab seluruhnya dalam Bahasa Indonesia.",
        "prompt_format": """
WAJIB cantumkan nilai persentase estimasi risiko di baris-baris pertama dengan format TEPAT:
SKOR_TOTAL: [0-100]%
SKOR_HAK_CIPTA: [0-100]%
SKOR_AI: [0-100]%
SKOR_BAHASA: [0-100]%
SKOR_METADATA: [0-100]%

Lanjutkan dengan laporan dalam format Markdown berikut:

### 👻 Transkrip yang Terdeteksi
> "(Tampilkan 1-2 kalimat awal transkrip)"

### 🔍 Indikasi Haunting
- **Poin Risiko 1:** [Penjelasan rinci]
- **Poin Risiko 2:** [Penjelasan jika ada]

### 🕯️ Saran Exorcism
1. **Penyesuaian Kata/Kalimat:** [Saran konkret]
2. **Disclosure & Metadata:** [Saran terkait AI / klip]

### 🛡️ Versi yang Lebih Aman
> "[Sediakan 1-2 kalimat alternatif yang lebih aman]"
"""
    }
}

# ====================== UPDATE POLICY (GEMINI - OPSIONAL) ======================
def update_policy_data(lang):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return f"⚠️ **Sync Failed:** `GEMINI_API_KEY` not found. Local data kept." if lang == "en" else f"⚠️ **Gagal Sync:** `GEMINI_API_KEY` tidak ditemukan. Data lokal tetap digunakan."

    try:
        client = genai.Client(api_key=api_key)
        prompt_update = """
        Fetch and summarize latest YouTube monetization policy guidelines (Advertiser-Friendly Guidelines, Reused Content, & Synthetic/AI Content Policy).
        Return ONLY a clean JSON array containing critical rule points. Format example:
        [
            "Rule 1...",
            "Rule 2..."
        ]
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_update
        )
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
        new_rules = json.loads(raw_text)
        updated_data = {
            "last_updated": now_str,
            "rules": new_rules
        }
        with open(POLICY_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, indent=4, ensure_ascii=False)
            
        return f"✅ **Sync Success via Gemini** | Last Sync: {now_str} ({len(new_rules)} rules updated)" if lang == "en" else f"✅ **Berhasil Sync via Gemini** | Terakhir Sync: {now_str} ({len(new_rules)} aturan diperbarui)"
        
    except Exception as e:
        return f"❌ **Sync Failed:** `{str(e)}`"

# ====================== RADAR CHART ======================
def create_radar_chart(copyright_score, ai_score, lang_score, metadata_score, lang="en"):
    t = I18N[lang]
    categories = [t["cat_copy"], t["cat_ai"], t["cat_lang"], t["cat_meta"]]
    values = [copyright_score, ai_score, lang_score, metadata_score]
    
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(34, 197, 94, 0.2)',
        line=dict(color='#22c55e', width=2),
        marker=dict(size=6, color='#4ade80'),
        name='Haunting Score'
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='#0a0a0a',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                gridcolor='#1f1f1f',
                color='#22c55e'
            ),
            angularaxis=dict(
                gridcolor='#1f1f1f',
                color='#86efac'
            )
        ),
        paper_bgcolor='#0a0a0a',
        font=dict(color='#86efac', family="monospace"),
        margin=dict(l=30, r=30, t=30, b=30),
        showlegend=False,
        autosize=True
    )
    return fig

# ====================== RISK METER ======================
def generate_risk_meter_html(score, lang="en"):
    t = I18N[lang]
    if score > 70:
        color = "#ef4444"
        status_label = t["status_demonetized"]
    elif score > 35:
        color = "#eab308"
        status_label = t["status_haunted"]
    else:
        color = "#22c55e"
        status_label = t["status_safe"]
        
    html_code = f"""
    <div style="background-color: #0a0a0a; padding: 12px 16px; border-radius: 4px; border: 1px solid #22c55e33; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; font-family: monospace; color: #86efac;">
            <span style="font-size: 0.95em; font-weight: 600;">Status: <span style="color: {color}; font-weight: 700;">{status_label}</span></span>
            <span style="font-size: 1.25em; font-weight: 800; color: {color};">{score}%</span>
        </div>
        <div style="position: relative; width: 100%; height: 8px; background: linear-gradient(to right, #22c55e 0%, #22c55e 35%, #eab308 35%, #eab308 70%, #ef4444 70%, #ef4444 100%); border-radius: 2px; margin-top: 8px;">
            <div style="position: absolute; left: calc({score}% - 4px); top: -4px; width: 8px; height: 16px; background-color: #ffffff; border-radius: 1px; box-shadow: 0 0 6px rgba(0,0,0,0.8);"></div>
        </div>
    </div>
    """
    return html_code

# ====================== FUNGSI UTAMA (GENERATOR) ======================
def periksa_kepatuhan(video_file, naskah_text, suara_ai, visual_ai, pihak_ketiga, lang_choice):
    lang = "en" if lang_choice == "English" else "id"
    t = I18N[lang]

    # Validasi awal: Jika video dan naskah sama-sama kosong
    if video_file is None and (not naskah_text or not naskah_text.strip()):
        yield (
            generate_risk_meter_html(0, lang),
            create_radar_chart(0, 0, 0, 0, lang),
            {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
            t["msg_no_input"],
            gr.update(interactive=True) # Tombol tetap aktif agar user bisa langsung menginput
        )
        return # Hentikan eksekusi langsung

    # Status awal jika input valid - Lock button & jalankan pemindaian
    yield (
        generate_risk_meter_html(0, lang),
        create_radar_chart(0, 0, 0, 0, lang),
        {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
        t["msg_waking"],
        gr.update(interactive=False)
    )
    
    time.sleep(0.8)

    transkrip_final = ""
    
    if video_file is not None:
        yield (
            generate_risk_meter_html(0, lang),
            create_radar_chart(0, 0, 0, 0, lang),
            {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
            t["msg_extracting"],
            gr.update(interactive=False)
        )
        try:
            file_path = video_file.name if hasattr(video_file, "name") else str(video_file)
            result_whisper = whisper_model.transcribe(file_path, fp16=False)
            transkrip_final = result_whisper.get("text", "").strip()
        except Exception as e:
            yield (
                generate_risk_meter_html(0, lang),
                create_radar_chart(0, 0, 0, 0, lang),
                {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
                t["msg_error_audio"].format(e=str(e)),
                gr.update(interactive=True)
            )
            return
    elif naskah_text and naskah_text.strip():
        transkrip_final = naskah_text.strip()

    else:
        yield (
            generate_risk_meter_html(0, lang),
            create_radar_chart(0, 0, 0, 0, lang),
            {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
            t["msg_no_input"],
            gr.update(interactive=True)
        )
        return

    yield (
        generate_risk_meter_html(0, lang),
        create_radar_chart(0, 0, 0, 0, lang),
        {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
        t["msg_deliberating"],
        gr.update(interactive=False)
    )

    policy_data = load_policy()
    rules_list = policy_data.get("rules", [])
    policy_text = "\n".join([f"- {r}" for r in rules_list])
    last_sync = policy_data.get("last_updated", "Unknown")
    
    transkrip_ringkas = transkrip_final[:2500]
    
    system_prompt = f"""
{t["prompt_role"]}
{t["prompt_task"]}
{t["prompt_lang_instruction"]}

POLICY GUIDELINES (Version Sync: {last_sync}):
{policy_text}

User Content Metadata:
- Uses AI Voiceover: {suara_ai}
- Uses AI Visuals/Avatars: {visual_ai}
- Uses Third-Party Clips: {pihak_ketiga}

{t["prompt_format"]}
"""
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "gemma2:2b",
            "prompt": f"{system_prompt}\n\nTranscript/Script:\n{transkrip_ringkas}",
            "options": {"temperature": 0.2},
            "stream": False
        })
        
        hasil_teks = response.json()['response']
        
        score_total = int(re.search(r'SKOR_TOTAL:\s*(\d+)%', hasil_teks).group(1)) if re.search(r'SKOR_TOTAL:\s*(\d+)%', hasil_teks) else 20
        score_copyright = int(re.search(r'SKOR_HAK_CIPTA:\s*(\d+)%', hasil_teks).group(1)) if re.search(r'SKOR_HAK_CIPTA:\s*(\d+)%', hasil_teks) else 10
        score_ai = int(re.search(r'SKOR_AI:\s*(\d+)%', hasil_teks).group(1)) if re.search(r'SKOR_AI:\s*(\d+)%', hasil_teks) else (70 if suara_ai or visual_ai else 15)
        score_lang = int(re.search(r'SKOR_BAHASA:\s*(\d+)%', hasil_teks).group(1)) if re.search(r'SKOR_BAHASA:\s*(\d+)%', hasil_teks) else 10
        score_meta = int(re.search(r'SKOR_METADATA:\s*(\d+)%', hasil_teks).group(1)) if re.search(r'SKOR_METADATA:\s*(\d+)%', hasil_teks) else (60 if pihak_ketiga else 10)
        
        hasil_markdown_bersih = re.sub(r'SKOR_[A-Z_]+:\s*\d+%\n?', '', hasil_teks).strip()
        radar_fig = create_radar_chart(score_copyright, score_ai, score_lang, score_meta, lang)
        
        label_dict = {
            t["cat_ai"]: score_ai / 100.0,
            t["cat_meta"]: score_meta / 100.0,
            t["cat_copy"]: score_copyright / 100.0,
            t["cat_lang"]: score_lang / 100.0
        }
        
        # Unlock button
        yield (
            generate_risk_meter_html(score_total, lang),
            radar_fig,
            label_dict,
            hasil_markdown_bersih,
            gr.update(interactive=True)
        )
        
    except Exception as e:
        yield (
            generate_risk_meter_html(0, lang),
            create_radar_chart(0, 0, 0, 0, lang),
            {t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0},
            t["msg_error_ollama"].format(e=str(e)),
            gr.update(interactive=True)
        )

# ====================== DYNAMIC UI SWITCH ======================
def change_language(lang_choice):
    lang = "en" if lang_choice == "English" else "id"
    t = I18N[lang]
    initial_policy = load_policy()
    last_time = initial_policy.get("last_updated", "Not Synced")
    
    policy_md = f"**Policy Baseline:** `youtube_policy.json` | **Last Sync:** {last_time}" if lang == "en" else f"**Baseline Kebijakan:** `youtube_policy.json` | **Terakhir Sync:** {last_time}"
    
    return [
        f"# {t['title']}\n### {t['subtitle']}\n{t['badge']}", # 1. header_md
        policy_md,                                           # 2. policy_status
        gr.update(value=t["sync_btn"]),                      # 3. btn_update
        gr.update(label=t["label_video"]),                   # 4. input_video
        gr.update(label=t["label_script"], placeholder=t["placeholder_script"]), # 5. input_naskah
        gr.update(label=t["chk_voice"]),                     # 6. chk_suara
        gr.update(label=t["chk_visual"]),                    # 7. chk_visual
        gr.update(label=t["chk_third"]),                     # 8. chk_pihak_ketiga
        gr.update(value=t["btn_submit"]),                    # 9. btn_submit
        generate_risk_meter_html(0, lang),                   # 10. output_risk_bar
        create_radar_chart(0, 0, 0, 0, lang),                # 11. output_radar
        gr.update(                                           # 12. output_labels
            label=t["label_breakdown"],
            value={t["cat_ai"]: 0.0, t["cat_meta"]: 0.0, t["cat_copy"]: 0.0, t["cat_lang"]: 0.0}
        ),
        t["msg_waiting"]                                     # 13. output_hasil
    ]
# ====================== CSS & JS ======================
custom_css = """
#results-container {
    position: relative;
    border: 1px solid #22c55e44;
    border-radius: 4px;
    padding: 16px;
    background-color: #0a0a0a;
    min-height: 420px;
}

#results-container:fullscreen {
    background: #000000;
    padding: 24px;
}

#results-toolbar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-bottom: 10px;
    height: 32px;
}

#results-fullscreen-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 30px;
    border: 1px solid #22c55e66;
    border-radius: 3px;
    background: #111111;
    color: #22c55e;
    cursor: pointer;
    font-size: 16px;
}

#results-fullscreen-btn:hover {
    background: #1a1a1a;
    color: #4ade80;
}
"""

js_head = """
<script>
document.addEventListener("click", async (event) => {
    const button = event.target.closest("#results-fullscreen-btn");
    if (!button) return;
    const container = document.getElementById("results-container");
    if (!container) return;
    try {
        if (document.fullscreenElement === container) {
            await document.exitFullscreen();
        } else {
            await container.requestFullscreen();
        }
    } catch (error) {
        console.error("Fullscreen error:", error);
    }
});

document.addEventListener("fullscreenchange", () => {
    const button = document.getElementById("results-fullscreen-btn");
    if (!button) return;
    const isFullscreen = !!document.fullscreenElement;
    button.textContent = isFullscreen ? "🗗" : "⛶";
    button.title = isFullscreen ? "Exit Fullscreen" : "Expand Fullscreen";
    setTimeout(() => window.dispatchEvent(new Event("resize")), 150);
});
</script>
"""

# ====================== INTERFACE ======================
with gr.Blocks(
    title="Policy Phantom",
    theme="hmb/terminal",
    css=custom_css,
    head=js_head
) as demo:
    
    with gr.Row():
        with gr.Column(scale=3):
            header_md = gr.Markdown(f"# {I18N['en']['title']}\n### {I18N['en']['subtitle']}\n{I18N['en']['badge']}")
        with gr.Column(scale=1, min_width=120):
            lang_selector = gr.Radio(
                choices=["English", "Bahasa Indonesia"],
                value="English",
                label="🌐 Language / Bahasa",
                interactive=True
            )
    
    initial_policy = load_policy()
    last_time = initial_policy.get("last_updated", "Not Synced")
    
    policy_status = gr.Markdown(
        f"**Policy Baseline:** `youtube_policy.json` | **Last Sync:** {last_time}"
    )
    
    btn_update = gr.Button(
        I18N["en"]["sync_btn"],
        variant="secondary",
        size="sm"
    )
    
    gr.Markdown("---")
    
    with gr.Row():
        # Left Column
        with gr.Column(scale=1, min_width=320):
            input_video = gr.Video(label=I18N["en"]["label_video"], sources=["upload"])
            input_naskah = gr.Textbox(
                lines=3,
                label=I18N["en"]["label_script"],
                placeholder=I18N["en"]["placeholder_script"]
            )
            chk_suara = gr.Checkbox(label=I18N["en"]["chk_voice"])
            chk_visual = gr.Checkbox(label=I18N["en"]["chk_visual"])
            chk_pihak_ketiga = gr.Checkbox(label=I18N["en"]["chk_third"])
            
            btn_submit = gr.Button(
                I18N["en"]["btn_submit"],
                variant="primary"
            )
        
        # Right Column
        with gr.Column(scale=1, min_width=320, elem_id="results-container"):
            gr.HTML("""
            <div id="results-toolbar">
                <button id="results-fullscreen-btn" type="button" title="Expand Fullscreen">
                    ⛶
                </button>
            </div>
            """)
            
            output_risk_bar = gr.HTML(value=generate_risk_meter_html(0, "en"))
            
            output_radar = gr.Plot(
                value=create_radar_chart(0, 0, 0, 0, "en"),
                label=I18N["en"]["radar_title"]
            )
            
            output_labels = gr.Label(
                value={
                    I18N["en"]["cat_ai"]: 0.0,
                    I18N["en"]["cat_meta"]: 0.0,
                    I18N["en"]["cat_copy"]: 0.0,
                    I18N["en"]["cat_lang"]: 0.0
                },
                label=I18N["en"]["label_breakdown"]
            )
            
            gr.Markdown("---")
            
            output_hasil = gr.Markdown(
                value=I18N["en"]["msg_waiting"],
                elem_id="result-markdown-box"
            )
            
    # Event Language Change
    lang_selector.change(
            fn=change_language,
            inputs=[lang_selector],
            outputs=[
                header_md, policy_status, btn_update, input_video, input_naskah,
                chk_suara, chk_visual, chk_pihak_ketiga, btn_submit,
                output_risk_bar, output_radar, output_labels, output_hasil
            ]
        )
    
    # Event Sync Policy
    btn_update.click(
        fn=update_policy_data,
        inputs=[lang_selector],
        outputs=policy_status
    )
    
    # Event Submit Scan
    btn_submit.click(
        fn=periksa_kepatuhan,
        inputs=[input_video, input_naskah, chk_suara, chk_visual, chk_pihak_ketiga, lang_selector],
        outputs=[output_risk_bar, output_radar, output_labels, output_hasil, btn_submit]
    )

if __name__ == "__main__":
    demo.launch()