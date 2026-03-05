import streamlit as st
from cryptography.fernet import Fernet
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
    page_title="GEN-Z GABON FREE-KONGOSSA",
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

.login{
background:#161b22;
padding:30px;
border-radius:15px;
text-align:center;
}

.like{
color:#ff4081;
font-size:18px;
}

</style>
""",unsafe_allow_html=True)

# =====================================================
# TTU ENGINE
# =====================================================

def ttu_update(rho,tick):

    K=25+5*math.sin(tick*0.2)

    phi=0.5+0.5*math.tanh(2.5*(rho-0.4))-(K/200)
    phi=max(0,min(1,phi))

    gamma=math.exp(-4*phi)

    if phi<0.3:
        phase="😴 Tunnel calme"
        refresh=7000
    elif phi<0.6:
        phase="🟢 Discussions actives"
        refresh=4000
    elif phi<0.85:
        phase="⚡ Tunnel chaud"
        refresh=2000
    else:
        phase="🔥 VIRAL"
        refresh=1000

    return phi,gamma,phase,K,refresh

# =====================================================
# CRYPTO ENGINE
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):

        k=hashlib.pbkdf2_hmac(
            "sha256",
            secret.encode(),
            b"SOVEREIGN-GABON",
            150000
        )

        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret,data):

        f=Fernet(SOVEREIGN.key(secret))

        return base64.b64encode(
            f.encrypt(data)
        ).decode()

    @staticmethod
    def decrypt(secret,data):

        try:

            f=Fernet(SOVEREIGN.key(secret))

            return f.decrypt(
                base64.b64decode(data)
            )

        except:

            return None

# =====================================================
# GLOBAL NODE
# =====================================================

@st.cache_resource
def get_node():

    return {

        "messages":{},
        "presence":{},
        "likes":{},
        "live":{},
        "ttu":{}

    }

NODE=get_node()

# =====================================================
# LOGIN
# =====================================================

if "uid" not in st.session_state:

    st.markdown("<div class='login'>",unsafe_allow_html=True)

    st.title("🇬🇦 GEN-Z GABON")

    pseudo=st.text_input("Pseudo")
    secret=st.text_input("Code Tunnel",type="password")

    if st.button("ENTRER"):

        if pseudo and secret:

            st.session_state.uid=f"{pseudo}#{uuid.uuid4().hex[:3]}"
            st.session_state.secret=secret

            st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)

    st.stop()

# =====================================================
# INIT
# =====================================================

secret=st.session_state.secret
sid=SOVEREIGN.tunnel(secret)

NODE["messages"].setdefault(sid,[])
NODE["likes"].setdefault(sid,{})
NODE["live"].setdefault(sid,None)
NODE["ttu"].setdefault(sid,{"rho":0.2,"tick":0})

TTU=NODE["ttu"][sid]

# =====================================================
# PRESENCE
# =====================================================

now=time.time()

NODE["presence"][st.session_state.uid]={
"ts":now,
"sid":sid
}

active=[u for u,d in NODE["presence"].items()
        if now-d["ts"]<30 and d["sid"]==sid]

# =====================================================
# MESSAGE PUSH
# =====================================================

def push(data,typ):

    mid=str(uuid.uuid4())

    NODE["messages"][sid].append({

        "id":mid,
        "u":st.session_state.uid,
        "d":SOVEREIGN.encrypt(secret,data),
        "t":typ,
        "ts":time.time()

    })

    NODE["likes"][sid][mid]=0

    NODE["messages"][sid]=NODE["messages"][sid][-200:]

    TTU["rho"]=min(1.3,TTU["rho"]+0.02)

# =====================================================
# LIKE
# =====================================================

def like(mid):

    NODE["likes"][sid][mid]+=1

# =====================================================
# UI
# =====================================================

st.title("🏠 Flux Souverain")

st.write(f"🟢 {len(active)} membres en ligne")

# =====================================================
# POST
# =====================================================

with st.expander("➕ Publier",expanded=True):

    tab1,tab2,tab3,tab4=st.tabs(
        ["💬 Texte","📸 Média","🎙️ Vocal","🔴 Live"]
    )

    # TEXT
    with tab1:

        txt=st.text_area("Message")

        if st.button("Envoyer texte"):

            if txt:

                push(txt.encode(),"text")
                st.rerun()

    # MEDIA
    with tab2:

        img=st.camera_input("Photo")

        file=st.file_uploader(
            "Envoyer média",
            type=["png","jpg","jpeg","mp4"]
        )

        if img and st.button("Publier photo"):

            push(img.getvalue(),"image")
            st.rerun()

        if file and st.button("Publier fichier"):

            push(file.getvalue(),file.type)
            st.rerun()

    # AUDIO
    with tab3:

        audio=st.audio_input("Vocal")

        if audio and st.button("Envoyer vocal"):

            push(audio.getvalue(),"audio")
            st.rerun()

    # LIVE
    with tab4:

        if NODE["live"][sid] is None:

            if st.button("🔴 Start Live"):

                NODE["live"][sid]=st.session_state.uid
                TTU["rho"]+=0.1
                st.rerun()

        else:

            st.success(
                f"🔴 LIVE par {NODE['live'][sid]}"
            )

            if NODE["live"][sid]==st.session_state.uid:

                if st.button("Stop Live"):

                    NODE["live"][sid]=None
                    st.rerun()

st.divider()

# =====================================================
# TTU UPDATE
# =====================================================

TTU["tick"]+=1

phi,gamma,phase,K,refresh=ttu_update(
TTU["rho"],TTU["tick"])

TTU["rho"]*=0.996

with st.expander("🔥 État du tunnel"):

    st.progress(phi)
    st.write(phase)
    st.write(f"Synchronisation {(1-gamma)*100:.1f}%")

# =====================================================
# FEED
# =====================================================

for m in reversed(NODE["messages"][sid][-60:]):

    raw=SOVEREIGN.decrypt(secret,m["d"])

    if raw:

        st.markdown(f"**{m['u']}**")

        if m["t"]=="text":

            st.markdown(
            f"<div class='msg'>{raw.decode()}</div>",
            unsafe_allow_html=True)

        elif m["t"]=="image":

            st.image(raw)

        elif "video" in m["t"]:

            st.video(raw)

        elif m["t"]=="audio":

            st.audio(raw)

        col1,col2=st.columns([1,6])

        with col1:

            if st.button("❤️",
                key=m["id"]):

                like(m["id"])
                st.rerun()

        with col2:

            st.write(
            f"{NODE['likes'][sid][m['id']]} likes"
            )

# =====================================================
# AUTO REFRESH
# =====================================================

st_autorefresh(
interval=refresh,
key="tunnel_refresh"
)