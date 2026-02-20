import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Rugni Debt Manager", layout="wide")

# --- CSS INIEZIONE: DESIGN FLAT E PULITO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    [data-testid="stHeader"] { display: none; }
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #f1f3f4 !important;
    }

    h1 { color: #1a73e8 !important; font-weight: 700 !important; margin-bottom: 5px !important; }
    h3 { color: #3c4043 !important; font-weight: 500 !important; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; margin-top: 30px !important; }

    div.stMetric, .stAlert, [data-testid="stMetric"], div.stNumberInput, div.stSelectbox, div.stSlider {
        background-color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3) !important;
        margin-bottom: 15px !important;
    }

    p, label, span, .stMarkdown p { color: #3c4043 !important; font-weight: 500 !important; }

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

    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #dadce0 !important; }

    .stButton>button {
        background-color: #1a73e8 !important;
        color: white !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        border: none !important;
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

# --- DATABASE ASSET ---
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
acconto_effettivo = 0.0

# LOGICA ACCONTO HIGH FIRST
if tipo_contratto == "High First":
    if debito_tot_orig < 5000: perc_acc = 20
    elif debito_tot_orig <= 10000: perc_acc = 15
    else: perc_acc = 10
    
    acconto_minimo = debito_tot_orig * (perc_acc / 100)
    st.warning(f"⚠️ **Fascia High First ({perc_acc}%):** Acconto minimo richiesto: **{acconto_minimo:,.2f} €**")
    acconto_effettivo = st.number_input("Inserisci importo prima rata (Acconto)", min_value=float(acconto_minimo), value=float(acconto_minimo))
    debito_residuo_da_rateizzare = debito_scontato_tot - acconto_effettivo
else:
    debito_residuo_da_rateizzare = debito_scontato_tot

# SVILUPPO PIANO
if tipo_contratto != "One Shot":
    # Rate Minime
    r_s, r_m = (150, 70) if portfolio != "P2DM" else (90, 35)
    min_t = r_s if num_pratiche == 1 else (r_m * num_pratiche)
    
    st.info(f"💡 Residuo da rateizzare: **{debito_residuo_da_rateizzare:,.2f} €**")
    rata_scelta = st.slider("Rata Mensile (€)", float(min_t), max(min_t+1500, 5000.0), float(min_t))
    
    # SVILUPPO CASCATA
    # Distribuiamo l'acconto proporzionalmente sui debiti per calcolare il residuo di ogni pratica
    deb_residui = []
    for d in lista_debiti_orig:
        valore_scontato = d['valore'] * (1 - sconto_f/100)
        # Sottraiamo la quota parte dell'acconto
        quota_acconto = (d['valore'] / debito_tot_orig) * acconto_effettivo
        deb_residui.append({"id": d['id'], "res": valore_scontato - quota_acconto})
    
    deb_residui = sorted(deb_residui, key=lambda x: x['res'])
    mesi_t = 0
    piani_f = {d['id']: [] for d in deb_residui}
    temp_res = [d['res'] for d in deb_residui]
    
    while sum(temp_res) > 0.1 and mesi_t < 400:
        attive = [v for v in temp_res if v > 0]
        n_a = len(attive)
        r_p = rata_scelta / n_a
        mesi_fase = min(attive) / r_p
        for i in range(len(temp_res)):
            if temp_res[i] > 0:
                piani_f[deb_residui[i]['id']].append({"r": round(mesi_fase), "v": round(r_p, 2)})
                temp_res[i] -= (r_p * m_fase)
        mesi_t += mesi_fase

    st.success(f"📌 Chiusura totale in {round(mesi_t) + (1 if acconto_effettivo > 0 else 0)} mesi")
    col_cards = st.columns(num_pratiche)
    for i, d_info in enumerate(deb_residui):
        with col_cards[i]:
            st.markdown(f"**PRATICA {d_info['id']}**")
            # Se High First, mostra l'acconto
            if acconto_effettivo > 0:
                quota_acc_singola = (lista_debiti_orig[d_info['id']-1]['valore'] / debito_tot_orig) * acconto_effettivo
                st.write(f"🚩 **1** rata da **{quota_acc_singola:.2f}€** (Acconto)")
            
            for step in piani_f[d_info['id']]:
                if step['r'] > 0:
                    st.write(f"🔹 **{step['r']}** rate da **{step['v']}€**")
    
    if (round(mesi_t) + (1 if acconto_effettivo > 0 else 0)) > 160: st.error("❌ LIMITE 160 MESI SUPERATO")
else:
    st.success(f"💰 DA VERSARE IN UNICA SOLUZIONE: **{debito_scontato_tot:,.2f} €**")
