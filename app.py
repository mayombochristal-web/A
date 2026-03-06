import streamlit as st
import os
import hashlib
from datetime import datetime, timedelta
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
from streamlit_mic_recorder import mic_recorder

# --- NOUVEAUX IMPORTS POUR LA PARTIE SCIENTIFIQUE ---
import numpy as np
import pandas as pd
import plotly.graph_objects as go
# ----------------------------------------------------

# =====================================================
# CONFIG & CONNEXION SUPABASE
# =====================================================
st.set_page_config(page_title="Free_Kogossa", layout="wide")

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

DATA_FOLDER = "data"
ASSETS_FOLDER = "assets"
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)

BUCKET_NAME = "uploads"       # Nom du bucket Supabase (doit être public)

# =====================================================
# SÉCURITÉ : HACHAGE DES MOTS DE PASSE
# =====================================================
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# =====================================================
# UPLOAD VERS SUPABASE STORAGE (URL PUBLIQUE)
# =====================================================
def upload_to_storage(file_data, filename, content_type=None):
    """
    Upload un fichier vers le bucket 'uploads' (public) et retourne l'URL publique.
    Retourne None en cas d'échec.
    """
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=file_data,
            file_options={"content-type": content_type} if content_type else {}
        )
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

# --- NOUVEAU : Suivi de l'activité pour rafraîchissement adaptatif ---
if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.now()

def update_activity():
    st.session_state.last_activity = datetime.now()

def get_refresh_interval():
    """Retourne l'intervalle de rafraîchissement selon l'inactivité (principe de dissipation)."""
    idle = (datetime.now() - st.session_state.last_activity).seconds
    if idle < 60:
        return 2000      # actif : 2 secondes
    elif idle < 300:
        return 5000      # 5 secondes
    else:
        return 10000     # inactif : 10 secondes
# ----------------------------------------------------

# =====================================================
# FONCTIONS DE GESTION DU WALLET ET FORFAITS
# =====================================================

def get_wallet(username):
    """Retourne le solde KC de l'utilisateur."""
    resp = supabase.table("wallets").select("kongo_balance").eq("username", username).execute()
    if resp.data:
        return resp.data[0]["kongo_balance"]
    return 0.0

def update_wallet(username, amount, operation="add"):
    """Ajoute ou retire des KC du wallet. operation : 'add' ou 'subtract'."""
    wallet = supabase.table("wallets").select("kongo_balance").eq("username", username).execute()
    if not wallet.data:
        return False
    current = wallet.data[0]["kongo_balance"]
    new_balance = current + amount if operation == "add" else current - amount
    if new_balance < 0:
        return False
    supabase.table("wallets").update({"kongo_balance": new_balance}).eq("username", username).execute()
    return True

def get_user_plan(username):
    """Retourne le forfait actuel de l'utilisateur."""
    resp = supabase.table("subscriptions").select("plan_type", "expires_at", "is_active").eq("username", username).execute()
    if resp.data:
        return resp.data[0]
    return {"plan_type": "Gratuit", "expires_at": None, "is_active": True}

def activate_plan(username, plan_type, duration_days=30):
    """Active un forfait pour l'utilisateur (met à jour subscriptions et tst_params)."""
    expires_at = datetime.now() + timedelta(days=duration_days)
    data = {
        "username": username,
        "plan_type": plan_type,
        "activated_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat(),
        "is_active": True
    }
    supabase.table("subscriptions").delete().eq("username", username).execute()
    supabase.table("subscriptions").insert(data).execute()

    params = {}
    if plan_type == "Gratuit":
        params = {"phi_m": 1.0, "phi_c": 1.0, "phi_d": 1.5}
    elif plan_type == "Pro_Memoire":
        params = {"phi_m": 3.0, "phi_c": 1.0, "phi_d": 0.1}
    elif plan_type == "Attracteur_Global":
        params = {"phi_m": 2.0, "phi_c": 10.0, "phi_d": 1.0}

    supabase.table("tst_params").update(params).eq("username", username).execute()

def credit_creator(amount):
    """Crédite le wallet du créateur (SCARABBE) du montant spécifié."""
    update_wallet("SCARABBE", amount, "add")

# --- NOUVEAU : S'assurer que SCARABBE a 1M KC ---
def ensure_scarabbe_wallet():
    """Si l'utilisateur est SCARABBE et que son wallet est à 0, on lui donne 1M KC."""
    if st.session_state.user == "SCARABBE":
        current = get_wallet("SCARABBE")
        if current == 0.0:
            update_wallet("SCARABBE", 1_000_000, "add")
            st.sidebar.success("🎉 Bienvenue Créateur ! 1 000 000 KC ont été crédités sur votre wallet.")
# ------------------------------------------------

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
                    update_activity()
                    ensure_scarabbe_wallet()   # ICI : on donne 1M à SCARABBE si nécessaire
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
            check = supabase.table("profiles").select("username").eq("username", new_user).execute()
            if check.data:
                st.error("Ce pseudo est déjà pris")
            elif len(new_pass) < 4:
                st.error("Mot de passe trop court (minimum 4 caractères)")
            else:
                profile_pic_url = ""
                if pic:
                    ext = pic.name.split('.')[-1]
                    filename = f"profile_{new_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    profile_pic_url = upload_to_storage(pic.getvalue(), filename, pic.type)
                    if not profile_pic_url:
                        st.error("Échec de l'upload de la photo de profil. Compte non créé.")
                        st.stop()

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
# NOUVEAU : CŒUR TST (calcul de stabilité)
# =====================================================
def calculate_stability(likes, comments, phi_m=1.0, phi_c=1.0, phi_d=1.0):
    """
    Applique la TTU-MC3 avec coefficients personnalisables.
    """
    stability = (likes * phi_m * 0.6 + comments * phi_c * 0.4) * np.exp(-phi_d)
    return round(stability, 2)

def get_user_params(username):
    """Récupère les paramètres TST de l'utilisateur."""
    resp = supabase.table("tst_params").select("phi_m", "phi_c", "phi_d").eq("username", username).execute()
    if resp.data:
        return resp.data[0]
    return {"phi_m": 1.0, "phi_c": 1.0, "phi_d": 1.0}

# =====================================================
# NOUVEAU : Gestion des likes
# =====================================================
def like_post(post_id, username):
    """Ajoute un like pour un post (table 'likes')."""
    existing = supabase.table("likes").select("*").eq("post_id", post_id).eq("username", username).execute()
    if not existing.data:
        supabase.table("likes").insert({"post_id": post_id, "username": username}).execute()
        update_activity()

def get_likes_count(post_id):
    """Retourne le nombre de likes pour un post."""
    resp = supabase.table("likes").select("*", count="exact").eq("post_id", post_id).execute()
    return resp.count if hasattr(resp, 'count') else len(resp.data)

# =====================================================
# FIL SOCIAL (AVEC SUPABASE STORAGE)
# =====================================================
def feed():
    st_autorefresh(interval=get_refresh_interval(), key="feed_refresh")
    banner()
    st.subheader("Exprime toi")

    text = st.text_area("Message")
    col_img, col_vid = st.columns(2)
    with col_img:
        img = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="feed_img")
    with col_vid:
        video = st.file_uploader("Vidéo", type=["mp4", "mov", "avi", "mkv"], key="feed_video")

    if img is not None and img.size > 50 * 1024 * 1024:
        st.error("Cette image est trop lourde (max 50 Mo)")
        st.stop()
    if video is not None and video.size > 50 * 1024 * 1024:
        st.error("Cette vidéo dépasse la limite de 50 Mo de Supabase")
        st.stop()

    if st.button("Publier"):
        media_url = ""
        media_type = None

        if img is not None:
            ext = img.name.split('.')[-1]
            filename = f"post_img_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            media_url = upload_to_storage(img.getvalue(), filename, img.type)
            if not media_url:
                st.error("L'image n'a pas pu être uploadée. Publication annulée.")
                st.stop()
            media_type = "image"
        elif video is not None:
            ext = video.name.split('.')[-1]
            filename = f"post_vid_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            media_url = upload_to_storage(video.getvalue(), filename, video.type)
            if not media_url:
                st.error("La vidéo n'a pas pu être uploadée. Publication annulée.")
                st.stop()
            media_type = "video"

        post_dict = {
            "username": st.session_state.user,
            "text": text,
            "media_path": media_url,
            "media_type": media_type,
        }
        supabase.table("posts").insert(post_dict).execute()
        update_activity()
        st.rerun()

    st.divider()

    posts_response = supabase.table("posts").select("*").order("created_at", desc=True).limit(20).execute()
    posts_list = posts_response.data if posts_response.data else []

    for post in posts_list:
        with st.container():
            st.subheader(f"@{post['username']}")
            st.write(post.get("text", ""))

            media_url = post.get("media_path", "")
            media_type = post.get("media_type")
            if media_url and media_type:
                if media_type == "image":
                    st.image(media_url)
                elif media_type == "video":
                    st.video(media_url)

            created_at = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
            st.caption(created_at.strftime("%Y-%m-%d %H:%M"))

            post_author = post["username"]
            author_params = get_user_params(post_author)
            likes_count = get_likes_count(post["id"])
            comments_response = supabase.table("comments").select("*", count="exact").eq("post_id", post["id"]).execute()
            comments_count = comments_response.count if hasattr(comments_response, 'count') else len(comments_response.data)
            stability = calculate_stability(likes_count, comments_count,
                                            phi_m=author_params["phi_m"],
                                            phi_c=author_params["phi_c"],
                                            phi_d=author_params["phi_d"])
            st.markdown(f"**Indice de Stabilité (TST) :** `{stability}`")
            if stability > 5.0:
                st.success("🔥 Ce post est un Attracteur Stable")

            col1, col2 = st.columns([1, 10])
            with col1:
                if st.button("❤️", key=f"like_{post['id']}"):
                    like_post(post["id"], st.session_state.user)
                    st.rerun()
            with col2:
                st.write(f"**{likes_count}** likes")

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
                    update_activity()
                    st.rerun()

            for c in comments:
                st.write(f"**{c['username']}** : {c['text']}")
            st.divider()

# =====================================================
# MESSAGERIE (AVEC SUPABASE STORAGE)
# =====================================================
def messenger():
    st_autorefresh(interval=get_refresh_interval(), key="msg_refresh")
    st.header("Messagerie")

    users_response = supabase.table("profiles").select("username").neq("username", st.session_state.user).execute()
    users_list = [u["username"] for u in users_response.data] if users_response.data else []

    if not users_list:
        st.info("Aucun autre utilisateur")
        return

    target = st.selectbox("Choisir utilisateur", users_list, key="msg_target")

    from_user = st.session_state.user
    messages_response = supabase.table("messages").select("*")\
        .or_(f"sender.eq.{from_user},recipient.eq.{from_user}")\
        .or_(f"sender.eq.{target},recipient.eq.{target}")\
        .order("created_at").execute()
    all_msgs = messages_response.data if messages_response.data else []
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

        if m.get("audio_path"):
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
        if audio_file is not None and audio_file.size > 50 * 1024 * 1024:
            st.error("Fichier audio trop lourd (max 50 Mo)")
            st.stop()

        if video_file is not None and video_file.size > 50 * 1024 * 1024:
            st.error("Fichier vidéo trop lourd (max 50 Mo)")
            st.stop()

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
        upload_success = False

        if audio_bytes is not None:
            filename = f"voice_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            url = upload_to_storage(audio_bytes, filename, "audio/wav")
            if url:
                message_dict["audio_path"] = url
                upload_success = True
            else:
                st.error("L'enregistrement audio n'a pas pu être uploadé.")
                st.stop()
        elif audio_file is not None:
            ext = audio_file.name.split('.')[-1]
            filename = f"audio_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            url = upload_to_storage(audio_file.getvalue(), filename, audio_file.type)
            if url:
                message_dict["audio_path"] = url
                upload_success = True
            else:
                st.error("Le fichier audio n'a pas pu être uploadé.")
                st.stop()
        elif video_file is not None:
            ext = video_file.name.split('.')[-1]
            filename = f"video_{st.session_state.user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            url = upload_to_storage(video_file.getvalue(), filename, video_file.type)
            if url:
                message_dict["video_path"] = url
                upload_success = True
            else:
                st.error("Le fichier vidéo n'a pas pu être uploadé.")
                st.stop()
        elif text_msg.strip() != "":
            message_dict["text"] = text_msg
            upload_success = True
        else:
            st.warning("Écris un message, enregistre un audio ou ajoute un fichier.")
            st.stop()

        if upload_success:
            supabase.table("messages").insert(message_dict).execute()
            update_activity()
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

    kc_balance = get_wallet(user)
    st.metric("💰 Kongo Coins", f"{kc_balance:.2f} KC")

    plan_info = get_user_plan(user)
    st.info(f"Forfait actuel : **{plan_info['plan_type']}**")
    if plan_info['expires_at']:
        expires = datetime.fromisoformat(plan_info['expires_at'].replace("Z", "+00:00"))
        st.caption(f"Expire le : {expires.strftime('%Y-%m-%d %H:%M')}")

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
            ext = new_pic.name.split('.')[-1]
            filename = f"profile_{user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            pic_url = upload_to_storage(new_pic.getvalue(), filename, new_pic.type)
            if pic_url:
                update_dict["profile_pic"] = pic_url
            else:
                st.error("Échec de l'upload de la nouvelle photo. Mise à jour annulée.")
                st.stop()

        if update_dict:
            supabase.table("profiles").update(update_dict).eq("username", user).execute()
            update_activity()
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
                update_activity()

# =====================================================
# BOUTIQUE / FORFAITS
# =====================================================
def shop():
    st.header("🛒 Boutique des Forfaits Physiques")
    user = st.session_state.user
    balance = get_wallet(user)

    st.metric("Votre solde", f"{balance:.2f} KC")

    st.subheader("Améliorez votre présence avec les forfaits TTU‑MC³")
    st.markdown("""
    - **Gratuit** : Dissipation rapide, visibilité standard. (0 KC)
    - **Pro_Memoire** : Vos posts durent plus longtemps (faible dissipation). (50 KC / mois)
    - **Attracteur_Global** : Devenez le centre d'attraction du réseau (visibilité ×10). (100 KC / mois)
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Activer Gratuit (0 KC)"):
            current = get_user_plan(user)
            if current['plan_type'] == 'Gratuit':
                st.warning("Vous êtes déjà en forfait Gratuit.")
            else:
                activate_plan(user, "Gratuit", 30)
                st.success("Forfait Gratuit activé.")
                st.rerun()
    with col2:
        if st.button("Activer Pro_Memoire (50 KC)"):
            if balance >= 50:
                if update_wallet(user, 50, "subtract"):
                    credit_creator(50)
                    activate_plan(user, "Pro_Memoire", 30)
                    st.success("Forfait Pro_Memoire activé !")
                    st.rerun()
                else:
                    st.error("Erreur lors du paiement.")
            else:
                st.error("Solde insuffisant.")
    with col3:
        if st.button("Activer Attracteur_Global (100 KC)"):
            if balance >= 100:
                if update_wallet(user, 100, "subtract"):
                    credit_creator(100)
                    activate_plan(user, "Attracteur_Global", 30)
                    st.success("Forfait Attracteur_Global activé !")
                    st.rerun()
                else:
                    st.error("Erreur lors du paiement.")
            else:
                st.error("Solde insuffisant.")

    st.divider()
    st.subheader("Acheter des Kongo Coins")
    st.markdown("(Simulation – à connecter à un vrai système de paiement)")
    amount = st.number_input("Montant de KC à ajouter", min_value=10, step=10, value=50)
    if st.button("Ajouter KC"):
        update_wallet(user, amount, "add")
        st.success(f"{amount} KC ajoutés à votre wallet !")
        st.rerun()

# =====================================================
# ADMIN PANEL (RÉSERVÉ À SCARABBE)
# =====================================================
def admin_panel():
    if st.session_state.user != "SCARABBE":
        st.error("Accès non autorisé.")
        return

    st.title("🛡️ Administration Centrale TTU-MC³")
    st.success("Accès Maître des Attracteurs validé.")

    users_resp = supabase.table("profiles").select("username").execute()
    users_list = [u["username"] for u in users_resp.data] if users_resp.data else []

    target_user = st.selectbox("Choisir un utilisateur à configurer", users_list)

    params = get_user_params(target_user)
    sub_info = get_user_plan(target_user)

    st.subheader(f"Réglages Physiques pour @{target_user}")
    st.write(f"Forfait actuel : {sub_info['plan_type']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        new_phi_m = st.slider("Coefficient Mémoire (Φm)", 0.1, 5.0, params["phi_m"])
    with col2:
        new_phi_c = st.slider("Cohérence / Visibilité (Φc)", 0.1, 10.0, params["phi_c"])
    with col3:
        new_phi_d = st.slider("Taux de Dissipation (Φd)", 0.01, 2.0, params["phi_d"])

    new_plan = st.selectbox("Forfait", ["Gratuit", "Pro_Memoire", "Attracteur_Global"],
                            index=["Gratuit", "Pro_Memoire", "Attracteur_Global"].index(sub_info['plan_type']) if sub_info['plan_type'] in ["Gratuit", "Pro_Memoire", "Attracteur_Global"] else 0)

    if st.button("Appliquer les modifications TTU-MC³"):
        supabase.table("tst_params").update({
            "phi_m": new_phi_m,
            "phi_c": new_phi_c,
            "phi_d": new_phi_d
        }).eq("username", target_user).execute()

        if new_plan != sub_info['plan_type']:
            supabase.table("subscriptions").delete().eq("username", target_user).execute()
            supabase.table("subscriptions").insert({
                "username": target_user,
                "plan_type": new_plan,
                "activated_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                "is_active": True
            }).execute()

        st.success("Système dynamique mis à jour avec succès.")

# =====================================================
# LABORATOIRE TST (visualisation 3D)
# =====================================================
def tst_laboratory():
    st.header("🔬 Laboratoire de Dynamique Triadique")
    st.info("Visualisation en temps réel de la convergence du réseau vers son attracteur stable.")

    def lorenz(x, y, z, s=10, r=28, b=2.667):
        x_dot = s*(y - x)
        y_dot = r*x - y - x*z
        z_dot = x*y - b*z
        return x_dot, y_dot, z_dot

    dt = 0.01
    num_steps = 2000
    xs = np.empty(num_steps + 1)
    ys = np.empty(num_steps + 1)
    zs = np.empty(num_steps + 1)
    xs[0], ys[0], zs[0] = (0., 1., 1.05)

    for i in range(num_steps):
        x_dot, y_dot, z_dot = lorenz(xs[i], ys[i], zs[i])
        xs[i+1] = xs[i] + (x_dot * dt)
        ys[i+1] = ys[i] + (y_dot * dt)
        zs[i+1] = zs[i] + (z_dot * dt)

    fig = go.Figure(data=[go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', line=dict(color='blue', width=1))])
    fig.update_layout(
        title="Attracteur de Lorenz – Analogie de la stabilité sociale",
        scene=dict(
            xaxis_title="Mémoire (M)",
            yaxis_title="Cohérence (C)",
            zaxis_title="Dissipation (D)"
        )
    )
    st.plotly_chart(fig)

    st.markdown("""
    Cette visualisation illustre comment un système dynamique (comme votre réseau) peut converger vers des états stables (attracteurs) 
    malgré des perturbations. Les paramètres sont issus de la **Théorie Spectrale Triadique** et du paradigme **TTU-MC³**.
    """)

# =====================================================
# À PROPOS / CRÉATEUR (VERSION ENRICHIE)
# =====================================================
def about():
    st.header("👤 Créateur & Vision Scientifique")

    col1, col2 = st.columns([1, 2])
    with col1:
        creator_pic = os.path.join(ASSETS_FOLDER, "creator.jpg")
        if os.path.exists(creator_pic):
            st.image(creator_pic, use_container_width=True)
        else:
            st.info("Photo de SCARABBE")

    with col2:
        st.markdown("""
        ### **SCARABBE** *Fondateur de Free_Kogossa & Chercheur en Systèmes Dynamiques*

        Free_Kogossa n'est pas qu'un réseau social ; c'est le premier moteur social piloté par la **Théorie Spectrale Triadique (TST)**. 
        Mon travail consiste à modéliser les interactions humaines non pas comme des données statiques, mais comme des flux d'énergie en quête de stabilité.
        """)

    st.divider()

    st.subheader("🔬 Le Moteur Théorique : TTU-MC³")

    with st.expander("En savoir plus sur la science derrière Free_Kogossa"):
        st.markdown("""
        L'architecture de cette application repose sur le paradigme **TTU-MC³** (Mémoire, Cohérence, Dissipation). 
        Contrairement aux algorithmes classiques, Free_Kogossa utilise :

        * **Convergence vers l'Attracteur** : Vos flux d'actualités sont optimisés pour atteindre un état d'équilibre informationnel stable.
        * **Stabilité de Lyapunov** : Pour garantir une modération organique et une robustesse face aux perturbations du réseau.
        * **Énergie Dissipative** : Un système d'auto-scaling qui réduit l'empreinte numérique quand le système est au repos.

        *Travaux basés sur la recherche doctorale : "Théorie Spectrale Triadique : Extension des systèmes dynamiques dissipatifs".*
        """)

        st.write("📊 **Simulation de Convergence Triadique**")
        t = np.linspace(0, 20, 200)
        dampening = np.exp(-0.2 * t)
        oscillation = np.cos(1.5 * t)
        stability = dampening * oscillation
        chart_data = pd.DataFrame({
            "Temps (t)": t,
            "Stabilité du Flux (Φ)": stability
        }).set_index("Temps (t)")
        st.line_chart(chart_data)
        st.caption("Visualisation de la stabilisation d'un flux d'information après interaction.")

        st.markdown("### 📄 Documents de recherche")
        doc_path_pdf = os.path.join(ASSETS_FOLDER, "TST_Thesis.pdf")
        doc_path_docx = os.path.join(ASSETS_FOLDER, "TST_Thesis.docx")
        if os.path.exists(doc_path_pdf):
            with open(doc_path_pdf, "rb") as f:
                st.download_button("📥 Télécharger la thèse (PDF)", f, file_name="TST_Thesis.pdf")
        if os.path.exists(doc_path_docx):
            with open(doc_path_docx, "rb") as f:
                st.download_button("📥 Télécharger la thèse (DOCX)", f, file_name="TST_Thesis.docx")
        if not os.path.exists(doc_path_pdf) and not os.path.exists(doc_path_docx):
            st.info("Les documents de recherche seront bientôt disponibles dans le dossier 'assets'.")

    st.divider()
    st.header("🌟 Avantages de Free_Kogossa")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        - 🔒 **Confidentialité** : Pas de pistage, pas de publicités ciblées.
        - 🎙️ **Multi-modalité** : Audio, Vidéo et Texte intégrés.
        - ⚡ **Algorithme Physique** : Une pertinence basée sur la TST.
        """)
    with col_b:
        st.markdown("""
        - 🔄 **Stabilité Structurelle** : Une infrastructure résiliente.
        - 📐 **Auto-scaling Énergétique** : Rafraîchissement adaptatif.
        - 🧠 **Recherche intégrée** : Le réseau est un laboratoire vivant.
        """)

    st.divider()
    st.caption("Free_Kogossa – L'union de la science gabonaise et de la technologie cloud. © 2026")

# =====================================================
# MAIN
# =====================================================
if not st.session_state.user:
    login()
else:
    st.sidebar.title("Free_Kogossa")
    kc_balance = get_wallet(st.session_state.user)
    st.sidebar.metric("💰 Kongo Coins", f"{kc_balance:.2f} KC")

    menu_options = ["Fil social", "Messagerie", "Profil", "Boutique", "Laboratoire TST", "À propos / Créateur"]
    if st.session_state.user == "SCARABBE":
        menu_options.append("Administration")

    page = st.sidebar.radio("Navigation", menu_options)

    if st.sidebar.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

    if page == "Fil social":
        feed()
    elif page == "Messagerie":
        messenger()
    elif page == "Profil":
        profile()
    elif page == "Boutique":
        shop()
    elif page == "Laboratoire TST":
        tst_laboratory()
    elif page == "À propos / Créateur":
        about()
    elif page == "Administration":
        admin_panel()