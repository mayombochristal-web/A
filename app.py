import streamlit as st
import math
import time
import random

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="FREE — KONGOSSA",
    page_icon="⚛️",
    layout="centered"
)

st.title("⚛️ TTU FORGE — Simulation Erbium-Or")
st.caption("Univers TTU minimal incarné par Streamlit")

# =====================================================
# UNIVERS TTU (ETAT GLOBAL)
# =====================================================
if "rho" not in st.session_state:
    st.session_state.rho = 0.2        # densité énergie
    st.session_state.phi = 0.55       # cohérence
    st.session_state.gamma = 1.0      # largeur spectrale
    st.session_state.phase = "Stable"
    st.session_state.tick = 0

# =====================================================
# MODELE TTU (COEUR PHYSIQUE)
# =====================================================

PHI_CRIT = 0.5088      # seuil triadique TTU
FORGE_THRESHOLD = 0.95 # transition Erbium

def ttu_update(rho, tick):
    """
    Dynamique TTU simplifiée :
    - rho injectée par observateur
    - cohérence augmente non-linéairement
    - saturation + courbure lanthanide
    """

    # effet courbure (zone lanthanides)
    K = 25 + 5 * math.sin(tick * 0.2)

    # cohérence informationnelle
    phi = 0.5 + 0.5 * math.tanh(2.5 * (rho - 0.4)) - (K / 200)

    phi = max(0.0, min(1.0, phi))

    # largeur spectrale (rétrécissement)
    gamma = math.exp(-4 * phi)

    # phase TTU
    if phi < PHI_CRIT:
        phase = "Dissolution"
    elif phi < 0.75:
        phase = "Résonance"
    elif phi < FORGE_THRESHOLD:
        phase = "Cohérence Forte"
    else:
        phase = "🔥 FORGE ACTIVE"

    return phi, gamma, phase, K

# =====================================================
# INTERACTION OBSERVATEUR
# =====================================================

st.subheader("⚡ Injection d'Énergie (ρ)")

rho_input = st.slider(
    "Densité d'énergie ρ (J/m³)",
    0.0,
    1.2,
    st.session_state.rho,
    0.01
)

if st.button("Injecter énergie"):
    st.session_state.rho = rho_input

# =====================================================
# EVOLUTION TEMPORELLE TTU
# =====================================================

st.session_state.tick += 1

phi, gamma, phase, K = ttu_update(
    st.session_state.rho,
    st.session_state.tick
)

st.session_state.phi = phi
st.session_state.gamma = gamma
st.session_state.phase = phase

# =====================================================
# OBSERVATION (MESURE)
# =====================================================

col1, col2 = st.columns(2)

with col1:
    st.metric("Φc — Cohérence", f"{phi*100:.2f} %")

    if phi > FORGE_THRESHOLD:
        st.success("Superposition orbitale atteinte")
    elif phi < PHI_CRIT:
        st.error("Rupture triadique")

with col2:
    st.metric("Γ — Largeur spectrale", f"{gamma:.4f} nm")
    st.metric("Courbure K", f"{K:.2f}")

st.divider()

# =====================================================
# VISUALISATION TTU
# =====================================================

st.subheader("📡 État de Phase")

if phase == "🔥 FORGE ACTIVE":
    st.markdown("### 🔥 Forge Erbium-Or ACTIVE")
elif phase == "Résonance":
    st.info("Zone Lanthanide — Cohérence par Courbure")
elif phase == "Dissolution":
    st.warning("Perte de cohérence informationnelle")
else:
    st.write("État stable")

# =====================================================
# BRUIT QUANTIQUE OBSERVATIONNEL
# =====================================================

noise = random.uniform(-0.01, 0.01)
observed_phi = max(0, min(1, phi + noise))

st.progress(observed_phi)

# =====================================================
# TEMPS TTU
# =====================================================

st.caption(f"Tick TTU : {st.session_state.tick}")

time.sleep(1.5)
st.rerun()