import streamlit as st
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="SovereignNet",
    page_icon="🌐",
    layout="wide"
)

DATA_FOLDER = "data"

FILES = {
    "users": "data/users.json",
    "posts": "data/posts.json",
    "stories": "data/stories.json",
    "messages": "data/messages.json",
    "groups": "data/groups.json"
}

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def load(file):
    if not os.path.exists(file):
        return []
    with open(file,"r") as f:
        return json.load(f)

def save(file,data):
    with open(file,"w") as f:
        json.dump(data,f,indent=2)

# =====================================================
# AUTO REFRESH (live)
# =====================================================

st_autorefresh(interval=5000, key="live")

# =====================================================
# SESSION
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# LOGIN
# =====================================================

if not st.session_state.user:

    st.title("🌐 SovereignNet")

    username = st.text_input("Nom utilisateur")

    if st.button("Connexion / Création"):
        users = load(FILES["users"])

        if username not in users:
            users.append(username)
            save(FILES["users"],users)

        st.session_state.user = username
        st.rerun()

    st.stop()

# =====================================================
# HEADER
# =====================================================

st.title(f"🌐 SovereignNet — {st.session_state.user}")

# =====================================================
# NAVIGATION TYPE WHATSAPP
# =====================================================

tab1, tab2, tab3 = st.tabs(["💬 Discussions","🔥 Actu","🌐 Communautés"])

# =====================================================
# DISCUSSIONS
# =====================================================

with tab1:

    st.subheader("Messagerie")

    messages = load(FILES["messages"])

    target = st.text_input("Envoyer message à")

    if target:

        text = st.text_input("Message")

        if st.button("Envoyer"):
            messages.append({
                "from": st.session_state.user,
                "to": target,
                "text": text,
                "time": time.time()
            })

            save(FILES["messages"],messages)

        st.write("Conversation")

        for m in messages:

            if (m["from"]==st.session_state.user and m["to"]==target) or \
               (m["from"]==target and m["to"]==st.session_state.user):

                st.write(f"**{m['from']}** : {m['text']}")

    st.divider()

    st.subheader("📞 Appel audio / vidéo")

    webrtc_streamer(
        key="call",
        mode=WebRtcMode.SENDRECV
    )

# =====================================================
# ACTU (POSTS + STORIES)
# =====================================================

with tab2:

    st.subheader("Créer publication")

    text = st.text_area("Quoi de neuf ?")

    if st.button("Publier"):

        posts = load(FILES["posts"])

        posts.append({
            "id":str(uuid.uuid4()),
            "user":st.session_state.user,
            "text":text,
            "likes":0,
            "reposts":0,
            "time":time.time()
        })

        save(FILES["posts"],posts)

    st.divider()

    st.subheader("📷 Story 24h")

    story = st.text_input("Story")

    if st.button("Poster story"):

        stories = load(FILES["stories"])

        stories.append({
            "user":st.session_state.user,
            "text":story,
            "time":time.time()
        })

        save(FILES["stories"],stories)

    stories = load(FILES["stories"])

    st.write("Stories actives")

    for s in stories:

        if time.time()-s["time"] < 86400:

            st.write(f"{s['user']} : {s['text']}")

    st.divider()

    st.subheader("🔥 Fil viral")

    posts = load(FILES["posts"])

    posts = sorted(posts, key=lambda x:(x["likes"]+x["reposts"]), reverse=True)

    for p in posts:

        st.write(f"### {p['user']}")

        st.write(p["text"])

        col1,col2 = st.columns(2)

        if col1.button("❤️ Like",key=p["id"]):

            p["likes"]+=1
            save(FILES["posts"],posts)

        if col2.button("🔁 Repost",key=p["id"]+"r"):

            p["reposts"]+=1
            save(FILES["posts"],posts)

        st.write(f"👍 {p['likes']}  🔁 {p['reposts']}")

        st.divider()

# =====================================================
# COMMUNAUTES
# =====================================================

with tab3:

    st.subheader("Créer tunnel")

    name = st.text_input("Nom tunnel")

    if st.button("Créer groupe"):

        groups = load(FILES["groups"])

        code = str(uuid.uuid4())[:8]

        groups.append({
            "name":name,
            "creator":st.session_state.user,
            "code":code,
            "members":[st.session_state.user],
            "messages":[]
        })

        save(FILES["groups"],groups)

        st.success(f"Code accès : {code}")

    st.divider()

    st.subheader("Rejoindre tunnel")

    join = st.text_input("Code")

    if st.button("Rejoindre"):

        groups = load(FILES["groups"])

        for g in groups:

            if g["code"]==join:

                g["members"].append(st.session_state.user)
                save(FILES["groups"],groups)

                st.success("Rejoint")

    st.divider()

    st.subheader("Mes tunnels")

    groups = load(FILES["groups"])

    for g in groups:

        if st.session_state.user in g["members"]:

            st.write(f"### {g['name']}")

            msg = st.text_input("message",key=g["code"])

            if st.button("envoyer",key=g["code"]+"b"):

                g["messages"].append({
                    "user":st.session_state.user,
                    "text":msg
                })

                save(FILES["groups"],groups)

            for m in g["messages"]:

                st.write(f"{m['user']} : {m['text']}")

            st.divider()