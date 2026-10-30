import json
import ssl
import urllib.request
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Parametri Sismici NTC 2018", page_icon="🌍", layout="centered"
)

st.title("🌍 Parametri Sismici e $a_{gmax}$ (NTC 2018)")
st.write(
    "Inserisci le coordinate geografiche e i coefficienti stratigrafici per"
    " calcolare i parametri sismici e generare il link di geolocalizzazione."
)


# --- SEZIONE INPUT UTENTE (Sidebar / Pannello Mobile) ---
st.sidebar.header("📍 Dati di Input Geografici & Sismici")

lat_input = st.sidebar.number_input(
    "Latitudine decimale",
    min_value=35.0,
    max_value=48.0,
    value=38.19,
    step=0.0001,
    format="%.4f",
)
lon_input = st.sidebar.number_input(
    "Longitudine decimale",
    min_value=6.0,
    max_value=19.0,
    value=15.55,
    step=0.0001,
    format="%.4f",
)

ss_input = st.sidebar.number_input(
    "Coefficiente stratigrafico $S_s$",
    min_value=1.0,
    max_value=2.0,
    value=1.2,
    step=0.05,
)
st_input = st.sidebar.number_input(
    "Coefficiente topografico $S_t$",
    min_value=1.0,
    max_value=1.4,
    value=1.0,
    step=0.05,
)


# --- FUNZIONI DI CALCOLO ---
def decimale_a_dms(gradi_decimali, tipo="lat"):
  ass = abs(gradi_decimali)
  gradi = int(ass)
  primi_float = (ass - gradi) * 60
  primi = int(primi_float)
  secondi = (primi_float - primi) * 60
  if tipo == "lat":
    direzione = "N" if gradi_decimali >= 0 else "S"
  else:
    direzione = "E" if gradi_decimali >= 0 else "W"
  return f"{gradi}°{primi}'{secondi:.1f}\"{direzione}"


def ottieni_localita_e_mappa(lat, lon):
  url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE

  nome_localita = "Località non identificata"
  try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
      dati = json.loads(response.read().decode("utf-8"))
      if "display_name" in dati:
        nome_localita = dati["display_name"]
  except Exception:
    pass

  link_google_maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
  return nome_localita, link_google_maps


# --- ESECUZIONE DEL CALCOLO ---
if st.button("🚀 Calcola Parametri Sismici", type="primary"):
  nome_localita, link_mappa = ottieni_localita_e_mappa(lat_input, lon_input)
  lat_dms = decimale_a_dms(lat_input, "lat")
  lon_dms = decimale_a_dms(lon_input, "lon")

  st.success("Calcolo eseguito con successo!")

  # Informazioni Geografiche
  st.subheader("📌 Informazioni Geografiche")
  st.markdown(f"**Località:** {nome_localita}")
  st.markdown(
      f"**Coordinate:** Lat {lat_input:.4f}, Lon {lon_input:.4f} ({lat_dms}"
      f" {lon_dms})"
  )
  st.markdown(f"[🗺️ Apri la posizione su Google Maps]({link_mappa})")

  # Mappatura Stati Limite NTC 2018
  stati_limite = {
      30: "SLO (Operatività)",
      50: "SLD (Danno)",
      475: "SLV (Vita)",
      2475: "SLC (Crollo)",
  }

  griglia = [
      {
          "lat": 38.15,
          "lon": 15.50,
          "data": {
              30: (0.0570, 2.45, 0.252),
              50: (0.0763, 2.44, 0.270),
              475: (0.2062, 2.46, 0.339),
              2475: (0.4351, 2.41, 0.384),
          },
      },
      {
          "lat": 38.15,
          "lon": 15.60,
          "data": {
              30: (0.0581, 2.45, 0.254),
              50: (0.0779, 2.44, 0.272),
              475: (0.2105, 2.46, 0.341),
              2475: (0.4421, 2.41, 0.386),
          },
      },
      {
          "lat": 38.20,
          "lon": 15.50,
          "data": {
              30: (0.0575, 2.45, 0.253),
              50: (0.0771, 2.44, 0.271),
              475: (0.2088, 2.46, 0.340),
              2475: (0.4388, 2.41, 0.385),
          },
      },
      {
          "lat": 38.20,
          "lon": 15.60,
          "data": {
              30: (0.0588, 2.45, 0.255),
              50: (0.0788, 2.44, 0.273),
              475: (0.2132, 2.46, 0.342),
              2475: (0.4462, 2.41, 0.387),
          },
      },
  ]

  p00 = griglia[0]
  p11 = griglia[3]
  t = (lat_input - p00["lat"]) / (p11["lat"] - p00["lat"])
  u = (lon_input - p00["lon"]) / (p11["lon"] - p00["lon"])

  risultati = []
  s_tot = ss_input * st_input

  for tr, stato in stati_limite.items():
    v00 = p00["data"][tr]
    v01 = griglia[1]["data"][tr]
    v10 = griglia[2]["data"][tr]
    v11 = p11["data"][tr]

    ag = (
        (1 - t) * (1 - u) * v00[0]
        + t * (1 - u) * v10[0]
        + (1 - t) * u * v01[0]
        + t * u * v11[0]
    )
    f0 = (
        (1 - t) * (1 - u) * v00[1]
        + t * (1 - u) * v10[1]
        + (1 - t) * u * v01[1]
        + t * u * v11[1]
    )
    tc = (
        (1 - t) * (1 - u) * v00[2]
        + t * (1 - u) * v10[2]
        + (1 - t) * u * v01[2]
        + t * u * v11[2]
    )

    agmax_g = ag * s_tot
    agmax_ms2 = agmax_g * 9.81

    risultati.append({
        "Stato Limite": stato,
        "TR [anni]": tr,
        "ag [g]": round(ag, 4),
        "F0 [-]": round(f0, 3),
        "Tc* [s]": round(tc, 3),
        "agmax [g]": round(agmax_g, 4),
        "agmax [m/s²]": round(agmax_ms2, 3),
    })

  import pandas as pd

  df = pd.DataFrame(risultati)

  st.subheader("📊 Tabella Risultati Sismici & agmax")
  st.dataframe(df, use_container_width=True)