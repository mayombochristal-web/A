# =========================================================
# FREE_KOGOSSA — SOCIAL AI NETWORK
# Interface style WhatsApp
# =========================================================

import streamlit as st
import uuid
import time

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Free_Kogossa",
    layout="wide"
)

st.title("🌍 Free_Kogossa")

# =========================================================
# SESSION STATE INIT
# =========================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

if "username" not in st.session_state:
    st.session_state.username = "User_" + st.session_state.user_id

if "tunnels" not in st.session_state:
    st.session_state.tunnels = []

if "messages" not in st.session_state:
    st.session_state.messages = {}

if "posts" not in st.session_state:
    st.session_state.posts = []

# =========================================================
# HEADER
# =========================================================

st.sidebar.title("👤 Profil")

username = st.sidebar.text_input(
    "Nom utilisateur",
    value=st.session_state.username
)

st.session_state.username = username

st.sidebar.write("ID:", st.session_state.user_id)

# =========================================================
# ONGLET PRINCIPAL
# =========================================================

tab_chat, tab_actu, tab_group = st.tabs(
    ["💬 Discussion", "📢 Actu", "🌐 Communautés"]
)

# =========================================================
# DISCUSSION
# =========================================================

with tab_chat:

    st.subheader("💬 Messagerie")

    if len(st.session_state.tunnels) == 0:
        st.info("Aucun tunnel disponible.")
    else:

        tunnel_names = [t["name"] for t in st.session_state.tunnels]

        selected = st.selectbox(
            "Choisir Tunnel",
            tunnel_names
        )

        tunnel = next(t for t in st.session_state.tunnels if t["name"] == selected)

        st.markdown("---")

        st.write("### Tunnel :", tunnel["name"])
        st.write("Créateur :", tunnel["creator"])

        if selected not in st.session_state.messages:
            st.session_state.messages[selected] = []

        for msg in st.session_state.messages[selected]:
            st.chat_message(msg["user"]).write(msg["text"])

        message = st.chat_input("Écrire message")

        if message:

            st.session_state.messages[selected].append({
                "user": st.session_state.username,
                "text": message,
                "time": time.time()
            })

            st.rerun()

# =========================================================
# ACTU
# =========================================================

with tab_actu:

    st.subheader("📢 Actu / Stories")

    type_post = st.selectbox(
        "Type de publication",
        ["Texte", "Photo", "Vidéo", "Audio"]
    )

    text = st.text_area("Message")

    media = st.file_uploader(
        "Ajouter média",
        type=["png", "jpg", "mp4", "mp3"]
    )

    if st.button("Publier"):

        st.session_state.posts.append({
            "user": st.session_state.username,
            "text": text,
            "media": media,
            "type": type_post,
            "time": time.time()
        })

        st.success("Publié")

    st.markdown("---")

    for post in reversed(st.session_state.posts):

        st.write("👤", post["user"])
        st.write(post["text"])

        if post["media"]:

            if post["type"] == "Photo":
                st.image(post["media"])

            elif post["type"] == "Vidéo":
                st.video(post["media"])

            elif post["type"] == "Audio":
                st.audio(post["media"])

        st.markdown("---")

# =========================================================
# COMMUNAUTÉS
# =========================================================

with tab_group:

    st.subheader("🌐 Communautés / Tunnels")

    st.markdown("### Créer Tunnel")

    name = st.text_input("Nom Tunnel")

    if st.button("Créer Tunnel"):

        code = str(uuid.uuid4())[:6]

        tunnel = {
            "name": name,
            "creator": st.session_state.username,
            "code": code,
            "members": [st.session_state.username]
        }

        st.session_state.tunnels.append(tunnel)

        st.success(f"Tunnel créé | Code accès : {code}")

    st.markdown("---")

    st.markdown("### Rejoindre Tunnel")

    join_code = st.text_input("Code Tunnel")

    if st.button("Rejoindre"):

        for tunnel in st.session_state.tunnels:

            if tunnel["code"] == join_code:

                if st.session_state.username not in tunnel["members"]:
                    tunnel["members"].append(st.session_state.username)

                st.success("Tunnel rejoint")
                st.rerun()

    st.markdown("---")

    st.markdown("### Mes Tunnels")

    if len(st.session_state.tunnels) == 0:
        st.write("Aucun tunnel")

    for tunnel in st.session_state.tunnels:

        st.write("🔹", tunnel["name"])
        st.write("Créateur:", tunnel["creator"])
        st.write("Code:", tunnel["code"])

        if st.session_state.username in tunnel["members"]:

            if st.button(
                f"Quitter {tunnel['name']}",
                key=tunnel["code"]
            ):

                tunnel["members"].remove(
                    st.session_state.username
                )

                st.success("Tunnel quitté")
                st.rerun()

        st.markdown("---")