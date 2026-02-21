import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Rugni Debt Manager PRO", layout="wide")

# --- CSS FIX: HEADER TRASPARENTE MA FUNZIONANTE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

    /* 1. RESET: Spazio in alto ridotto ma tasti preservati */
    .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; }
    
    /* Rende l'header invisibile ma lascia i tasti (come la freccia del menu) cliccabili */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: #1a73e8 !important;
    }
    
    html, body, [data-testid="stAppViewContainer"] { background-color: #f8f9fa !important; color: #000000 !important; }

    /* 2. TITOLI E TESTI: Contrasto Massimo */
    h1 { color: #1a73e8 !important; font-weight: 800 !important; margin-bottom: 20px !important; }
    h3 { color: #000000 !important; font-weight: 700 !important; margin-top: 30px !important; border-bottom: 2px solid #1a73e8; padding-bottom: 5px; }
    p, label, span, .stMarkdown p, .stWidgetLabel p { color: #000000 !important; font-weight: 600 !important; }

    /* 3. CARD PULITE */
    div[data-testid="stMetric"], .stAlert, div.stNumberInput, div.stSelectbox, div.stSlider, div[data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        border: 1px solid #dadce0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(60,64,67,0.3) !important;
        margin-bottom: 15px !important;
    }

    /* 4. BANNER MOBILE */
    .mobile-hint { background-color: #1a73e8 !important; color: #ffffff !important; padding: 12px; border-radius: 8px; text-align: center; font-weight: 700; margin-bottom: 20px; }

    /* 5. METRICHE */
    [data-testid="stMetricValue"] { color: #1a73e8 !important; font-weight: 800 !important; font-size: 35px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENUTO APP ---
st.markdown('<div class="mobile-hint">📱 MENU IMPOSTAZIONI: Clicca l\'icona &equiv; o la freccia &gt; in alto a sinistra</div>', unsafe_allow_html=True)
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

portfolio = "P1"
if asset_input in p2_assets: portfolio = "P2"
elif asset_input in p3_assets: portfolio = "P3"
elif asset_input in p2dm_assets: portfolio = "P2DM"

# --- DEBITI ---
st.subheader("📋 Inserimento Debiti")
lista_debiti_orig = []
cols_in = st.columns(num_pratiche)
for i in range(num_pratiche):
    with cols_in[i]:
        v = st.number_input(f"Pratica {i+1} (€)", min_value=0.0, value=2500.0, key=f"d_{i}")
        lista_debiti_orig.append({"id": i+1, "valore": v})
debito_tot_orig = sum(d['valore'] for d in lista_debiti_orig)

# --- RATE MINIME ---
rate_map = {"Negativa": (150, 70), "No Info": (180, 100), "Positiva < 1k": (180, 100), "Positiva 1k-2k": (200, 130), "Positiva > 2k": (250, 180), "Pensionato": (150, 70)}
if portfolio == "P2DM":
    rate_map = {"Negativa": (90, 35), "No Info": (100, 65), "Positiva < 1k": (100, 65), "Positiva 1k-2k": (150, 95), "Positiva > 2k": (200, 140), "Pensionato": (90, 35)}

k_patr = "Negativa" if "Negativa" in scelta_patr or "Pensionato" in scelta_patr else ("No Info" if "No" in scelta_patr else scelta_patr)
r_sing, r_mult = rate_map.get(k_patr, (180, 100))
minima_totale = float(r_sing if num_pratiche == 1 else (r_mult * num_pratiche))

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
st.subheader("📊 Parametri di Riferimento")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("One Shot Max", f"{sc_os}%")
m2.metric("Short Arr Max", f"{sc_sh}%")
m3.metric("High First Max", f"{sc_hf}%")
m4.metric("PdR Max", f"{sc_pdr}%")
m5.metric("Rata Minima", f"{minima_totale}€")

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

# --- TABS ---
tab1, tab2 = st.tabs(["🔄 Piano Standard a Cascata", "⚡ Tool: Velocità Variabile"])

with tab1:
    if tipo_accordo == "One Shot":
        st.success(f"✅ Pagamento One Shot autorizzato: {debito_scontato:,.2f} €")
    else:
        # Number Input per precisione millimetrica
        rata_scelta = st.number_input("Inserisci Rata Mensile Concordata (€)", min_value=minima_totale, value=minima_totale, step=1.0)
        
        acconto_hf = 0.0
        if tipo_accordo == "High First":
            perc_acc = 20 if debito_tot_orig < 5000 else (15 if debito_tot_orig <= 10000 else 10)
            acc_min = debito_tot_orig * (perc_acc / 100)
            st.warning(f"⚠️ Acconto minimo High First: {acc_min:,.2f} €")
            acconto_hf = st.number_input("Importo Acconto", min_value=float(acc_min), value=float(acc_min), key="acc_std")
        
        deb_res_list = []
        for d in lista_debiti_orig:
            scontato = d['valore'] * (1 - sconto_f/100)
            q_acc = (d['valore'] / debito_tot_orig) * acconto_hf
            deb_res_list.append({"id": d['id'], "res": scontato - q_acc})
        
        deb_ordinati = sorted(deb_res_list, key=lambda x: x['res'])
        mesi_t, piani_f, temp_res = 0, {d['id']: [] for d in deb_ordinati}, [d['res'] for d in deb_ordinati]
        
        while sum(temp_res) > 0.01 and mesi_t < 500:
            attive = [v for v in temp_res if v > 0.01]
            if not attive: break
            r_p = rata_scelta / len(attive)
            m_fase = min(attive) / r_p
            for i in range(len(temp_res)):
                if temp_res[i] > 0.01:
                    piani_f[deb_ordinati[i]['id']].append({"r": round(m_fase), "v": round(r_p, 2)})
                    temp_res[i] -= (r_p * m_fase)
            mesi_tot += m_fase # <-- ERRORE FIXATO (era mesi_tot invece di mesi_t)
            mesi_t += 0 # Rimuovere questo, era un refuso di logica

        # Correzione finale ciclo
        mesi_finali = round(sum(p['r'] for p in piani_f[deb_ordinati[-1]['id']]))
        st.success(f"📌 Chiusura totale in {mesi_finali + (1 if acconto_hf > 0 else 0)} mesi")
        
        col_res = st.columns(num_pratiche)
        for i, d_inf in enumerate(deb_ordinati):
            with col_res[i]:
                st.markdown(f"**PRATICA {d_inf['id']}**")
                if acconto_hf > 0:
                    q_a = (lista_debiti_orig[d_inf['id']-1]['valore'] / debito_tot_orig) * acconto_hf
                    st.write(f"🚩 **1** rata da **{q_a:.2f}€**")
                for step in piani_f[d_inf['id']]:
                    if step['r'] > 0: st.write(f"🔹 **{step['r']}** rate da **{step['v']}€**")

with tab2:
    st.markdown("### 🛠️ Simulatore a Velocità Variabile")
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        n1, i1 = st.number_input("Step 1: N. Rate", 0, value=0), st.number_input("Step 1: Importo (€)", 0.0, value=0.0)
    with col_v2:
        n2, i2 = st.number_input("Step 2: N. Rate", 0, value=0), st.number_input("Step 2: Importo (€)", 0.0, value=0.0)
    with col_v3:
        i_f = st.number_input("Step Finale: Importo Rata (€)", 0.0, value=float(minima_totale/num_pratiche))

    pagato_m = (n1 * i1) + (n2 * i2)
    res_v = debito_scontato - pagato_m
    if i_f > 0:
        rate_f = max(0.0, res_v / i_f)
        st.info(f"📉 Residuo: {max(0.0, res_v):,.2f} €")
        if res_v > 0:
            st.warning(f"👉 Mancano ancora **{int(rate_f) + 1} rate** da **{i_f} €**")
