import streamlit as st
import json
import os
import hashlib
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_mic_recorder import mic_recorder

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Free_Kogossa", layout="wide")

DATA_FOLDER = "data"
USERS_FILE = f"{DATA_FOLDER}/users.json"
POSTS_FILE = f"{DATA_FOLDER}/posts.json"
MESSAGES_FILE = f"{DATA_FOLDER}/messages.json"
ASSETS_FOLDER = "assets"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)

# =====================================================
# SÉCURITÉ : HACHAGE DES MOTS DE PASSE
# =====================================================
def hash_password(password):
    """Retourne le hash SHA‑256 du mot de passe."""
    return hashlib.sha256(str.encode(password)).hexdigest()

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
# CHARGEMENT INITIAL DES DONNÉES
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
# LOGIN / REGISTER (AVEC HACHAGE)
# =====================================================
def login():
    st.title("🌍 Free_Kogossa")
    st.info("🔐 Les mots de passe sont désormais hachés. Les anciens comptes ne sont plus valides, veuillez en créer un nouveau.")
    
    tab1, tab2 = st.tabs(["Connexion", "Créer compte"])

    with tab1:
        username = st.text_input("Nom utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            if username in users and users[username]["password"] == hash_password(password):
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
            elif len(new_pass) < 4:
                st.error("Mot de passe trop court (minimum 4 caractères)")
            else:
                pic_path = ""
                if pic:
                    pic_path = f"{DATA_FOLDER}/{new_user}_profile.png"
                    with open(pic_path, "wb") as f:
                        f.write(pic.getbuffer())

                users[new_user] = {
                    "password": hash_password(new_pass),  # Stockage haché
                    "bio": bio,
                    "location": location,
                    "profile_pic": pic_path,
                    "created": str(datetime.now())
                }
                save_json(USERS_FILE, users)
                st.success("Compte créé ! Vous pouvez maintenant vous connecter.")

# =====================================================
# BANNIERE DE PROFIL
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
# FIL SOCIAL (AVEC VIDÉOS ET LIMITATION À 20 POSTS)
# =====================================================
def feed():
    # Auto‑refresh toutes les 5 secondes (moins de charge serveur)
    st_autorefresh(interval=5000, key="feed_refresh")
    banner()
    st.subheader("Exprime toi")

    text = st.text_area("Message")

    col_img, col_vid = st.columns(2)
    with col_img:
        img = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="feed_img")
    with col_vid:
        video = st.file_uploader("Vidéo", type=["mp4", "mov", "avi", "mkv"], key="feed_video")

    if st.button("Publier"):
        post_id = str(len(posts) + 1)
        media_path = ""
        media_type = None

        if img is not None:
            media_path = f"{DATA_FOLDER}/post_{post_id}.png"
            with open(media_path, "wb") as f:
                f.write(img.getbuffer())
            media_type = "image"
        elif video is not None:
            ext = os.path.splitext(video.name)[1]
            media_path = f"{DATA_FOLDER}/post_{post_id}{ext}"
            with open(media_path, "wb") as f:
                f.write(video.getbuffer())
            media_type = "video"

        posts[post_id] = {
            "user": st.session_state.user,
            "text": text,
            "media_path": media_path,
            "media_type": media_type,
            "time": datetime.now().timestamp(),
            "comments": []
        }
        save_json(POSTS_FILE, posts)
        st.rerun()

    st.divider()
    # OPTIMISATION : afficher seulement les 20 derniers posts
    ordered = sorted(posts.items(), key=lambda x: x[1]["time"], reverse=True)[:20]

    for pid, post in ordered:
        with st.container():
            st.subheader(f"@{post['user']}")
            st.write(post["text"])

            media_path = post.get("media_path", "")
            media_type = post.get("media_type")
            if media_path and os.path.exists(media_path):
                if media_type == "image":
                    st.image(media_path)
                elif media_type == "video":
                    st.video(media_path)

            st.caption(datetime.fromtimestamp(post["time"]))

            comment = st.text_input("Commenter", key=f"c{pid}")
            if st.button("Envoyer", key=f"b{pid}"):
                post["comments"].append({"user": st.session_state.user, "text": comment})
                save_json(POSTS_FILE, posts)
                st.rerun()

            for c in post["comments"]:
                st.write(f"**{c['user']}** : {c['text']}")
            st.divider()

# =====================================================
# MESSAGERIE (CORRECTION ENREGISTREMENT VOCAL)
# =====================================================
def messenger():
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

    # Affichage des messages
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
            st.write(prefix + m.get("text", ""))

    st.divider()
    st.subheader("Nouveau message")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        text_msg = st.text_area("Texte", key="msg_text", height=100, label_visibility="collapsed", placeholder="Écris ton message...")
    with col2:
        audio_file = st.file_uploader("🎵 Audio (fichier)", type=["mp3", "wav", "ogg"], key="msg_audio")
    with col3:
        video_file = st.file_uploader("🎬 Vidéo (fichier)", type=["mp4", "mov", "avi"], key="msg_video")
    with col4:
        st.write("🎙️ Enregistrement vocal")
        recorder_output = mic_recorder(
            start_prompt="Démarrer",
            stop_prompt="Arrêter",
            just_once=False,
            key="recorder"
        )

    if st.button("Envoyer message", type="primary"):
        # Extraction des bytes de l'enregistrement
        audio_bytes = None
        if recorder_output is not None:
            if isinstance(recorder_output, dict):
                audio_bytes = recorder_output.get("bytes")
            else:
                audio_bytes = recorder_output

        if audio_bytes is not None:
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
# PROFIL (AVEC MODIFICATION DU MOT DE PASSE)
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

    st.subheader("Modifier les informations")
    new_bio = st.text_area("Bio", value=users[user].get("bio", ""))
    new_loc = st.text_input("Localisation", value=users[user].get("location", ""))
    new_pic = st.file_uploader("Changer photo", type=["png", "jpg", "jpeg"])

    if st.button("Mettre à jour le profil"):
        users[user]["bio"] = new_bio
        users[user]["location"] = new_loc
        if new_pic:
            path = f"{DATA_FOLDER}/{user}_profile.png"
            with open(path, "wb") as f:
                f.write(new_pic.getbuffer())
            users[user]["profile_pic"] = path
        save_json(USERS_FILE, users)
        st.rerun()

    st.divider()
    st.subheader("Sécurité")
    with st.expander("Modifier le mot de passe"):
        old_pass = st.text_input("Ancien mot de passe", type="password")
        new_pass1 = st.text_input("Nouveau mot de passe", type="password")
        new_pass2 = st.text_input("Confirmer le nouveau mot de passe", type="password")

        if st.button("Changer le mot de passe"):
            if users[user]["password"] != hash_password(old_pass):
                st.error("Ancien mot de passe incorrect")
            elif new_pass1 != new_pass2:
                st.error("Les nouveaux mots de passe ne correspondent pas")
            elif len(new_pass1) < 4:
                st.error("Le mot de passe doit contenir au moins 4 caractères")
            else:
                users[user]["password"] = hash_password(new_pass1)
                save_json(USERS_FILE, users)
                st.success("Mot de passe modifié avec succès !")

# =====================================================
# À PROPOS / CRÉATEUR
# =====================================================
def about():
    st.header("👤 Créateur du réseau")
    
    creator_pic = os.path.join(ASSETS_FOLDER, "creator.jpg")
    if os.path.exists(creator_pic):
        st.image(creator_pic, width=200)
    else:
        st.info("Ajoutez une photo dans assets/creator.jpg")

    st.markdown("""
    ### **SCARABBE**  
    *Fondateur de Free_Kogossa*

    Passionné par les technologies de communication et les communautés en ligne, j'ai créé Free_Kogossa pour offrir un espace d'échange libre, respectueux et innovant. Mon objectif est de permettre à chacun de s'exprimer sans contraintes, tout en restant connecté à ses proches.
    """)

    st.divider()
    st.header("🌟 Avantages de Free_Kogossa")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - 🔒 **Confidentialité** : Pas de pistage, pas de publicités ciblées.
        - 🎤 **Messages vocaux & vidéo** : Enregistrez directement depuis l'interface.
        - ⚡ **Temps réel** : Rafraîchissement automatique pour une conversation fluide.
        - 📸 **Partage multimédia** : Images, audio, vidéo dans le fil et en privé.
        """)
    with col2:
        st.markdown("""
        - 🗂️ **Stockage local** : Vos données restent sur votre serveur.
        - 👥 **Communauté libre** : Créez votre réseau sans restrictions.
        - 🔄 **Mises à jour continues** : Le projet évolue avec vos retours.
        - 💬 **Commentaires intégrés** : Interagissez sur les publications.
        """)

    st.divider()
    st.caption("Free_Kogossa – un projet open source et communautaire.")

# =====================================================
# MAIN
# =====================================================
if not st.session_state.user:
    login()
else:
    st.sidebar.title("Free_Kogossa")
    page = st.sidebar.radio(
        "Navigation",
        ["Fil social", "Messagerie", "Profil", "À propos / Créateur"]
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
    elif page == "À propos / Créateur":
        about()