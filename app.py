import streamlit as st
import json
import os
import uuid
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Free_Kongossa",
    page_icon="🌐",
    layout="wide"
)

DATA = "data"

FILES = {
    "users": f"{DATA}/users.json",
    "groups": f"{DATA}/groups.json",
    "posts": f"{DATA}/posts.json"
}

if not os.path.exists(DATA):
    os.makedirs(DATA)

# =====================================================
# DATABASE UTILS
# =====================================================

def load(file):

    if not os.path.exists(file):
        return []

    with open(file,"r") as f:
        return json.load(f)

def save(file,data):

    with open(file,"w") as f:
        json.dump(data,f,indent=2)

# =====================================================
# LIVE REFRESH
# =====================================================

st_autorefresh(interval=4000,key="live")

# =====================================================
# SESSION
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "group" not in st.session_state:
    st.session_state.group = None

# =====================================================
# LOGIN
# =====================================================

if not st.session_state.user:

    st.title("🌐 Free_Kongossa")

    name = st.text_input("Nom utilisateur")

    if st.button("Connexion"):

        users = load(FILES["users"])

        if name not in users:
            users.append(name)
            save(FILES["users"],users)

        st.session_state.user = name
        st.rerun()

    st.stop()

# =====================================================
# HEADER
# =====================================================

st.title(f"🌐 Free_Kongossa — {st.session_state.user}")

tab1,tab2,tab3 = st.tabs(["💬 Discussions","🔥 Actu","🌐 Communautés"])

# =====================================================
# COMMUNAUTES
# =====================================================

with tab3:

    st.subheader("Créer tunnel")

    groups = load(FILES["groups"])

    owned = [g for g in groups if g["creator"]==st.session_state.user]

    if len(owned) < 3:

        name = st.text_input("Nom tunnel")

        description = st.text_area("Description")

        public = st.checkbox("Tunnel public (follow possible)")

        avatar = st.file_uploader("Photo tunnel",type=["png","jpg","jpeg"])

        if st.button("Créer tunnel"):

            code = str(uuid.uuid4())[:8]

            groups.append({
                "id":str(uuid.uuid4()),
                "name":name,
                "creator":st.session_state.user,
                "description":description,
                "public":public,
                "code":code,
                "members":[st.session_state.user],
                "messages":[]
            })

            save(FILES["groups"],groups)

            st.success(f"Tunnel créé | code : {code}")

    else:
        st.warning("Limite de 3 tunnels créés atteinte")

    st.divider()

    # rejoindre

    st.subheader("Rejoindre tunnel")

    code = st.text_input("Code invitation")

    if st.button("Rejoindre"):

        groups = load(FILES["groups"])

        for g in groups:

            if g["code"] == code:

                if st.session_state.user not in g["members"]:
                    g["members"].append(st.session_state.user)

        save(FILES["groups"],groups)

    st.divider()

    # tunnels publics

    st.subheader("Tunnels publics")

    groups = load(FILES["groups"])

    for g in groups:

        if g["public"]:

            st.write(f"### {g['name']}")

            st.write(g["description"])

            st.write(f"Membres : {len(g['members'])}")

            if st.session_state.user in g["members"]:

                if st.button("Ne plus suivre",key=g["id"]):

                    g["members"].remove(st.session_state.user)
                    save(FILES["groups"],groups)

            else:

                if st.button("Suivre",key=g["id"]):

                    g["members"].append(st.session_state.user)
                    save(FILES["groups"],groups)

            st.divider()

# =====================================================
# DISCUSSIONS
# =====================================================

with tab1:

    groups = load(FILES["groups"])

    my_groups = [g for g in groups if st.session_state.user in g["members"]]

    names = [g["name"] for g in my_groups]

    group_name = st.selectbox("Choisir tunnel",names)

    group = next(g for g in my_groups if g["name"]==group_name)

    st.write(f"### {group['name']}")

    msg = st.text_input("Message")

    if st.button("Envoyer"):

        group["messages"].append({
            "user":st.session_state.user,
            "text":msg,
            "time":time.time()
        })

        save(FILES["groups"],groups)

    st.divider()

    for m in group["messages"][-50:]:

        st.write(f"**{m['user']}** : {m['text']}")

# =====================================================
# ACTU
# =====================================================

with tab2:

    st.subheader("Publier")

    text = st.text_area("Texte")

    photo = st.camera_input("Photo / vidéo")

    if st.button("Poster"):

        posts = load(FILES["posts"])

        posts.append({
            "id":str(uuid.uuid4()),
            "user":st.session_state.user,
            "text":text,
            "time":time.time(),
            "comments":[]
        })

        save(FILES["posts"],posts)

    st.divider()

    st.subheader("Fil d'actualité")

    posts = load(FILES["posts"])

    posts = sorted(posts,key=lambda x:x["time"],reverse=True)

    for p in posts:

        st.write(f"### {p['user']}")

        st.write(p["text"])

        comment = st.text_input("Commenter",key=p["id"])

        if st.button("Envoyer",key=p["id"]+"c"):

            p["comments"].append({
                "user":st.session_state.user,
                "text":comment
            })

            save(FILES["posts"],posts)

        for c in p["comments"]:

            st.write(f"💬 {c['user']} : {c['text']}")

        st.divider()