import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- KONFIGURACJA CHMURY SUPABASE (BEZPOŚREDNIA) ---
import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Wczytaj plik (zmień nazwę lub ścieżkę)
load_dotenv(dotenv_path="apikey.env")

# 2. Pobierz zmienne
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 3. Sprawdź czy są
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Błąd: Nie znaleziono kluczy w pliku apikey.env! Sprawdź nazwę pliku.")
    st.stop()

# 4. Inicjalizacja (tylko raz!)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="RunTracker Vault", page_icon="☁️", layout="wide", initial_sidebar_state="collapsed")

# --- HTML/CSS: LEKKIE SZKŁO, POWOLNE PASTELOWE TŁO ---
st.markdown("""
<div class="bokeh-container">
    <div class="flare flare-1"></div>
    <div class="flare flare-2"></div>
    <div class="flare flare-3"></div>
</div>

<style>
    /* Pływające Flary - DUŻE I WOLNE */
    .bokeh-container {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; overflow: hidden; pointer-events: none;
        background: linear-gradient(135deg, #eef2f3 0%, #dcecfc 100%); 
    }
    .flare {
        position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.65;
        mix-blend-mode: multiply;
    }
    
    .flare-1 {
        width: 120vw; height: 120vh; background: #A1C4FD;
        -webkit-animation: move1 20s infinite alternate ease-in-out;
        animation: move1 20s infinite alternate ease-in-out;
    }
    .flare-2 {
        width: 110vw; height: 110vh; background: #FBC2EB;
        -webkit-animation: move2 24s infinite alternate-reverse ease-in-out;
        animation: move2 24s infinite alternate-reverse ease-in-out;
    }
    .flare-3 {
        width: 130vw; height: 130vh; background: #C2E9FB;
        -webkit-animation: move3 18s infinite alternate ease-in-out;
        animation: move3 18s infinite alternate ease-in-out;
    }
    
    @-webkit-keyframes move1 { 0% { top: -30%; left: -30%; } 100% { top: 10%; left: 20%; } }
    @keyframes move1 { 0% { top: -30%; left: -30%; } 100% { top: 10%; left: 20%; } }
    @-webkit-keyframes move2 { 0% { top: 20%; left: -20%; } 100% { top: -20%; left: 30%; } }
    @keyframes move2 { 0% { top: 20%; left: -20%; } 100% { top: -20%; left: 30%; } }
    @-webkit-keyframes move3 { 0% { top: -20%; left: 30%; } 100% { top: 30%; left: -30%; } }
    @keyframes move3 { 0% { top: -20%; left: 30%; } 100% { top: 30%; left: -30%; } }

    .stApp { background: transparent !important; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .main .block-container { animation: fadeIn 0.4s ease-out; z-index: 1; position: relative; padding-top: 2rem !important; }
    
    h1, h2, h3 { color: #2c3e50 !important; font-weight: 800; text-shadow: 1px 1px 3px rgba(255,255,255,0.7); }
    
    /* SZKLANE KAFELKI */
    div[data-testid="metric-container"] { 
        background: rgba(255, 255, 255, 0.45) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
        border-radius: 20px !important; 
        padding: 20px !important; 
        transition: all 0.2s ease;
    }
    div[data-testid="metric-container"]:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 15px 40px 0 rgba(31, 38, 135, 0.12) !important;
    }
    div[data-testid="stMetricLabel"] { color: #4a5a6a !important; font-weight: 600 !important; }
    div[data-testid="stMetricValue"] { color: #1a252f !important; font-weight: 800 !important; }
    
    /* POZIOMA NAWIGACJA */
    div[data-testid="stRadio"] {
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        margin-bottom: 2rem !important;
        width: 100% !important;
    }
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: center !important;
        gap: 15px !important;
        flex-wrap: wrap !important;
    }
    div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.55) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 30px !important;
        padding: 10px 25px !important;
        transition: all 0.2s ease !important;
        cursor: pointer;
        flex-grow: 0 !important; 
        margin-bottom: 5px !important;
    }
    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        transform: translateY(-2px) scale(1.02);
    }
    div[role="radiogroup"] > label[data-checked="true"] {
        background: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        color: #2c3e50 !important;
        font-weight: 800 !important;
    }
    div[role="radiogroup"] > label > div:first-child { display: none; }
    
    /* FORMULARZE */
    .stTextArea textarea, .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        background: rgba(255, 255, 255, 0.55) !important; 
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    /* PRZYCISKI */
    button[data-testid="stBaseButton-secondary"] {
        background: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.9) !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        background: #ffffff !important;
        transform: scale(1.02);
    }

    [data-testid="collapsedControl"] { display: none; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {background: transparent !important;}
</style>
""", unsafe_allow_html=True)

# --- INTELIGENTNY PARSER ---
def parse_garmin_text(text):
    res = {'dist': 0.0, 'dur': '', 'cad': 0}
    cads = []
    podsumowanie_cad = 0
    lines = text.strip().split('\n')
    for line in lines:
        tokens = line.split()
        if not tokens: continue
        if tokens[0].lower() == 'podsumowanie':
            for t in tokens:
                if ':' in t and not res['dur']: res['dur'] = t
            for t in tokens[4:]:
                try:
                    val = float(t.replace(',', '.'))
                    if 0 < val < 500:
                        res['dist'] = val
                        break
                except: pass
            try: podsumowanie_cad = int(tokens[12])
            except: pass
        if 'Bieg' in tokens:
            try:
                idx = tokens.index('Bieg')
                cad = int(tokens[idx + 11])
                if 120 < cad < 250: cads.append(cad)
            except: pass
    if cads: res['cad'] = sum(cads) // len(cads)
    elif podsumowanie_cad > 0: res['cad'] = podsumowanie_cad
    return res

def duration_to_mins(dur_str):
    try:
        parts = str(dur_str).split(':')
        if len(parts) == 3: return int(parts[0])*60 + int(parts[1]) + int(parts[2])/60
        if len(parts) == 2: return int(parts[0]) + int(parts[1])/60
        return 0
    except: return 0

def mins_to_str(total_mins):
    if pd.isna(total_mins): return "0h 0m"
    h = int(total_mins // 60)
    m = int(total_mins % 60)
    return f"{h}h {m}m"

if 'parsed' not in st.session_state:
    st.session_state.parsed = {'dist': 0.0, 'dur': '', 'cad': 0}

# --- NAGŁÓWEK I WYBÓR PROFILU ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>☁️ RunTracker Vault</h1>", unsafe_allow_html=True)

# Centralne okienko do zmiany użytkownika
col_u1, col_u2, col_u3 = st.columns([2, 1, 2])
with col_u2:
    st.markdown("<p style='text-align: center; margin-bottom: 0px; font-weight: bold;'>👤 Zalogowany jako:</p>", unsafe_allow_html=True)
    # Tu wpisz imiona kumpli (np. "Prezes", "Janek", "Tomek")
    current_user = st.selectbox("", ["Bartek", "Alicja"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# --- NAWIGACJA ---
menu = st.radio(
    "", 
    ["📥 Dodaj Trening", "📊 Centrum Analizy (Edycja)", "📋 Podsumowania AI", "🤖 Paczka dla AI"], 
    horizontal=True,
    label_visibility="collapsed"
)

# ==========================================
# MODUŁ 1: DODAWANIE TRENINGU (SUPABASE)
# ==========================================
if menu == "📥 Dodaj Trening":
    st.markdown("<p style='color: #2c3e50; font-weight: bold;'>Wklej surową tabelę ze splitami z Garmina.</p>", unsafe_allow_html=True)
    raw_text = st.text_area("Tabela:", height=120, label_visibility="collapsed")
    
    if st.button("🔍 Autouzupełnij formularz"):
        if raw_text:
            st.session_state.parsed = parse_garmin_text(raw_text)
            st.rerun()
            
    with st.form("save_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            date_input = st.date_input("📅 Data biegu:")
            distance_input = st.number_input("📏 Dystans (km):", value=float(st.session_state.parsed['dist']), step=0.1)
        with col2:
            duration_input = st.text_input("⏱️ Czas (MM:SS):", value=st.session_state.parsed['dur'])
            type_input = st.selectbox("🏃 Typ treningu:", ["Interwały", "Rozbieganie", "Bieg ciągły", "Long Run", "Regeneracja"])
        with col3:
            cadence_input = st.number_input("👟 Śr. Kadencja (spm):", value=int(st.session_state.parsed['cad']), step=1)
            rpe_input = st.slider("📊 Zmęczenie (RPE 1-10):", 1, 10, 5)
            
        notes_input = st.text_area("📝 Uwagi (opcjonalnie):")
        
        if st.form_submit_button("💾 Zapisz do bazy"):
            data = {
                "user_name": current_user,
                "date": str(date_input),
                "distance": distance_input,
                "duration": duration_input,
                "type": type_input,
                "cadence": cadence_input,
                "rpe": rpe_input,
                "notes": notes_input
            }
            supabase.table("runs").insert(data).execute()
            
            st.session_state.parsed = {'dist': 0.0, 'dur': '', 'cad': 0}
            st.success(f"Bieg zabezpieczony w Chmurze dla profilu: {current_user}!")

# ==========================================
# MODUŁ 2: CENTRUM ANALIZY (SUPABASE)
# ==========================================
elif menu == "📊 Centrum Analizy (Edycja)":
    # Odczyt danych z Supabase tylko dla aktywnego profilu
    res = supabase.table("runs").select("*").eq("user_name", current_user).order("date", desc=True).execute()
    df = pd.DataFrame(res.data)
    
    if df.empty:
        df = pd.DataFrame(columns=['id', 'date', 'distance', 'duration', 'type', 'cadence', 'rpe', 'notes'])
        st.info(f"Brak treningów dla profilu: {current_user}.")
    else:
        df['date_obj'] = pd.to_datetime(df['date'], errors='coerce')
        df['Month_Year'] = df['date_obj'].dt.strftime('%Y-%m')
        df['dur_mins'] = df['duration'].apply(duration_to_mins)
        
        now = pd.Timestamp.now()
        valid_months = df['Month_Year'].dropna().unique().tolist()
        months = sorted(valid_months, reverse=True)
        
        filter_opts = ["Cała historia", "Ostatnie 7 dni", "Ostatnie 30 dni"] + [f"Miesiąc: {m}" for m in months]
        selected_filter = st.selectbox("📅 Filtruj dane:", filter_opts)
        
        if selected_filter == "Ostatnie 7 dni":
            df = df[df['date_obj'] >= (now - pd.Timedelta(days=7))]
        elif selected_filter == "Ostatnie 30 dni":
            df = df[df['date_obj'] >= (now - pd.Timedelta(days=30))]
        elif selected_filter.startswith("Miesiąc: "):
            m_str = selected_filter.split(": ")[1]
            df = df[df['Month_Year'] == m_str]
            
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Suma Dystansu", f"{df['distance'].sum():.2f} km")
        col2.metric("Liczba Treningów", len(df))
        col3.metric("Czas W Ruchu", mins_to_str(df['dur_mins'].sum()))
        col4.metric("Średnie RPE", f"{df['rpe'].mean():.1f} / 10" if not df['rpe'].isnull().all() else "Brak")
        
        st.markdown("---")
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("<h3 style='text-align:center;'>🍩 Rozkład Typów Treningów</h3>", unsafe_allow_html=True)
            if not df.empty:
                fig_pie = px.pie(df, names="type", values="distance", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            st.markdown("<h3 style='text-align:center;'>⚡ Trend Zmęczenia (RPE)</h3>", unsafe_allow_html=True)
            if not df.empty:
                df_sorted = df.dropna(subset=['date_obj']).sort_values(by='date_obj')
                fig_rpe = px.line(df_sorted, x="date", y="rpe", markers=True, color_discrete_sequence=['#ff7675'], line_shape='spline')
                fig_rpe.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(range=[0,10.5]))
                st.plotly_chart(fig_rpe, use_container_width=True)

        st.markdown("---")
        st.markdown("<h3 style='text-align:center;'>📋 Edytor Aktywności</h3>", unsafe_allow_html=True)
        edited_df = st.data_editor(
            df[['id', 'date', 'distance', 'duration', 'type', 'cadence', 'rpe', 'notes']],
            column_config={"id": None}, num_rows="dynamic", use_container_width=True, key="data_editor"
        )
        
        if st.button("💾 Zapisz zmiany w Chmurze (Edycja / Usuwanie)"):
            # Kasujemy stare wpisy dla TEGO konkretnego usera
            supabase.table("runs").delete().eq("user_name", current_user).execute()
            
            # Wrzucamy nową, poprawioną tabelę hurtowo
            new_records = []
            for index, row in edited_df.iterrows():
                if pd.notna(row['distance']) and pd.notna(row['date']):
                    new_records.append({
                        "user_name": current_user,
                        "date": row['date'],
                        "distance": row['distance'],
                        "duration": row['duration'],
                        "type": row['type'],
                        "cadence": row['cadence'],
                        "rpe": row['rpe'],
                        "notes": row['notes']
                    })
            if new_records:
                supabase.table("runs").insert(new_records).execute()
            st.success("Zmiany nadpisane w chmurze!")
            st.rerun()

# ==========================================
# MODUŁ 3: PODSUMOWANIA OKRESOWE AI (SUPABASE)
# ==========================================
elif menu == "📋 Podsumowania AI":
    st.title("Kronika Trenerska AI")
    
    with st.form("add_summary_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            summary_type = st.selectbox("📂 Typ podsumowania:", ["Tygodniowe", "Miesięczne"])
        with col_s2:
            summary_period = st.text_input("⏱️ Okres rozliczeniowy:", placeholder="np. Tydzień 24, Maj 2026")
            
        summary_content = st.text_area("🧠 Treść analizy od bota:", height=150, placeholder="Wklej tutaj raport...")
        
        if st.form_submit_button("💾 Zapisz raport w Kronice (Chmura)"):
            if summary_period and summary_content:
                data = {
                    "user_name": current_user,
                    "period": summary_period,
                    "type": summary_type,
                    "content": summary_content
                }
                supabase.table("ai_summaries").insert(data).execute()
                st.success(f"Dodano raport dla {current_user}!")
                st.rerun()
            else:
                st.warning("Uzupełnij okres oraz treść przed zapisem!")

    st.markdown("---")
    
    res_s = supabase.table("ai_summaries").select("*").eq("user_name", current_user).order("id", desc=True).execute()
    df_s = pd.DataFrame(res_s.data)
    
    if not df_s.empty:
        st.subheader("📖 Archiwum Raportów")
        
        view_filter = st.radio("Filtruj kronikę:", ["Wszystkie", "Tygodniowe", "Miesięczne"], horizontal=True)
        df_filtered_s = df_s.copy()
        if view_filter != "Wszystkie":
            df_filtered_s = df_s[df_s['type'] == view_filter]
            
        for _, r in df_filtered_s.iterrows():
            emoji = "📅" if r['type'] == "Tygodniowe" else "🌕"
            with st.expander(f"{emoji} {r['type']} - {r['period']}"):
                st.write(r['content'])
                
        st.markdown("---")
        st.markdown("<h3 style='text-align:center;'>🛠️ Zarządzanie Kroniką (Edycja / Usuwanie)</h3>", unsafe_allow_html=True)
        
        edited_df_s = st.data_editor(
            df_s[['id', 'type', 'period', 'content']],
            column_config={"id": None, "type": "Typ", "period": "Okres", "content": "Treść raportu"},
            num_rows="dynamic", use_container_width=True, key="summary_editor"
        )
        
        if st.button("💾 Nadpisz zmiany w Kronice (Chmura)"):
            supabase.table("ai_summaries").delete().eq("user_name", current_user).execute()
            new_sums = []
            for _, row in edited_df_s.iterrows():
                if pd.notna(row['period']) and pd.notna(row['content']):
                    new_sums.append({
                        "user_name": current_user,
                        "period": row['period'],
                        "type": row['type'],
                        "content": row['content']
                    })
            if new_sums:
                supabase.table("ai_summaries").insert(new_sums).execute()
            st.success("Kronika uaktualniona w chmurze!")
            st.rerun()
    else:
        st.info("Kronika dla tego profilu jest jeszcze pusta.")

# ==========================================
# MODUŁ 4: EKSPORT DO ZEWNĘTRZNEGO AI
# ==========================================
elif menu == "🤖 Paczka dla AI":
    res = supabase.table("runs").select("*").eq("user_name", current_user).order("date", desc=True).execute()
    df = pd.DataFrame(res.data)
    
    if df.empty:
        st.info(f"Brak danych do eksportu dla {current_user}.")
    else:
        df['date_obj'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date_obj'])
        df['Month_Year'] = df['date_obj'].dt.strftime('%Y-%m')
        
        st.markdown("<p style='color: #2c3e50; font-weight: bold; margin-bottom: 5px;'>Sposób wyboru danych:</p>", unsafe_allow_html=True)
        export_mode = st.radio("", ["Ostatnie x treningów", "Z konkretnego miesiąca"], horizontal=True, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_export = df.copy()
        
        if export_mode == "Ostatnie x treningów":
            x_runs = st.number_input("Ile ostatnich treningów pobrać?", min_value=1, max_value=500, value=10, step=1)
            df_export = df.head(x_runs)
        else:
            months = sorted(df['Month_Year'].unique().tolist(), reverse=True)
            sel_m = st.selectbox("Wybierz miesiąc:", months)
            df_export = df[df['Month_Year'] == sel_m]
        
        export_data = df_export[['date', 'type', 'distance', 'duration', 'cadence', 'rpe', 'notes']].to_dict(orient="records")
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        prompt_template = f"""Wciel się w rolę profesjonalnego, bezlitosnego trenera biegowego. Przeanalizuj poniższą paczkę wyników biegacza: {current_user}.
Zwróć uwagę na objętość, proporcje typów treningów i RPE.
Podsumuj, czy robi progres, czy się obija. Wytykaj błędy. Zakończ mocną radą.

Dane:
{json_data}"""

        st.text_area("Gotowy kod do AI (Ctrl+A -> Ctrl+C):", value=prompt_template, height=400)