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

.login{
background:#161b22;
padding:30px;
border-radius:15px;
text-align:center;
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
# CRYPTO LIGHT
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

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
        "presence":{},
        "likes":{},
        "ttu":{},
        "posts":{}

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

    if st.button("Entrer"):

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
NODE["ttu"].setdefault(sid,{"rho":0.2,"tick":0})
NODE["posts"].setdefault(sid,[])

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
        "d":SOVEREIGN.encrypt(data),
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
# HEADER
# =====================================================

st.title("🇬🇦 Free_Kogossa")

st.write(f"🟢 {len(active)} membres en ligne")

# =====================================================
# NAVIGATION
# =====================================================

tab_chat,tab_actu,tab_com=st.tabs(
["💬 Discussion","📢 Actu","🌐 Communautés"]
)

# =====================================================
# DISCUSSION
# =====================================================

with tab_chat:

    st.subheader("Tunnel")

    txt=st.text_area("Message",key="msgbox")

    if st.button("Envoyer"):

        if txt:

            push(txt.encode(),"text")
            st.session_state.msgbox=""
            st.rerun()

    st.divider()

    for m in reversed(NODE["messages"][sid][-60:]):

        raw=SOVEREIGN.decrypt(m["d"])

        if raw:

            st.markdown(f"**{m['u']}**")

            if m["t"]=="text":

                st.markdown(
                f"<div class='msg'>{raw.decode()}</div>",
                unsafe_allow_html=True)

            if st.button("❤️",key=m["id"]):

                like(m["id"])
                st.rerun()

            st.write(
            f"{NODE['likes'][sid][m['id']]} likes"
            )

# =====================================================
# ACTU
# =====================================================

with tab_actu:

    st.subheader("📢 Publications")

    post=st.text_area("Exprime toi")

    if st.button("Publier actu"):

        NODE["posts"][sid].append({
        "u":st.session_state.uid,
        "txt":post,
        "ts":time.time()
        })

        st.rerun()

    st.divider()

    for p in reversed(NODE["posts"][sid]):

        st.markdown(f"**{p['u']}**")
        st.write(p["txt"])
        st.caption(time.ctime(p["ts"]))

# =====================================================
# COMMUNAUTÉ
# =====================================================

with tab_com:

    st.subheader("Tunnel Info")

    st.write("ID Tunnel")
    st.code(sid)

    st.write("Code d'accès")
    st.code(secret)

# =====================================================
# TTU
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
# AUTO REFRESH
# =====================================================

st_autorefresh(
interval=refresh,
key="tunnel_refresh"
)