import streamlit as st
from streamlit_autorefresh import st_autorefresh
import uuid
import json
import os
import time
import hashlib
import random

# ======================================
# CONFIG
# ======================================

st.set_page_config(
    page_title="FREE KONGOSSA",
    page_icon="🔥",
    layout="wide"
)

DATA="data"

FILES={
"users":f"{DATA}/users.json",
"groups":f"{DATA}/groups.json",
"posts":f"{DATA}/posts.json",
"stories":f"{DATA}/stories.json"
}

os.makedirs(DATA,exist_ok=True)

def load(path):
    if not os.path.exists(path):
        return []
    with open(path,"r") as f:
        return json.load(f)

def save(path,data):
    with open(path,"w") as f:
        json.dump(data,f)

# ======================================
# LOGIN
# ======================================

if "user" not in st.session_state:

    st.title("🔥 FREE KONGOSSA")

    pseudo=st.text_input("Pseudo")

    if st.button("Entrer"):

        if pseudo:

            st.session_state.user=f"{pseudo}_{uuid.uuid4().hex[:4]}"
            st.rerun()

    st.stop()

# ======================================
# LOAD DATA
# ======================================

users=load(FILES["users"])
groups=load(FILES["groups"])
posts=load(FILES["posts"])
stories=load(FILES["stories"])

# ======================================
# UI HEADER
# ======================================

st.title("🔥 FREE KONGOSSA")

tab1,tab2,tab3=st.tabs(["💬 Discussions","🔥 Actu","👥 Communautés"])

# ======================================
# DISCUSSIONS
# ======================================

with tab1:

    my_groups=[g for g in groups if st.session_state.user in g["members"]]

    if len(my_groups)==0:
        st.info("Aucun tunnel rejoint.")
        st.stop()

    names=[g["name"] for g in my_groups]

    group_name=st.selectbox("Choisir tunnel",names)

    group=None
    for g in my_groups:
        if g["name"]==group_name:
            group=g

    if group is None:
        st.stop()

    col1,col2=st.columns([1,3])

    with col1:
        if group["photo"]:
            st.image(group["photo"],width=80)

    with col2:
        st.subheader(group["name"])
        st.caption(f"{len(group['members'])} membres")
        st.write(group["description"])

    st.divider()

    # MESSAGE INPUT
    if "msg" not in st.session_state:
        st.session_state.msg=""

    msg=st.text_input("Message",key="msg")

    if st.button("Envoyer"):

        if msg.strip()!="":

            group["messages"].append({
            "user":st.session_state.user,
            "text":msg,
            "time":time.time()
            })

            save(FILES["groups"],groups)

            st.session_state.msg=""
            st.rerun()

    st.divider()

    for m in group["messages"][-50:]:

        st.write(f"**{m['user']}** : {m['text']}")

# ======================================
# ACTU
# ======================================

with tab2:

    st.subheader("Nouvelle publication")

    text=st.text_area("Texte")

    col1,col2=st.columns(2)

    with col1:
        cam=st.camera_input("Photo")

    with col2:
        file=st.file_uploader("Upload",type=["png","jpg","jpeg","mp4"])

    if st.button("Publier"):

        media=None

        if cam:
            media=cam.getvalue()

        elif file:
            media=file.getvalue()

        posts.append({
        "id":uuid.uuid4().hex,
        "user":st.session_state.user,
        "text":text,
        "media":media,
        "time":time.time(),
        "likes":0,
        "comments":[]
        })

        save(FILES["posts"],posts)

        st.rerun()

    st.divider()

    # ALGO VIRAL
    def score(p):
        age=time.time()-p["time"]
        return (p["likes"]+1)/((age/3600)+1)

    posts_sorted=sorted(posts,key=score,reverse=True)

    for p in posts_sorted[:50]:

        st.write(f"**{p['user']}**")

        if p["text"]:
            st.write(p["text"])

        if p["media"]:
            st.image(p["media"])

        if st.button("🔥 Like",key=p["id"]):
            p["likes"]+=1
            save(FILES["posts"],posts)
            st.rerun()

        st.write(f"{p['likes']} likes")

        # COMMENT
        c=st.text_input("Commenter",key=f"c{p['id']}")

        if st.button("Envoyer",key=f"s{p['id']}"):

            if c:
                p["comments"].append({
                "user":st.session_state.user,
                "text":c
                })

                save(FILES["posts"],posts)
                st.rerun()

        for com in p["comments"]:
            st.write(f"💬 {com['user']} : {com['text']}")

        st.divider()

# ======================================
# COMMUNAUTES
# ======================================

with tab3:

    st.subheader("Créer tunnel")

    my_created=[g for g in groups if g["creator"]==st.session_state.user]

    if len(my_created)>=3:

        st.warning("Limite de 3 tunnels créés")

    else:

        name=st.text_input("Nom tunnel")
        desc=st.text_input("Description")
        photo=st.file_uploader("Photo tunnel",type=["png","jpg","jpeg"])

        if st.button("Créer"):

            code=hashlib.sha1(name.encode()).hexdigest()[:6]

            groups.append({
            "name":name,
            "description":desc,
            "photo":photo.getvalue() if photo else None,
            "code":code,
            "creator":st.session_state.user,
            "members":[st.session_state.user],
            "messages":[]
            })

            save(FILES["groups"],groups)

            st.success(f"Code tunnel : {code}")

            st.rerun()

    st.divider()

    st.subheader("Rejoindre tunnel")

    join=st.text_input("Code tunnel")

    if st.button("Rejoindre"):

        for g in groups:

            if g["code"]==join:

                if st.session_state.user not in g["members"]:
                    g["members"].append(st.session_state.user)

                    save(FILES["groups"],groups)

                    st.success("Tunnel rejoint")
                    st.rerun()

    st.divider()

    st.subheader("Mes tunnels")

    for g in groups:

        if st.session_state.user in g["members"]:

            col1,col2=st.columns([4,1])

            with col1:
                st.write(g["name"])

            with col2:

                if st.button("Quitter",key=g["code"]):

                    g["members"].remove(st.session_state.user)

                    save(FILES["groups"],groups)

                    st.rerun()

# ======================================
# AUTO REFRESH
# ======================================

st_autorefresh(interval=4000,key="refresh")