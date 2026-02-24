import streamlit as st
import time
import random
from datetime import datetime

# =====================================================
# GEN-Z GABON FREE-KONGOSSA — V24 TTU Anti-Crash
# =====================================================

st.set_page_config(
    page_title="GEN-Z GABON FREE-KONGOSSA",
    layout="wide"
)

# =====================================================
# TTU GLOBAL STATE (ANTI CRASH)
# =====================================================

@st.cache_resource
def global_state():
    return {
        "messages": [],
        "users": set(),
        "rho": 0.1,
        "last_update": time.time(),
        "phi": 10.0,
        "gamma": 0.6,
        "phase": "Dissolution"
    }

STATE = global_state()

# =====================================================
# TTU TIME ENGINE (Δk/k)
# =====================================================

def ttu_update():

    now = time.time()

    # temps discret (anti surcharge)
    if now - STATE["last_update"] < 3:
        return

    STATE["last_update"] = now

    activity = len(STATE["messages"])

    # énergie tunnel
    STATE["rho"] = max(0.05, min(1.0,
        STATE["rho"] + activity*0.0005 - 0.01))

    # cohérence TTU
    STATE["phi"] = STATE["rho"] * 100

    # dispersion spectrale
    STATE["gamma"] = max(0.1, 1 - STATE["rho"])

    # phase dynamique
    if STATE["phi"] > 75:
        STATE["phase"] = "🔥 Forge Active"
    elif STATE["phi"] > 40:
        STATE["phase"] = "Résonance"
    else:
        STATE["phase"] = "Dissolution"


ttu_update()

# =====================================================
# SIDEBAR (PSEUDO + CODE SUR MEME PAGE)
# =====================================================

st.sidebar.title("🌍 GEN-Z GABON")

pseudo = st.sidebar.text_input("Pseudo")
tunnel = st.sidebar.text_input("Code Tunnel")

connect = st.sidebar.button("Entrer dans le tunnel")

if connect and pseudo and tunnel:
    st.session_state["user"] = pseudo
    st.session_state["tunnel"] = tunnel
    STATE["users"].add(pseudo)

# =====================================================
# MAIN UI
# =====================================================

st.title("🔥 FREE-KONGOSSA")

if "user" not in st.session_state:

    st.info("Entre ton pseudo et le code tunnel dans la barre latérale.")

    st.stop()

user = st.session_state["user"]

# =====================================================
# STATISTIQUES TTU (EMULATION SOCIALE)
# =====================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("👥 Utilisateurs", len(STATE["users"]))
col2.metric("Φc Cohérence", f"{STATE['phi']:.1f}%")
col3.metric("Γ Spectrale", f"{STATE['gamma']:.2f}")
col4.metric("Phase", STATE["phase"])

st.divider()

# =====================================================
# CHAT TUNNEL
# =====================================================

message = st.text_input("Parle au tunnel...")

if st.button("Envoyer") and message:

    STATE["messages"].append({
        "user": user,
        "msg": message,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    # limite mémoire anti crash
    if len(STATE["messages"]) > 200:
        STATE["messages"] = STATE["messages"][-200:]

# =====================================================
# AFFICHAGE MESSAGES (léger)
# =====================================================

chat_box = st.container()

with chat_box:

    for m in reversed(STATE["messages"][-30:]):
        st.write(f"**{m['user']}** [{m['time']}] : {m['msg']}")

# =====================================================
# AUTO REFRESH TTU (temps discret)
# =====================================================

time.sleep(2)
st.rerun()