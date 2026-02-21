import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Rugni Debt Manager PRO", layout="wide")

# --- CSS GOOGLE STYLE (CONTRASTO E PULIZIA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    .block-container { padding-top: 1rem !important; }
    [data-testid="stHeader"] { display: none; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8f9fa !important; color: #000000 !important; }
    h1 { color: #1a73e8 !important; font-weight: 800 !important; }
    h2, h3 { color: #000000 !important; font-weight: 700 !important; border-bottom: 2px solid #1a73e8; padding-bottom: 5px; margin-top: 20px !important; }
    p, label, span { color: #000000 !important; font-weight: 600 !important; }
    div[data-testid="stMetric"], .stAlert, div.stNumberInput, div.stSelectbox, div.stSlider {
        background-color: #ffffff !important;
        border: 1px solid #dadce0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(60,64,67,0.3) !important;
    }
    .mobile-hint { background-color: #1a73e8; color: white !important; padding: 12px; border-radius: 8px; text-align: center; font-weight: 700; margin-bottom: 15px; }
    [data-testid="stMetricValue"] { color: #1a73e8 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="mobile-hint">📱 MENU IMPOSTAZIONI: Clicca l\'icona &equiv; in alto a sinistra</div>', unsafe_allow_html=True)
st.title("🛡️ Rugni Debt Management")

# --- SIDEBAR ---
st.sidebar.markdown("### ⚙️ Configurazione")
asset_input = st.sidebar.text_input("Nome Asset", value="FLO/2").upper()
num_pratiche = st.sidebar.number_input("N. Pratiche", min_value=1, value=1)
proc = st.sidebar.selectbox("Tipo Procedura", ["Classic Negotiation", "Behavioral Negotiation"])
scelta_patr = st.sidebar.selectbox("Stato Patrimoniale", ["Negativa", "No Info", "Positiva < 1k", "Positiva 1k-2k", "Positiva > 2k", "Pensionato"])
is_decaduto = st.sidebar.checkbox("Già Decaduto")
pdr_attivo = st.sidebar.checkbox("PdR Attivo")

# --- DATABASE ASSET ---
p2_assets = ["AGSUN/2", "AGS/2", "AGSF/2", "FLO/2", "AFLO/2", "UNIF/1", "UNIF/2", "UNIG", "UCQ/2", "UCQ/3", "DBF/1", "DBF/3", "CMFC/1", "CCRII"]
p3_assets = ["MPS", "FIN/1", "CMP", "CMS", "UCQ/1", "UCQA", "IUB", "EDS", "SRG", "INT", "DBK"]
p2dm_assets = ["ISB", "LOC", "IFIS", "BLF"]

if asset_input in p2_assets: portfolio = "P2"
elif asset_input in p3_assets: portfolio = "P3"
elif asset_input in p2dm_assets: portfolio = "P2DM"
else: portfolio = "P1"

# --- DEBITI ---
st.subheader("📋 Inserimento Debiti")
lista_debiti_orig = []
cols_in = st.columns(num_pratiche)
for i in range(num_pratiche):
    with cols_in[i]:
        v = st.number_input(f"Pratica {i+1} (€)", min_value=0.0, value=2500.0, key=f"d_{i}")
        lista_debiti_orig.append({"id": i+1, "valore": v})
debito_tot_orig = sum(d['valore'] for d in lista_debiti_orig)

# --- SCONTI MAX ---
sc_os, sc_sh, sc_hf, sc_pdr = 0, 0, 0, 0
if portfolio == "P1":
    sc_sh, sc_hf, sc_pdr = 25, 20, (10 if not is_decaduto else 0)
    if "Negativa" in scelta_patr or "Pensionato" in scelta_patr: sc_os = 70 if debito_tot_orig < 10000 else 60
elif portfolio == "P2":
    sc_sh, sc_hf, sc_pdr = 30, 25, (10 if not is_decaduto else 0)
    sc_os = 60 if debito_tot_orig > 10000 else 40
elif portfolio == "P3":
    sc_sh, sc_hf, sc_pdr = 40, 30, (20 if not is_decaduto else 15)
    sc_os = 70 if "Negativa" in scelta_patr else 50
elif portfolio == "P2DM":
    sc_os, sc_sh, sc_hf, sc_pdr = 60, 50, 40, 30
    if is_decaduto: sc_pdr = 15

# --- DASHBOARD ---
st.subheader("📊 Analisi Sconti Max Autorizzati")
m1, m2, m3, m4 = st.columns(4)
m1.metric("One Shot", f"{sc_os}%")
m2.metric("Short Arr", f"{sc_sh}%")
m3.metric("High First", f"{sc_hf}%")
m4.metric("PdR", f"{sc_pdr}%")

# --- ACCORDO ---
st.subheader("🤝 Configurazione Accordo")
c1, c2 = st.columns(2)
with c1:
    tipo_accordo = st.selectbox("Strategia", ["One Shot", "Short Arrangement", "High First", "Piano di Rientro"])
with c2:
    t_max = {"One Shot": sc_os, "Short Arrangement": sc_sh, "High First": sc_hf, "Piano di Rientro": sc_pdr}[tipo_accordo]
    sconto_f = st.number_input(f"Sconto scelto (Max {t_max}%)", 0, int(t_max), 0)

debito_scontato = debito_tot_orig * (1 - sconto_f/100)
st.success(f"💰 **Debito netto da rientrare: {debito_scontato:,.2f} €**")

# --- TOOL RIENTRO LIBERO (VELOCITÀ VARIABILI) ---
st.markdown("### 🛠️ Tool: Piano a Velocità Variabile")
st.write("Usa questo strumento per creare piani con rate di importi differenti.")

col_lib1, col_lib2, col_lib3 = st.columns(3)
with col_lib1:
    n_step1 = st.number_input("Step 1: N. Rate", min_value=0, value=0)
    imp_step1 = st.number_input("Step 1: Importo (€)", min_value=0.0, value=0.0)
with col_lib2:
    n_step2 = st.number_input("Step 2: N. Rate", min_value=0, value=0)
    imp_step2 = st.number_input("Step 2: Importo (€)", min_value=0.0, value=0.0)
with col_lib3:
    imp_finale = st.number_input("Step Finale: Importo Rata (€)", min_value=0.0, value=100.0)

# Calcolo Residuo dopo gli step manuali
pagato_man = (n_step1 * imp_step1) + (n_step2 * imp_step2)
residuo_finale = debito_scontato - pagato_man

if imp_finale > 0:
    rate_finali_necessarie = max(0.0, residuo_finale / imp_finale)
    importo_residuo_visual = max(0.0, residuo_finale)
    
    st.info(f"📉 **Situazione dopo Step 1 e 2:** Residuo € {importo_residuo_visual:,.2f}")
    if residuo_finale > 0:
        st.warning(f"👉 Per chiudere il contratto servono ancora **{int(rate_finali_necessarie) + 1} rate** da **{imp_finale} €**")
        st.write(f"Durata Totale Piano: {int(n_step1 + n_step2 + rate_finali_necessarie) + 1} mesi")
    else:
        st.success("✅ Il debito viene estinto con i primi due step!")

# --- SEZIONE CASCATA STANDARD (Opzionale, rimane sotto) ---
st.markdown("---")
st.subheader("⏳ Simulatore a Cascata Standard (Rata Unica)")
# ... (Qui rimane il codice precedente per la cascata automatica se serve)
