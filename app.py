import streamlit as st
from streamlit_autorefresh import st_autorefresh

import hashlib
import time
import uuid
import base64
import math

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Free_Kogossa",
    page_icon="🇬🇦",
    layout="centered"
)

# =====================================================
# STYLE
# =====================================================

st.markdown("""
<style>

.stApp{
background:#0e1117;
color:white;
}

.msg{
padding:12px;
border-radius:12px;
background:#1c1c1c;
margin-bottom:10px;
border-left:4px solid #00c853;
}

.tunnel{
background:#161b22;
padding:10px;
border-radius:12px;
margin-bottom:10px;
}

</style>
""",unsafe_allow_html=True)

# =====================================================
# CRYPTO LIGHT
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:16]

    @staticmethod
    def encrypt(data):
        return base64.b64encode(data).decode()

    @staticmethod
    def decrypt(data):

        try:
            return base64.b64decode(data)
        except:
            return None

# =====================================================
# GLOBAL NODE
# =====================================================

@st.cache_resource
def get_node():

    return {

        "messages":{},
        "likes":{},
        "groups":{},
        "presence":{}

    }

NODE=get_node()

# =====================================================
# LOGIN
# =====================================================

if "uid" not in st.session_state:

    st.title("🇬🇦 Free_Kogossa")

    pseudo=st.text_input("Pseudo")
    code=st.text_input("Code tunnel",type="password")

    if st.button("Entrer"):

        if pseudo and code:

            st.session_state.uid=f"{pseudo}#{uuid.uuid4().hex[:3]}"
            st.session_state.secret=code

            st.rerun()

    st.stop()

# =====================================================
# INIT
# =====================================================

uid=st.session_state.uid
secret=st.session_state.secret
sid=SOVEREIGN.tunnel(secret)

NODE["messages"].setdefault(sid,[])
NODE["likes"].setdefault(sid,{})
NODE["groups"].setdefault(sid,{
    "name":"Mon tunnel",
    "desc":"",
    "public":True,
    "members":[uid],
    "avatar":None
})

# =====================================================
# PRESENCE
# =====================================================

now=time.time()

NODE["presence"][uid]={
"ts":now,
"sid":sid
}

online=[u for u,d in NODE["presence"].items()
        if now-d["ts"]<30 and d["sid"]==sid]

# =====================================================
# HEADER
# =====================================================

st.title("🇬🇦 Free_Kogossa")

st.write(f"🟢 {len(online)} membres en ligne")

tab1,tab2,tab3=st.tabs(
["💬 Discussion","📢 Actu","🌐 Communautés"]
)

# =====================================================
# DISCUSSION
# =====================================================

with tab1:

    group=NODE["groups"][sid]

    st.markdown("<div class='tunnel'>",unsafe_allow_html=True)

    if group["avatar"]:
        st.image(group["avatar"],width=80)

    st.write(f"### {group['name']}")
    st.write(group["desc"])
    st.write(f"Membres : {len(group['members'])}")

    st.markdown("</div>",unsafe_allow_html=True)

    msg=st.text_input("Message",key="msg_input")

    media=st.file_uploader(
        "Image / vidéo",
        type=["jpg","png","jpeg","mp4"]
    )

    if st.button("Envoyer message"):

        if msg or media:

            data=msg.encode() if msg else media.getvalue()
            typ="text" if msg else media.type

            mid=str(uuid.uuid4())

            NODE["messages"][sid].append({

                "id":mid,
                "u":uid,
                "d":SOVEREIGN.encrypt(data),
                "t":typ,
                "ts":time.time()

            })

            NODE["likes"][sid][mid]=0

            st.rerun()

    st.divider()

    for m in reversed(NODE["messages"][sid][-50:]):

        raw=SOVEREIGN.decrypt(m["d"])

        if raw:

            st.markdown(f"**{m['u']}**")

            if m["t"]=="text":

                st.markdown(
                f"<div class='msg'>{raw.decode()}</div>",
                unsafe_allow_html=True)

            elif "image" in m["t"]:
                st.image(raw)

            elif "video" in m["t"]:
                st.video(raw)

            if st.button("❤️",key=m["id"]):

                NODE["likes"][sid][m["id"]]+=1
                st.rerun()

            st.write(
            f"{NODE['likes'][sid][m['id']]} likes"
            )

# =====================================================
# ACTU
# =====================================================

with tab2:

    st.subheader("Publier actu")

    text=st.text_area("Texte")

    img=st.camera_input("Photo")

    video=st.file_uploader(
        "Vidéo",
        type=["mp4"]
    )

    if st.button("Publier"):

        NODE["messages"][sid].append({

            "id":str(uuid.uuid4()),
            "u":uid,
            "d":SOVEREIGN.encrypt(
                text.encode() if text else img.getvalue()
            ),
            "t":"text" if text else "image",
            "ts":time.time()

        })

        st.rerun()

# =====================================================
# COMMUNAUTES
# =====================================================

with tab3:

    st.subheader("Gestion des tunnels")

    g=NODE["groups"][sid]

    name=st.text_input("Nom tunnel",value=g["name"])
    desc=st.text_area("Description",value=g["desc"])

    public=st.checkbox(
        "Tunnel public",
        value=g["public"]
    )

    avatar=st.file_uploader(
        "Photo tunnel",
        type=["png","jpg","jpeg"]
    )

    if st.button("Mettre à jour tunnel"):

        g["name"]=name
        g["desc"]=desc
        g["public"]=public

        if avatar:
            g["avatar"]=avatar.getvalue()

        st.rerun()

    st.divider()

    st.write("Code invitation")

    st.code(secret)

    if st.button("Quitter tunnel"):

        st.session_state.clear()
        st.rerun()

# =====================================================
# AUTO REFRESH
# =====================================================

st_autorefresh(
interval=3000,
key="refresh"
)