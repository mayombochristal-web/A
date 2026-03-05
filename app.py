import streamlit as st
import os
import hashlib
from datetime import datetime
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
from streamlit_mic_recorder import mic_recorder

# =====================================================
# CONFIG & CONNEXION SUPABASE
# =====================================================
st.set_page_config(page_title="Free_Kogossa", layout="wide")

# Récupération des secrets (à configurer dans Streamlit Cloud / secrets.toml local)
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

DATA_FOLDER = "data"
ASSETS_FOLDER = "assets"
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)

# =====================================================
# SÉCURITÉ : HACHAGE DES MOTS DE PASSE
# =====================================================
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# =====================================================
# SESSION
# =====================================================
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# LOGIN / REGISTER (AVEC SUPABASE)
# =====================================================
def login():
    st.title("🌍 Free_Kogossa x GEN-Z GABON")
    st.info("🔐 Connexion Cloud – vos données sont sécurisées.")

    tab1, tab2 = st.tabs(["Connexion", "Créer compte"])

    with tab1:
        username = st.text_input("Nom utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            response = supabase.table("profiles").select("*").eq("username", username).execute()
            if response.data:
                user_data = response.data[0]
                if user_data["password"] == hash_password(password):
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")
            else:
                st.error("Utilisateur non trouvé")

    with tab2:
        new_user = st.text_input("Nom utilisateur", key="newuser")
        new_pass = st.text_input("Mot de passe", type="password", key="newpass")
        bio = st.text_area("Bio")
        location = st.text_input("Localisation")
        pic = st.file_uploader("Photo profil", type=["png", "jpg", "jpeg"])

        if st.button("Créer compte"):
            # Vérifier si l'utilisateur existe déjà
            check = supabase.table("profiles").select("username").eq("username", new_user).execute()
            if check.data:
                st.error("Ce pseudo est déjà pris")
            elif len(new_pass) < 4:
                st.error("Mot de passe trop court (minimum 4 caractères)")
            else:
                # Sauvegarde de l'image localement (optionnel)
                pic_path = ""
                if pic:
                    pic_path = f"{DATA_FOLDER}/{new_user}_profile.png"
                    with open(pic_path, "wb") as f:
                        f.write(pic.getbuffer())

                # Insertion dans Supabase
                user_dict = {
                    "username": new_user,
                    "password": hash_password(new_pass),
                    "bio": bio,
                    "location": location,
                    "profile_pic": pic_path,
                }
                supabase.table("profiles").insert(user_dict).execute()
                st.success("Compte créé sur le Cloud ! Vous pouvez maintenant vous connecter.")

# =====================================================
# BANNIERE DE PROFIL (depuis Supabase)
# =====================================================
def banner():
    user = st.session_state.user
    # Récupérer les infos du profil depuis Supabase
    response = supabase.table("profiles").select("*").eq("username", user).execute()
    if response.data:
        profile = response.data[0]
    else:
        st.error("Profil introuvable")
        return

    st.divider()
    col1, col2 = st.columns([1, 4])

    with col1:
        pic = profile.get("profile_pic", "")
        if pic and os.path.exists(pic):
            st.image(pic, width=120)

    with col2:
        st.title(user)
        if profile.get("bio"):
            st.write(profile["bio"])
        if profile.get("location"):
            st.caption("📍 " + profile["location"])

    st.divider()

# =====================================================
# FIL SOCIAL (AVEC SUPABASE)
# =====================================================
def feed():
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
        media_path = ""
        media_type = None

        if img is not None:
            # Générer un nom unique (on utilise un timestamp)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            media_path = f"{DATA_FOLDER}/post_img_{st.session_state.user}_{timestamp}.png"
            with open(media_path, "wb") as f:
                f.write(img.getbuffer())
            media_type = "image"
        elif video is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(video.name)[1]
            media_path = f"{DATA_FOLDER}/post_vid_{st.session_state.user}_{timestamp}{ext}"
            with open(media_path, "wb") as f:
                f.write(video.getbuffer())
            media_type = "video"

        # Insertion du post dans Supabase
        post_dict = {
            "username": st.session_state.user,
            "text": text,
            "media_path": media_path,
            "media_type": media_type,
        }
        supabase.table("posts").insert(post_dict).execute()
        st.rerun()

    st.divider()

    # Récupération des 20 derniers posts avec leurs commentaires
    # On joint les commentaires ? Pour simplifier, on récupère les posts puis on charge les commentaires séparément.
    posts_response = supabase.table("posts").select("*").order("created_at", desc=True).limit(20).execute()
    posts_list = posts_response.data if posts_response.data else []

    for post in posts_list:
        with st.container():
            st.subheader(f"@{post['username']}")
            st.write(post.get("text", ""))

            media_path = post.get("media_path", "")
            media_type = post.get("media_type")
            if media_path and os.path.exists(media_path):
                if media_type == "image":
                    st.image(media_path)
                elif media_type == "video":
                    st.video(media_path)

            # Formatage de la date
            created_at = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
            st.caption(created_at.strftime("%Y-%m-%d %H:%M"))

            # Récupération des commentaires pour ce post
            comments_response = supabase.table("comments").select("*").eq("post_id", post["id"]).order("created_at").execute()
            comments = comments_response.data if comments_response.data else []

            # Zone de commentaire
            comment_key = f"c_{post['id']}"
            comment_text = st.text_input("Commenter", key=comment_key)
            if st.button("Envoyer", key=f"b_{post['id']}"):
                if comment_text.strip():
                    comment_dict = {
                        "post_id": post["id"],
                        "username": st.session_state.user,
                        "text": comment_text,
                    }
                    supabase.table("comments").insert(comment_dict).execute()
                    st.rerun()

            # Affichage des commentaires existants
            for c in comments:
                st.write(f"**{c['username']}** : {c['text']}")
            st.divider()

# =====================================================
# MESSAGERIE (AVEC SUPABASE)
# =====================================================
def messenger():
    st_autorefresh(interval=2000, key="msg_refresh")
    st.header("Messagerie")

    # Récupération de la liste des autres utilisateurs
    users_response = supabase.table("profiles").select("username").neq("username", st.session_state.user).execute()
    users_list = [u["username"] for u in users_response.data] if users_response.data else []

    if not users_list:
        st.info("Aucun autre utilisateur")
        return

    target = st.selectbox("Choisir utilisateur", users_list, key="msg_target")

    # Récupération des messages entre l'utilisateur courant et le target
    # On utilise un filtre OR : (sender=user & recipient=target) OR (sender=target & recipient=user)
    from_user = st.session_state.user
    messages_response = supabase.table("messages").select("*")\
        .or_(f"sender.eq.{from_user},recipient.eq.{from_user}")\
        .or_(f"sender.eq.{target},recipient.eq.{target}")\
        .order("created_at").execute()
    # Note: cette double condition n'est pas idéale, on peut utiliser une condition plus complexe.
    # Mieux : on récupère tous les messages où (sender=from_user et recipient=target) ou (sender=target et recipient=from_user)
    # Avec Supabase, on peut faire :
    # .or_("and(sender.eq.from_user,recipient.eq.target),and(sender.eq.target,recipient.eq.from_user)")
    # Mais pour simplifier, on va filtrer en python après récupération.
    # On récupère un peu plus large puis on filtre.
    # Alternative: on utilise une fonction RPC, mais on reste simple ici.
    all_msgs = messages_response.data if messages_response.data else []
    # Filtrer pour ne garder que les échanges entre les deux
    filtered_msgs = [
        m for m in all_msgs
        if (m["sender"] == from_user and m["recipient"] == target) or
           (m["sender"] == target and m["recipient"] == from_user)
    ]
    # Trier par date (déjà fait par la requête, mais on refiltre, donc on trie)
    filtered_msgs.sort(key=lambda x: x["created_at"])

    for m in filtered_msgs:
        if m["sender"] == st.session_state.user:
            prefix = "🟢 **Moi** : "
        else:
            prefix = f"🔵 **{m['sender']}** : "

        if m.get("audio_path") and os.path.exists(m["audio_path"]):
            st.write(prefix + "[Message audio]")
            st.audio(m["audio_path"])
        elif m.get("video_path") and os.path.exists(m["video_path"]):
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

        message_dict = {
            "sender": st.session_state.user,
            "recipient": target,
        }

        if audio_bytes is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"{DATA_FOLDER}/voice_{st.session_state.user}_{timestamp}.wav"
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            message_dict["audio_path"] = audio_path
        elif audio_file is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"{DATA_FOLDER}/audio_{st.session_state.user}_{timestamp}.audio"
            with open(audio_path, "wb") as f:
                f.write(audio_file.getbuffer())
            message_dict["audio_path"] = audio_path
        elif video_file is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = f"{DATA_FOLDER}/video_{st.session_state.user}_{timestamp}.video"
            with open(video_path, "wb") as f:
                f.write(video_file.getbuffer())
            message_dict["video_path"] = video_path
        elif text_msg.strip() != "":
            message_dict["text"] = text_msg
        else:
            st.warning("Écris un message, enregistre un audio ou ajoute un fichier.")
            st.stop()

        # Insertion du message dans Supabase
        supabase.table("messages").insert(message_dict).execute()
        st.rerun()

# =====================================================
# PROFIL (AVEC SUPABASE)
# =====================================================
def profile():
    user = st.session_state.user
    st.header("Profil")

    # Récupérer les infos actuelles
    response = supabase.table("profiles").select("*").eq("username", user).execute()
    if not response.data:
        st.error("Profil introuvable")
        return
    profile_data = response.data[0]

    pic = profile_data.get("profile_pic", "")
    if pic and os.path.exists(pic):
        st.image(pic, width=150)

    st.write("Bio :", profile_data.get("bio", ""))
    st.write("Localisation :", profile_data.get("location", ""))
    st.caption("Compte créé : " + profile_data.get("created_at", ""))

    st.subheader("Modifier les informations")
    new_bio = st.text_area("Bio", value=profile_data.get("bio", ""))
    new_loc = st.text_input("Localisation", value=profile_data.get("location", ""))
    new_pic = st.file_uploader("Changer photo", type=["png", "jpg", "jpeg"])

    if st.button("Mettre à jour le profil"):
        update_dict = {}
        if new_bio != profile_data.get("bio"):
            update_dict["bio"] = new_bio
        if new_loc != profile_data.get("location"):
            update_dict["location"] = new_loc
        if new_pic:
            path = f"{DATA_FOLDER}/{user}_profile.png"
            with open(path, "wb") as f:
                f.write(new_pic.getbuffer())
            update_dict["profile_pic"] = path

        if update_dict:
            supabase.table("profiles").update(update_dict).eq("username", user).execute()
            st.rerun()

    st.divider()
    st.subheader("Sécurité")
    with st.expander("Modifier le mot de passe"):
        old_pass = st.text_input("Ancien mot de passe", type="password")
        new_pass1 = st.text_input("Nouveau mot de passe", type="password")
        new_pass2 = st.text_input("Confirmer le nouveau mot de passe", type="password")

        if st.button("Changer le mot de passe"):
            if profile_data["password"] != hash_password(old_pass):
                st.error("Ancien mot de passe incorrect")
            elif new_pass1 != new_pass2:
                st.error("Les nouveaux mots de passe ne correspondent pas")
            elif len(new_pass1) < 4:
                st.error("Le mot de passe doit contenir au moins 4 caractères")
            else:
                supabase.table("profiles").update({"password": hash_password(new_pass1)}).eq("username", user).execute()
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