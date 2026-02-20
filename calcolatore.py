import math

def calcola_piano_recupero():
    print("--- CALCOLATORE STRATEGICO RECUPERO CREDITI ---")
    
    # 1. DATABASE ASSET
    p2_assets = ["AGSUN/2", "AGS/2", "AGSF/2", "UNIF/1", "UNIF/2", "DBF/1", "CMFC/1", "UCQ/2", "UCQ/3"] # Esempio (lista accorciata per brevità)
    p3_assets = ["MPS", "FIN/1", "CMP", "CMS", "UCQ/1", "UCQA", "IUB", "EDS", "SRG", "INT", "DBK"]
    p2dm_assets = ["ISB", "LOC", "IFIS", "BLF"]

    # 2. INPUT UTENTE
    asset_input = input("Inserisci nome Asset: ").upper()
    debito_totale = float(input("Inserisci importo debito totale (€): "))
    num_pratiche = int(input("Quante pratiche ha il cliente? "))
    
    print("\nPatrimoniale: 1-Negativa, 2-No Info, 3-Positiva <1k, 4-Positiva 1k-2k, 5-Positiva >2k, 6-Pensionato/Negativa Stabile")
    scelta_patr = input("Scegli (1-6): ")
    
    proc = input("Procedura (C: Classic, B: Behavioral): ").upper()
    is_decaduto = input("Ha già piani scaduti? (S/N): ").upper() == 'S'
    pdr_attivo = input("Ha un PdR attualmente attivo? (S/N): ").upper() == 'S'

    # 3. IDENTIFICAZIONE PORTAFOGLIO
    if asset_input in p2_assets:
        portfolio = "P2"
    elif asset_input in p3_assets:
        portfolio = "P3"
    elif asset_input in p2dm_assets:
        portfolio = "P2DM"
    else:
        portfolio = "P1"

    # 4. LOGICA SCONTI (Esempio semplificato basato sulle tue regole)
    sconto_os = 0
    sconto_pdr = 0
    
    if portfolio == "P1":
        if proc == "C":
            if scelta_patr in ['1', '6']:
                sconto_os = 70 if debito_totale < 10000 else 60
                if pdr_attivo: sconto_os -= 20
                sconto_pdr = 10 if not is_decaduto else 0
        else: # Behavioral
            sconto_os = 30 if debito_totale < 10000 else 50
            sconto_pdr = 10 if not is_decaduto else 0

    elif portfolio == "P3":
        if scelta_patr == '6':
            sconto_os = 70 if not pdr_attivo else 50
        elif scelta_patr in ['1', '2']:
            sconto_os = 60 if not pdr_attivo else 40
        else:
            sconto_os = 50 if not pdr_attivo else 30
        sconto_pdr = 20 if not is_decaduto else 15

    elif portfolio == "P2DM":
        sconto_os = 60
        sconto_pdr = 30 if not is_decaduto else 15

    # 5. CALCOLO RATE MINIME
    if portfolio == "P2DM":
        rate_min = {'1':(90, 35), '2':(100, 65), '3':(100, 65), '4':(150, 95), '5':(200, 140), '6':(90, 35)}
    else:
        rate_min = {'1':(150, 70), '2':(180, 100), '3':(180, 100), '4':(200, 130), '5':(250, 180), '6':(150, 70)}

    r_singola, r_multipla = rate_min.get(scelta_patr, (180, 100))
    minima_da_rispettare = r_singola if num_pratiche == 1 else (r_multipla * num_pratiche)

    # 6. OUTPUT RISULTATI
    print("\n" + "="*30)
    print(f"ANALISI PORTAFOGLIO: {portfolio}")
    print(f"SCONTO MAX ONE SHOT: {sconto_os}% (Saldo: {debito_totale * (1 - sconto_os/100):.2f}€)")
    print(f"SCONTO MAX PdR: {sconto_pdr}%")
    print(f"RATA MINIMA TOTALE RICHIESTA: {minima_da_rispettare}€")
    print("="*30)

    # 7. LOGICA SUDDIVISIONE (Esempio 2 pratiche)
    if num_pratiche > 1:
        rata_proposta = float(input(f"Inserisci rata totale che il cliente può pagare (min {minima_da_rispettare}€): "))
        if rata_proposta < minima_da_rispettare:
            print("ERRORE: Rata inferiore al minimo autorizzato!")
        else:
            rata_per_caso = rata_proposta / num_pratiche
            print(f"\nRIPARTIZIONE: Pagherà {rata_per_caso:.2f}€ per ogni pratica.")
            # Qui si potrebbe espandere con la logica dei mesi esatti

calcola_piano_recupero()