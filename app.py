import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Rugni Debt Manager", layout="wide")

# --- CSS INIEZIONE: DESIGN FLAT E PULITO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    /* 1. RESET TOTALE: Rimuove spazi vuoti in alto e margini inutili */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    [data-testid="stHeader"] {
        display: none;
    }
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #f1f3f4 !important; /* Grigio Google più morbido */
    }

    /* 2. TITOLI PULITI: Niente box, solo testo elegante */
    h1 {
        color: #1a73e8 !important;
        font-weight: 700 !important;
        padding: 0px !important;
        margin-bottom: 5px !important;
    }
    h3 {
        color: #3c4043 !important;
        font-weight: 500 !important;
        border-bottom: 2px solid #1a73e8;
        padding-bottom: 10px;
        margin-top: 30px !important;
    }

    /* 3. DESIGN FLAT: Rimuove i "gradini" e i bordi eccessivi */
    div.stMetric, .stAlert, [data-testid="stMetric"], div.stNumberInput, div.stSelectbox, div.stSlider {
        background-color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3) !important;
        margin-bottom: 15px !important;
    }

    /* 4. FIX TESTO: Forza nero su fondo bianco */
    p, label, span, .stMarkdown p {
        color: #3c4043 !important;
        font-weight: 500 !important;
    }

    /* 5. BANNER MOBILE: Sottile e moderno */
    .mobile-hint {
        background-color: #1a73e8;
        color: white !important;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: 600;
        font-size: 14px;
    }

    /* 6. SIDEBAR: Semplice e chiara */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #dadce0 !important;
    }

    /* 7. BOTTONI GOOGLE */
    .stButton>button {
        background-color: #1a73e8 !important;
        color: white !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BANNER MOBILE ---
st.markdown('<div class="mobile-hint">📱 MENU IMPOSTAZIONI: Clicca l\'icona &equiv; in alto a sinistra</div>', unsafe_allow_html=True)

# --- TITOLO ---
st.title("🛡️ Rugni Debt Management")
st.markdown("##### Portafoglio Asset & Simulatore a Cascata")

# --- SIDEBAR ---
st.sidebar.markdown("### ⚙️ Configurazione")
asset_input = st.sidebar.text_input("Nome Asset", value="FLO/2").upper()
num_pratiche = st.sidebar.number_input("N. Pratiche", min_value=1, value=1)
proc = st.sidebar.selectbox("Tipo Procedura", ["Classic Negotiation", "Behavioral Negotiation"])
scelta_patr = st.sidebar.selectbox("Stato Patrimoniale", ["Negativa", "No Info", "Positiva < 1k", "Positiva 1k-2k", "Positiva > 2k", "Pensionato"])
is_decaduto = st.sidebar.checkbox("Già Decaduto")
pdr_attivo = st.sidebar.checkbox("PdR Attivo")

# --- LOGICA PORTAFOGLIO ---
p2_assets = ["AGSUN/2", "AGS/2", "AGSF/2", "FLO/2", "AFLO/2", "UNIF/1", "UNIF/2", "UNIG", "UCQ/2", "UCQ/3", "DBF/1", "DBF/3", "CMFC/1", "CCRII"]
p3_assets = ["MPS", "FIN/1", "CMP", "CMS", "UCQ/1", "UCQA", "IUB", "EDS", "SRG", "INT", "DBK"]
p2dm_assets = ["ISB", "LOC", "IFIS", "BLF"]

if asset_input in p2_assets: portfolio = "P2"
elif asset_input in p3_assets: portfolio = "P3"
elif asset_input in p2dm_assets: portfolio = "P2DM"
else: portfolio = "P1"

# --- SEZIONE DEBITI ---
st.subheader("📋 Inserimento Debiti")
lista_debiti_orig = []
cols_in = st.columns(num_pratiche)
for i in range(num_pratiche):
    with cols_in[i]:
        v = st.number_input(f"Pratica {i+1} (€)", min_value=0.0, value=2500.0, key=f"d_{i}")
        lista_debiti_orig.append({"id": i+1, "valore": v})

debito_tot_orig = sum(d['valore'] for d in lista_debiti_orig)

# --- CALCOLO SCONTI MASSIMI ---
sc_os, sc_sh, sc_hf, sc_pdr = 0, 0, 0, 0
if portfolio == "P1":
    sc_sh, sc_hf, sc_pdr = 25, 20, (10 if not is_decaduto else 0)
    if "Negativa" in scelta_patr or "Pensionato" in scelta_patr:
        sc_os = 70 if debito_tot_orig < 10000 else 60
elif portfolio == "P2":
    sc_sh, sc_hf, sc_pdr = 30, 25, (10 if not is_decaduto else 0)
    sc_os = 60 if debito_tot_orig > 10000 else 40
elif portfolio == "P3":
    sc_sh, sc_hf, sc_pdr = 40, 30, (20 if not is_decaduto else 15)
    sc_os = 70 if "Negativa" in scelta_patr else 50
elif portfolio == "P2DM":
    sc_os, sc_sh, sc_hf, sc_pdr = 60, 50, 40, 30
    if is_decaduto: sc_pdr = 15

# --- DASHBOARD SCONTI ---
st.subheader("📊 Analisi Sconti Max Autorizzati")
m1, m2, m3, m4 = st.columns(4)
m1.metric("One Shot", f"{sc_os}%")
m2.metric("Short Arr", f"{sc_sh}%")
m3.metric("High First", f"{sc_hf}%")
m4.metric("PdR", f"{sc_pdr}%")

# --- NEGOZIAZIONE ---
st.subheader("🤝 Accordo Negoziale")
c1, c2 = st.columns(2)
with c1:
    tipo_contratto = st.selectbox("Strategia Scelta", ["One Shot", "Short Arrangement", "High First", "Piano di Rientro"])
with c2:
    t_max = {"One Shot": sc_os, "Short Arrangement": sc_sh, "High First": sc_hf, "Piano di Rientro": sc_pdr}[tipo_contratto]
    sconto_f = st.number_input(f"Sconto applicato (Max {t_max}%)", 0, int(t_max), 0)

debito_scontato_tot = debito_tot_orig * (1 - sconto_f/100)

if tipo_contratto != "One Shot":
    r_s, r_m = (150, 70) if portfolio != "P2DM" else (90, 35)
    min_t = r_s if num_pratiche == 1 else (r_m * num_pratiche)
    
    st.info(f"💡 Debito Scontato Totale: **{debito_scontato_tot:,.2f} €**")
    rata_scelta = st.slider("Rata Mensile (€)", float(min_t), max(min_t+1500, 5000.0), float(min_t))
    
    # SVILUPPO CASCATA
    deb_residui = sorted([{"id": d['id'], "res": d['valore']*(1-sconto_f/100)} for d in lista_debiti_orig], key=lambda x: x['res'])
    mesi_t = 0
    piani_f = {d['id']: [] for d in deb_residui}
    temp_res = [d['res'] for d in deb_residui]
    
    while sum(temp_res) > 0.1 and mesi_t < 400:
        attive = [v for v in temp_res if v > 0]
        n_a = len(attive)
        r_p = rata_scelta / n_a
        m_fase = min(attive) / r_p
        for i in range(len(temp_res)):
            if temp_res[i] > 0:
                piani_f[deb_residui[i]['id']].append({"r": round(m_fase), "v": round(r_p, 2)})
                temp_res[i] -= (r_p * m_fase)
        mesi_t += m_fase

    st.success(f"📌 Chiusura totale in {round(mesi_t)} mesi")
    col_cards = st.columns(num_pratiche)
    for i, d_info in enumerate(deb_residui):
        with col_cards[i]:
            st.markdown(f"**PRATICA {d_info['id']}**")
            for step in piani_f[d_info['id']]:
                if step['r'] > 0:
                    st.write(f"🔹 **{step['r']}** rate da **{step['v']}€**")
    
    if mesi_t > 160: st.error("❌ LIMITE 160 MESI SUPERATO")
else:
    st.success(f"💰 DA VERSARE IN UNICA SOLUZIONE: **{debito_scontato_tot:,.2f} €**")
