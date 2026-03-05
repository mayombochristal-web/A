import streamlit as st
import json
import os
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="Free_Kogossa", layout="wide")

DATA_FOLDER = "data"
USERS_FILE = f"{DATA_FOLDER}/users.json"
POSTS_FILE = f"{DATA_FOLDER}/posts.json"
MESSAGES_FILE = f"{DATA_FOLDER}/messages.json"

os.makedirs(DATA_FOLDER, exist_ok=True)

# =====================================================
# IMPORTS POUR AUTO-REFRESH ET AUDIO RECORDER
# =====================================================
# Nécessite : pip install streamlit-autorefresh streamlit-audio-recorder
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Veuillez installer streamlit-autorefresh : pip install streamlit-autorefresh")
    st.stop()

try:
    from streamlit_audio_recorder import audio_recorder
except ImportError:
    st.error("Veuillez installer streamlit-audio-recorder : pip install streamlit-audio-recorder")
    st.stop()

# =====================================================
# JSON UTILS
# =====================================================

def load_json(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =====================================================
# LOAD DATA
# =====================================================

users = load_json(USERS_FILE)
posts = load_json(POSTS_FILE)
messages = load_json(MESSAGES_FILE)

# =====================================================
# SESSION
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# LOGIN / REGISTER
# =====================================================

def login():
    st.title("🌍 Free_Kogossa")

    tab1, tab2 = st.tabs(["Connexion", "Créer compte"])

    with tab1:
        username = st.text_input("Nom utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Identifiants incorrects")

    with tab2:
        new_user = st.text_input("Nom utilisateur", key="newuser")
        new_pass = st.text_input("Mot de passe", type="password", key="newpass")
        bio = st.text_area("Bio")
        location = st.text_input("Localisation")
        pic = st.file_uploader("Photo profil", type=["png", "jpg", "jpeg"])

        if st.button("Créer compte"):
            if new_user in users:
                st.error("Utilisateur existe déjà")
            else:
                pic_path = ""
                if pic:
                    pic_path = f"{DATA_FOLDER}/{new_user}_profile.png"
                    with open(pic_path, "wb") as f:
                        f.write(pic.getbuffer())

                users[new_user] = {
                    "password": new_pass,
                    "bio": bio,
                    "location": location,
                    "profile_pic": pic_path,
                    "created": str(datetime.now())
                }
                save_json(USERS_FILE, users)
                st.success("Compte créé")

# =====================================================
# PROFILE BANNER
# =====================================================

def banner():
    user = st.session_state.user
    st.divider()
    col1, col2 = st.columns([1, 4])

    with col1:
        pic = users[user].get("profile_pic", "")
        if pic and os.path.exists(pic):
            st.image(pic, width=120)

    with col2:
        st.title(user)
        if users[user].get("bio"):
            st.write(users[user]["bio"])
        if users[user].get("location"):
            st.caption("📍 " + users[user]["location"])

    st.divider()

# =====================================================
# SOCIAL FEED (avec auto-refresh)
# =====================================================

def feed():
    # Auto-refresh toutes les 3 secondes
    st_autorefresh(interval=3000, key="feed_refresh")

    banner()
    st.subheader("Exprime toi")

    text = st.text_area("Message")
    img = st.file_uploader("Image", type=["png", "jpg", "jpeg"])

    if st.button("Publier"):
        post_id = str(len(posts) + 1)
        img_path = ""

        if img:
            img_path = f"{DATA_FOLDER}/post_{post_id}.png"
            with open(img_path, "wb") as f:
                f.write(img.getbuffer())

        posts[post_id] = {
            "user": st.session_state.user,
            "text": text,
            "image": img_path,
            "time": datetime.now().timestamp(),
            "comments": []
        }
        save_json(POSTS_FILE, posts)
        st.rerun()

    st.divider()

    ordered = sorted(posts.items(), key=lambda x: x[1]["time"], reverse=True)

    for pid, post in ordered:
        st.subheader(post["user"])
        st.write(post["text"])

        if post["image"] and os.path.exists(post["image"]):
            st.image(post["image"])

        st.caption(datetime.fromtimestamp(post["time"]))

        comment = st.text_input("Commenter", key=f"c{pid}")
        if st.button("Envoyer", key=f"b{pid}"):
            post["comments"].append({
                "user": st.session_state.user,
                "text": comment
            })
            save_json(POSTS_FILE, posts)
            st.rerun()

        for c in post["comments"]:
            st.write(f"**{c['user']}** : {c['text']}")

        st.divider()

# =====================================================
# MESSENGER (auto-refresh + enregistrement vocal)
# =====================================================

def messenger():
    # Auto-refresh toutes les 2 secondes
    st_autorefresh(interval=2000, key="msg_refresh")

    st.header("Messagerie")

    users_list = [u for u in users if u != st.session_state.user]

    if not users_list:
        st.info("Aucun autre utilisateur")
        return

    target = st.selectbox("Choisir utilisateur", users_list, key="msg_target")
    conv_id = "_".join(sorted([st.session_state.user, target]))

    if conv_id not in messages:
        messages[conv_id] = []

    # Afficher les messages existants
    ordered = sorted(messages[conv_id], key=lambda x: x["time"])

    for m in ordered:
        if m["sender"] == st.session_state.user:
            prefix = "🟢 **Moi** : "
        else:
            prefix = f"🔵 **{m['sender']}** : "

        if "audio_path" in m and os.path.exists(m["audio_path"]):
            st.write(prefix + "[Message audio]")
            st.audio(m["audio_path"])
        elif "video_path" in m and os.path.exists(m["video_path"]):
            st.write(prefix + "[Message vidéo]")
            st.video(m["video_path"])
        else:
            # message texte
            st.write(prefix + m.get("text", ""))

    st.divider()

    # Saisie d'un nouveau message
    st.subheader("Nouveau message")

    # Utilisation de colonnes pour disposer les différents types d'envoi
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        text_msg = st.text_area("Texte", key="msg_text", height=100, label_visibility="collapsed", placeholder="Écris ton message...")

    with col2:
        audio_file = st.file_uploader(
            "🎵 Audio (fichier)", type=["mp3", "wav", "ogg"], key="msg_audio"
        )

    with col3:
        video_file = st.file_uploader(
            "🎬 Vidéo (fichier)", type=["mp4", "mov", "avi"], key="msg_video"
        )

    with col4:
        st.write("🎙️ Enregistrement vocal")
        audio_bytes = mic_recorder(
    start_prompt="🎙️ Démarrer l'enregistrement",
    stop_prompt="⏹️ Arrêter",
    just_once=False,
    key="recorder"
)

    # Bouton d'envoi unique (gère tous les types)
    if st.button("Envoyer message", type="primary"):
        # 1. Vérifier s'il y a un enregistrement vocal
        if audio_bytes is not None:
            # Sauvegarder l'audio enregistré
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"{DATA_FOLDER}/voice_{st.session_state.user}_{timestamp}.wav"
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)

            messages[conv_id].append({
                "sender": st.session_state.user,
                "audio_path": audio_path,
                "time": datetime.now().timestamp()
            })
            save_json(MESSAGES_FILE, messages)
            st.rerun()

        # 2. Sinon, vérifier l'upload audio
        elif audio_file is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"{DATA_FOLDER}/audio_{st.session_state.user}_{timestamp}.audio"
            with open(audio_path, "wb") as f:
                f.write(audio_file.getbuffer())

            messages[conv_id].append({
                "sender": st.session_state.user,
                "audio_path": audio_path,
                "time": datetime.now().timestamp()
            })
            save_json(MESSAGES_FILE, messages)
            st.rerun()

        # 3. Sinon, vérifier l'upload vidéo
        elif video_file is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = f"{DATA_FOLDER}/video_{st.session_state.user}_{timestamp}.video"
            with open(video_path, "wb") as f:
                f.write(video_file.getbuffer())

            messages[conv_id].append({
                "sender": st.session_state.user,
                "video_path": video_path,
                "time": datetime.now().timestamp()
            })
            save_json(MESSAGES_FILE, messages)
            st.rerun()

        # 4. Sinon, message texte
        elif text_msg.strip() != "":
            messages[conv_id].append({
                "sender": st.session_state.user,
                "text": text_msg,
                "time": datetime.now().timestamp()
            })
            save_json(MESSAGES_FILE, messages)
            st.rerun()

        else:
            st.warning("Écris un message, enregistre un audio ou ajoute un fichier.")

# =====================================================
# PROFILE
# =====================================================

def profile():
    user = st.session_state.user
    st.header("Profil")

    pic = users[user].get("profile_pic", "")
    if pic and os.path.exists(pic):
        st.image(pic, width=150)

    st.write("Bio :", users[user].get("bio", ""))
    st.write("Localisation :", users[user].get("location", ""))
    st.caption("Compte créé : " + users[user]["created"])

    st.subheader("Modifier")

    new_bio = st.text_area("Bio", value=users[user].get("bio", ""))
    new_loc = st.text_input("Localisation", value=users[user].get("location", ""))
    new_pic = st.file_uploader("Changer photo", type=["png", "jpg", "jpeg"])

    if st.button("Mettre à jour profil"):
        users[user]["bio"] = new_bio
        users[user]["location"] = new_loc

        if new_pic:
            path = f"{DATA_FOLDER}/{user}_profile.png"
            with open(path, "wb") as f:
                f.write(new_pic.getbuffer())
            users[user]["profile_pic"] = path

        save_json(USERS_FILE, users)
        st.rerun()

# =====================================================
# MAIN
# =====================================================

if not st.session_state.user:
    login()
else:
    st.sidebar.title("Free_Kogossa")
    page = st.sidebar.radio(
        "Navigation",
        ["Fil social", "Messagerie", "Profil"]
    )

    if st.sidebar.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

    if page == "Fil social":
        feed()
    elif page == "Messagerie":
        messenger()
    elif page == "Profil":
        profile()