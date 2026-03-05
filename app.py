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

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

DATA_FOLDER = "data"          # Pour fichiers temporaires (optionnel)
ASSETS_FOLDER = "assets"      # Pour la photo du créateur
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)

BUCKET_NAME = "uploads"       # Nom du bucket Supabase

# =====================================================
# SÉCURITÉ : HACHAGE DES MOTS DE PASSE
# =====================================================
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# =====================================================
# UPLOAD VERS SUPABASE STORAGE
# =====================================================
def upload_to_storage(file_data, filename, content_type=None):
    """
    Upload un fichier vers le bucket 'uploads' et retourne l'URL publique.
    file_data: bytes ou BytesIO
    filename: nom du fichier (unique de préférence)
    content_type: type MIME (optionnel)
    """
    try:
        # Upload du fichier
        supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=file_data,
            file_options={"content-type": content_type} if content_type else {}
        )
        # Récupération de l'URL publique
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        return public_url
    except Exception as e:
        st.error(f"Erreur d'upload : {e}")
        return None

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
            # Vérifier si l'utilisateur existe
            check = supabase.table("profiles").select("username").eq("username", new_user).execute()
            if check.data:
                st.error("Ce pseudo est déjà pris")
            elif len(new_pass) < 4:
                st.error("Mot de passe trop court (minimum 4 caractères)")
            else:
                profile_pic_url = ""
                if pic:
                    # Générer un nom de fichier unique
                    ext = pic.name.split('.')[-1]
                    filename = f"profile_{new_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    profile_pic_url = upload_to_storage(pic.getvalue(), filename, pic.type)

                # Insertion dans Supabase
                user_dict = {
                    "username": new_user,
                    "password": hash_password(new_pass),
                    "bio": bio,
                    "location": location,
                    "profile_pic": profile_pic_url,
                }
                supabase.table("profiles").insert(user_dict).execute()
                st.success("Compte créé sur le Cloud ! Vous pouvez maintenant vous connecter.")

# =====================================================
# BANNIERE DE PROFIL (depuis Supabase)
# =====================================================
def banner():
    user = st.session_state.user
    response = supabase.table("profiles").select("*").eq("username", user).execute()
    if response.data:
        profile = response.data[0]
    else:
        st.error("Profil introuvable")
        return

    st.divider()
    col1, col2 = st.columns([1, 4])

    with col1:
        pic_url = profile.get("profile_pic", "")
        if pic_url:
            st.image(pic_url, width=120)
        else:
            st.caption("(aucune photo)")

    with col2:
        st.title(user)
        if profile.get("bio"):
            st.write(profile["bio"])
        if profile.get("location"):
            st.caption("📍 " + profile["location"])

    st.divider()

# =====================================================
# FIL SOCIAL (AVEC SUPABASE STORAGE)
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
    if img and img.size > 50 * 1024 * 1024:
    st.error("Cette image est trop lourde (max 50 Mo)")
if video and video.size > 50 * 1024 * 1024:
    st.error("Cette vidéo dépasse la limite de 50 Mo de Supabase")

    if st.button("Publier"):
        media_url = ""
        media_type = None

        if img is not None:
            ext = img.name.split('.')[-1]
            filename = f"post_img_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            media_url = upload_to_storage(img.getvalue(), filename, img.type)
            media_type = "image"
        elif video is not None:
            ext = video.name.split('.')[-1]
            filename = f"post_vid_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            media_url = upload_to_storage(video.getvalue(), filename, video.type)
            media_type = "video"

        # Insertion du post dans Supabase
        post_dict = {
            "username": st.session_state.user,
            "text": text,
            "media_path": media_url,      # On garde le même nom de colonne
            "media_type": media_type,
        }
        supabase.table("posts").insert(post_dict).execute()
        st.rerun()

    st.divider()

    # Récupération des 20 derniers posts
    posts_response = supabase.table("posts").select("*").order("created_at", desc=True).limit(20).execute()
    posts_list = posts_response.data if posts_response.data else []

    for post in posts_list:
        with st.container():
            st.subheader(f"@{post['username']}")
            st.write(post.get("text", ""))

            media_url = post.get("media_path", "")
            media_type = post.get("media_type")
            if media_url:
                if media_type == "image":
                    st.image(media_url)
                elif media_type == "video":
                    st.video(media_url)

            # Formatage de la date
            created_at = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
            st.caption(created_at.strftime("%Y-%m-%d %H:%M"))

            # Récupération des commentaires
            comments_response = supabase.table("comments").select("*").eq("post_id", post["id"]).order("created_at").execute()
            comments = comments_response.data if comments_response.data else []

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

            for c in comments:
                st.write(f"**{c['username']}** : {c['text']}")
            st.divider()

# =====================================================
# MESSAGERIE (AVEC SUPABASE STORAGE)
# =====================================================
def messenger():
    st_autorefresh(interval=2000, key="msg_refresh")
    st.header("Messagerie")

    # Liste des autres utilisateurs
    users_response = supabase.table("profiles").select("username").neq("username", st.session_state.user).execute()
    users_list = [u["username"] for u in users_response.data] if users_response.data else []

    if not users_list:
        st.info("Aucun autre utilisateur")
        return

    target = st.selectbox("Choisir utilisateur", users_list, key="msg_target")

    # Récupération des messages entre les deux utilisateurs
    from_user = st.session_state.user
    # Requête avec OR pour les deux sens
    messages_response = supabase.table("messages").select("*")\
        .or_(f"sender.eq.{from_user},recipient.eq.{from_user}")\
        .or_(f"sender.eq.{target},recipient.eq.{target}")\
        .order("created_at").execute()
    all_msgs = messages_response.data if messages_response.data else []
    # Filtrer pour n'avoir que les échanges entre les deux
    filtered_msgs = [
        m for m in all_msgs
        if (m["sender"] == from_user and m["recipient"] == target) or
           (m["sender"] == target and m["recipient"] == from_user)
    ]
    filtered_msgs.sort(key=lambda x: x["created_at"])

    for m in filtered_msgs:
        if m["sender"] == st.session_state.user:
            prefix = "🟢 **Moi** : "
        else:
            prefix = f"🔵 **{m['sender']}** : "

        if m.get("audio_path"):  # contient une URL
            st.write(prefix + "[Message audio]")
            st.audio(m["audio_path"])
        elif m.get("video_path"):
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
            filename = f"voice_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            url = upload_to_storage(audio_bytes, filename, "audio/wav")
            message_dict["audio_path"] = url
        elif audio_file is not None:
            ext = audio_file.name.split('.')[-1]
            filename = f"audio_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            url = upload_to_storage(audio_file.getvalue(), filename, audio_file.type)
            message_dict["audio_path"] = url
        elif video_file is not None:
            ext = video_file.name.split('.')[-1]
            filename = f"video_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            url = upload_to_storage(video_file.getvalue(), filename, video_file.type)
            message_dict["video_path"] = url
        elif text_msg.strip() != "":
            message_dict["text"] = text_msg
        else:
            st.warning("Écris un message, enregistre un audio ou ajoute un fichier.")
            st.stop()

        supabase.table("messages").insert(message_dict).execute()
        st.rerun()

# =====================================================
# PROFIL (AVEC SUPABASE STORAGE)
# =====================================================
def profile():
    user = st.session_state.user
    st.header("Profil")

    response = supabase.table("profiles").select("*").eq("username", user).execute()
    if not response.data:
        st.error("Profil introuvable")
        return
    profile_data = response.data[0]

    pic_url = profile_data.get("profile_pic", "")
    if pic_url:
        st.image(pic_url, width=150)
    else:
        st.caption("(aucune photo)")

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
            # Upload de la nouvelle photo
            ext = new_pic.name.split('.')[-1]
            filename = f"profile_{user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            pic_url = upload_to_storage(new_pic.getvalue(), filename, new_pic.type)
            if pic_url:
                update_dict["profile_pic"] = pic_url

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
        - 🗂️ **Stockage cloud** : Vos médias sont hébergés en toute sécurité.
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