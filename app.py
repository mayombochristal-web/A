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

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# =====================================================
# AUTO REFRESH GLOBAL (MESSAGERIE TEMPS RÉEL)
# =====================================================

st.experimental_autorefresh(interval=3000, key="refresh")

# =====================================================
# UTILITAIRES JSON
# =====================================================

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

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
# AUTH
# =====================================================

def login():

    st.title("Free_Kogossa")

    tab1, tab2 = st.tabs(["Connexion","Créer un compte"])

    with tab1:

        username = st.text_input("Nom utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):

            if username in users and users[username]["password"] == password:

                st.session_state.user = username
                st.success("Connexion réussie")
                st.rerun()

            else:

                st.error("Identifiants incorrects")

    with tab2:

        new_user = st.text_input("Nom utilisateur", key="newuser")
        new_pass = st.text_input("Mot de passe", type="password", key="newpass")

        bio = st.text_area("Bio")
        location = st.text_input("Localisation")

        profile_pic = st.file_uploader("Photo profil", type=["png","jpg","jpeg"])

        if st.button("Créer compte"):

            if new_user in users:

                st.error("Utilisateur existe déjà")

            else:

                pic_path = ""

                if profile_pic:

                    pic_path = f"{DATA_FOLDER}/{new_user}_profile.png"

                    with open(pic_path,"wb") as f:
                        f.write(profile_pic.getbuffer())

                users[new_user] = {
                    "password": new_pass,
                    "profile_pic": pic_path,
                    "bio": bio,
                    "location": location,
                    "created": str(datetime.now())
                }

                save_json(USERS_FILE, users)

                st.success("Compte créé")

# =====================================================
# BANNIÈRE PROFIL
# =====================================================

def banner():

    user = st.session_state.user

    st.markdown("---")

    col1,col2 = st.columns([1,4])

    with col1:

        if users[user]["profile_pic"] and os.path.exists(users[user]["profile_pic"]):

            st.image(users[user]["profile_pic"], width=120)

    with col2:

        st.title(user)

        if users[user].get("bio"):
            st.write(users[user]["bio"])

        if users[user].get("location"):
            st.caption("📍 "+users[user]["location"])

    st.markdown("---")

# =====================================================
# FIL SOCIAL
# =====================================================

def feed():

    banner()

    st.subheader("Exprime toi")

    post_text = st.text_area("Message")

    post_img = st.file_uploader("Image", type=["png","jpg","jpeg"])

    if st.button("Publier"):

        post_id = str(len(posts)+1)

        img_path = ""

        if post_img:

            img_path = f"{DATA_FOLDER}/post_{post_id}.png"

            with open(img_path,"wb") as f:
                f.write(post_img.getbuffer())

        posts[post_id] = {
            "user": st.session_state.user,
            "text": post_text,
            "image": img_path,
            "time": str(datetime.now()),
            "comments": []
        }

        save_json(POSTS_FILE, posts)

        st.rerun()

    st.divider()

    ordered_posts = sorted(posts.items(), key=lambda x: x[1]["time"], reverse=True)

    for pid,post in ordered_posts:

        st.subheader(post["user"])

        st.write(post["text"])

        if post["image"] and os.path.exists(post["image"]):

            st.image(post["image"])

        st.caption(post["time"])

        st.write("Commentaires")

        comment = st.text_input("Commenter", key=f"c{pid}")

        if st.button("Envoyer", key=f"b{pid}"):

            post["comments"].append({
                "user": st.session_state.user,
                "text": comment,
                "time": str(datetime.now())
            })

            save_json(POSTS_FILE, posts)

            st.rerun()

        for c in post["comments"]:

            st.write(f"**{c['user']}** : {c['text']}")

        st.divider()

# =====================================================
# MESSAGERIE
# =====================================================

def messenger():

    st.header("Messagerie")

    users_list = [u for u in users if u != st.session_state.user]

    target = st.selectbox("Choisir utilisateur", users_list)

    if not target:
        return

    conv_id = "_".join(sorted([st.session_state.user,target]))

    if conv_id not in messages:
        messages[conv_id] = []

    ordered = sorted(messages[conv_id], key=lambda x: x["time"])

    for m in ordered:

        if m["sender"] == st.session_state.user:
            st.write(f"🟢 **Moi** : {m['text']}")
        else:
            st.write(f"🔵 **{m['sender']}** : {m['text']}")

    msg = st.text_input("Message")

    if st.button("Envoyer message"):

        messages[conv_id].append({
            "sender": st.session_state.user,
            "text": msg,
            "time": str(datetime.now())
        })

        save_json(MESSAGES_FILE, messages)

        st.rerun()

# =====================================================
# PROFIL
# =====================================================

def profile():

    user = st.session_state.user

    st.header("Profil")

    if users[user]["profile_pic"] and os.path.exists(users[user]["profile_pic"]):
        st.image(users[user]["profile_pic"], width=150)

    st.write("Bio :", users[user].get("bio",""))
    st.write("Localisation :", users[user].get("location",""))

    st.caption("Compte créé : "+users[user]["created"])

    st.subheader("Modifier profil")

    new_bio = st.text_area("Bio", value=users[user].get("bio",""))
    new_loc = st.text_input("Localisation", value=users[user].get("location",""))

    new_pic = st.file_uploader("Changer photo", type=["png","jpg","jpeg"])

    if st.button("Mettre à jour profil"):

        users[user]["bio"] = new_bio
        users[user]["location"] = new_loc

        if new_pic:

            path = f"{DATA_FOLDER}/{user}_profile.png"

            with open(path,"wb") as f:
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
        ["Fil social","Messagerie","Profil"]
    )

    if st.sidebar.button("Déconnexion"):

        st.session_state.user = None
        st.rerun()

    if page == "Fil social":
        feed()

    if page == "Messagerie":
        messenger()

    if page == "Profil":
        profile()