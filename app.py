# =====================================================
# GEN-Z GABON FREE-KONGOSSA — V27 TTU ULTRA
# Architecture Anti-Crash Streamlit
# =====================================================

import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from PIL import Image

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="GEN-Z GABON FREE-KONGOSSA",
    layout="wide"
)

DATA_FILE = "tunnel_ttu.json"

# ---------------- TTU STORAGE ----------------

def init_db():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"messages": [], "lives": []}, f)

def load_db():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

init_db()

# ---------------- TTU AUTO SYNC ----------------
# rafraîchissement doux (principe Δt TTU)

st_autorefresh(interval=3000, key="ttu_refresh")

# ---------------- SESSION ----------------

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# PAGE LOGIN (SANS SIDEBAR)
# =====================================================

if st.session_state.user is None:

    st.title("🔥 GEN-Z GABON FREE-KONGOSSA")

    pseudo = st.text_input("Pseudo")
    code = st.text_input("Code secret", type="password")

    if st.button("Entrer dans le Tunnel"):
        if pseudo and code:
            st.session_state.user = pseudo
            st.rerun()

    st.stop()

# =====================================================
# APP PRINCIPALE
# =====================================================

db = load_db()

st.title(f"🌍 Tunnel Social — {st.session_state.user}")

tab1, tab2, tab3 = st.tabs(
    ["💬 Messagerie", "📸 Publier", "🔴 Live"]
)

# =====================================================
# 💬 MESSAGERIE FLUIDE TTU
# =====================================================

with tab1:

    st.subheader("Conversation temps réel")

    for msg in db["messages"][-50:]:

        if msg["type"] == "text":
            st.write(f"**{msg['user']}** : {msg['content']}")

        elif msg["type"] == "image":
            st.image(msg["content"], width=250,
                     caption=msg["user"])

        elif msg["type"] == "video":
            st.video(msg["content"])

    st.divider()

    col1, col2 = st.columns([4,1])

    with col1:
        message = st.text_input("Message", key="msg")

    with col2:
        if st.button("Envoyer"):
            if message:
                db["messages"].append({
                    "user": st.session_state.user,
                    "type": "text",
                    "content": message,
                    "time": time.time()
                })
                save_db(db)
                st.rerun()

# =====================================================
# 📸 PUBLICATION PHOTO / VIDEO
# =====================================================

with tab2:

    st.subheader("Publier")

    uploaded = st.file_uploader(
        "Photo ou vidéo",
        type=["png","jpg","jpeg","mp4","mov"]
    )

    if uploaded:

        file_path = f"media_{time.time()}_{uploaded.name}"

        with open(file_path, "wb") as f:
            f.write(uploaded.read())

        if uploaded.type.startswith("image"):
            db["messages"].append({
                "user": st.session_state.user,
                "type": "image",
                "content": file_path,
                "time": time.time()
            })

        else:
            db["messages"].append({
                "user": st.session_state.user,
                "type": "video",
                "content": file_path,
                "time": time.time()
            })

        save_db(db)

        st.success("Publié dans le tunnel ✅")
        st.rerun()

# =====================================================
# 🔴 LIVE TTU STABLE (ANTI CRASH)
# =====================================================

with tab3:

    st.subheader("Live du Tunnel")

    st.info(
        "🎥 Pour un live stable Streamlit Cloud, "
        "utiliser caméra téléphone + upload continu."
    )

    live_video = st.file_uploader(
        "Envoyer une vidéo LIVE",
        type=["mp4","mov"],
        key="live"
    )

    if live_video:

        live_path = f"live_{time.time()}.mp4"

        with open(live_path, "wb") as f:
            f.write(live_video.read())

        db["lives"].append({
            "user": st.session_state.user,
            "video": live_path,
            "time": time.time()
        })

        save_db(db)
        st.success("🔴 LIVE lancé")

    st.divider()

    st.subheader("Lives actifs")

    for live in reversed(db["lives"][-5:]):
        st.write(f"🔴 {live['user']} en direct")
        st.video(live["video"])

# =====================================================
# FOOTER TTU
# =====================================================

st.caption("TTU-MC³ Stream Architecture — Anti Crash Mode")