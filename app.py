import streamlit as st
import json
import os
import uuid
import time
from streamlit_autorefresh import st_autorefresh

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="SovereignNet",
    page_icon="🌐",
    layout="wide"
)

DATA="data"

FILES={
"users":f"{DATA}/users.json",
"groups":f"{DATA}/groups.json",
"posts":f"{DATA}/posts.json"
}

os.makedirs(DATA,exist_ok=True)

# =====================================================
# DATABASE
# =====================================================

def load(file):

    if not os.path.exists(file):
        return []

    try:
        with open(file,"r") as f:
            return json.load(f)
    except:
        return []

def save(file,data):

    with open(file,"w") as f:
        json.dump(data,f,indent=2)

# =====================================================
# LIVE REFRESH
# =====================================================

st_autorefresh(interval=4000,key="refresh")

# =====================================================
# SESSION
# =====================================================

if "user" not in st.session_state:
    st.session_state.user=None

if "msg_input" not in st.session_state:
    st.session_state.msg_input=""

# =====================================================
# LOGIN
# =====================================================

if not st.session_state.user:

    st.title("🌐 SovereignNet")

    name=st.text_input("Nom utilisateur")

    if st.button("Connexion"):

        if name:

            users=load(FILES["users"])

            if name not in users:
                users.append(name)
                save(FILES["users"],users)

            st.session_state.user=name
            st.rerun()

    st.stop()

# =====================================================
# LOAD DATA
# =====================================================

groups=load(FILES["groups"])
posts=load(FILES["posts"])

# =====================================================
# HEADER
# =====================================================

st.title(f"🌐 SovereignNet — {st.session_state.user}")

tab1,tab2,tab3=st.tabs(["💬 Discussions","🔥 Actu","🌐 Communautés"])

# =====================================================
# DISCUSSIONS
# =====================================================

with tab1:

    groups=load(FILES["groups"])

    my_groups=[g for g in groups if st.session_state.user in g["members"]]

    if len(my_groups)==0:
        st.info("Aucun tunnel rejoint")
        st.stop()

    names=[g["name"] for g in my_groups]

    group_name=st.selectbox("Choisir tunnel",names)

    group=None
    for g in my_groups:
        if g["name"]==group_name:
            group=g
            break

    if group is None:
        st.stop()

    # ====================
    # PROFIL TUNNEL
    # ====================

    col1,col2=st.columns([1,4])

    with col1:
        if group.get("photo"):
            st.image(group["photo"],width=80)

    with col2:
        st.subheader(group["name"])
        st.caption(f"Membres : {len(group['members'])}")
        st.write(group.get("description",""))

    st.divider()

    # MESSAGE INPUT

    msg=st.text_input("Message",key="msg_input")

    if st.button("Envoyer"):

        if msg.strip()!="":

            group["messages"].append({
            "user":st.session_state.user,
            "text":msg,
            "time":time.time()
            })

            save(FILES["groups"],groups)

            st.session_state.msg_input=""
            st.rerun()

    st.divider()

    for m in group["messages"][-50:]:

        st.write(f"**{m['user']}** : {m['text']}")

# =====================================================
# ACTU
# =====================================================

with tab2:

    st.subheader("Publier")

    text=st.text_area("Texte")

    col1,col2=st.columns(2)

    with col1:
        cam=st.camera_input("Photo / vidéo")

    with col2:
        file=st.file_uploader("Choisir fichier",type=["jpg","jpeg","png","mp4"])

    if st.button("Publier Actu"):

        media=None

        if cam:
            media=cam.getvalue()

        elif file:
            media=file.getvalue()

        posts.append({
        "id":str(uuid.uuid4()),
        "user":st.session_state.user,
        "text":text,
        "media":media,
        "time":time.time(),
        "comments":[]
        })

        save(FILES["posts"],posts)

        st.rerun()

    st.divider()

    st.subheader("Fil d'actualité")

    posts=load(FILES["posts"])

    posts=sorted(posts,key=lambda x:x["time"],reverse=True)

    for p in posts[:50]:

        st.write(f"### {p['user']}")

        if p["text"]:
            st.write(p["text"])

        if p.get("media"):
            st.image(p["media"])

        comment=st.text_input("Commenter",key=f"c{p['id']}")

        if st.button("Envoyer",key=f"s{p['id']}"):

            if comment:

                p["comments"].append({
                "user":st.session_state.user,
                "text":comment
                })

                save(FILES["posts"],posts)

                st.rerun()

        for c in p["comments"]:
            st.write(f"💬 {c['user']} : {c['text']}")

        st.divider()

# =====================================================
# COMMUNAUTES
# =====================================================

with tab3:

    groups=load(FILES["groups"])

    st.subheader("Créer tunnel")

    owned=[g for g in groups if g["creator"]==st.session_state.user]

    if len(owned)<3:

        name=st.text_input("Nom tunnel")
        description=st.text_area("Description")
        public=st.checkbox("Tunnel public")

        avatar=st.file_uploader("Photo tunnel",type=["png","jpg","jpeg"])

        if st.button("Créer tunnel"):

            code=str(uuid.uuid4())[:8]

            groups.append({
            "id":str(uuid.uuid4()),
            "name":name,
            "creator":st.session_state.user,
            "description":description,
            "public":public,
            "code":code,
            "photo":avatar.getvalue() if avatar else None,
            "members":[st.session_state.user],
            "messages":[]
            })

            save(FILES["groups"],groups)

            st.success(f"Tunnel créé | code : {code}")

            st.rerun()

    else:
        st.warning("Limite de 3 tunnels créés")

    st.divider()

    st.subheader("Rejoindre tunnel")

    join_code=st.text_input("Code invitation")

    if st.button("Rejoindre"):

        for g in groups:

            if g["code"]==join_code:

                if st.session_state.user not in g["members"]:
                    g["members"].append(st.session_state.user)

        save(FILES["groups"],groups)
        st.rerun()

    st.divider()

    st.subheader("Tunnels publics")

    for g in groups:

        if g["public"]:

            st.write(f"### {g['name']}")
            st.write(g["description"])
            st.write(f"Membres : {len(g['members'])}")

            if st.session_state.user in g["members"]:

                if st.button("Ne plus suivre",key=g["id"]):

                    g["members"].remove(st.session_state.user)
                    save(FILES["groups"],groups)
                    st.rerun()

            else:

                if st.button("Suivre",key=g["id"]):

                    g["members"].append(st.session_state.user)
                    save(FILES["groups"],groups)
                    st.rerun()

            st.divider()