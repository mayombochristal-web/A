import streamlit as st
from cryptography.fernet import Fernet
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import hashlib, time, uuid, base64, math

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
.stApp{background:#0e1117;color:white;}
.msg{background:#1e1e1e;padding:10px;
border-radius:10px;margin-bottom:8px;}
</style>
""",unsafe_allow_html=True)

# =====================================================
# TTU ENGINE (ADAPTIVE TIME)
# =====================================================

def ttu_update(rho,tick):

    K=25+5*math.sin(tick*0.2)

    phi=0.5+0.5*math.tanh(2.5*(rho-0.4))-(K/200)
    phi=max(0,min(1,phi))

    gamma=math.exp(-4*phi)

    if phi<0.3:
        phase="😴 CALME"
        refresh=7
    elif phi<0.6:
        phase="🟢 ACTIF"
        refresh=4
    elif phi<0.85:
        phase="⚡ CHAUD"
        refresh=2
    else:
        phase="🔥 VIRAL"
        refresh=1

    return phi,gamma,phase,K,refresh

# =====================================================
# CRYPTO
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):
        k=hashlib.pbkdf2_hmac(
            "sha256",secret.encode(),
            b"GABON-SOVEREIGN",150000)
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret,data):
        return base64.b64encode(
            Fernet(SOVEREIGN.key(secret)).encrypt(data)
        ).decode()

    @staticmethod
    def decrypt(secret,data):
        try:
            return Fernet(
                SOVEREIGN.key(secret)
            ).decrypt(base64.b64decode(data))
        except:
            return None

# =====================================================
# GLOBAL NODE (ANTI CRASH MEMORY)
# =====================================================

@st.cache_resource
def get_node():
    return {
        "TUNNELS":{},
        "PRESENCE":{},
        "TTU":{},
        "LIVE":{}
    }

NODE=get_node()

# =====================================================
# LOGIN UNIQUE PAGE
# =====================================================

st.sidebar.title("🇬🇦 FREE-KONGOSSA")

pseudo=st.sidebar.text_input("Pseudo")
secret=st.sidebar.text_input("Tunnel Secret",type="password")

if st.sidebar.button("Connexion") and pseudo and secret:
    st.session_state.uid=f"{pseudo}#{uuid.uuid4().hex[:3]}"
    st.session_state.secret=secret
    st.rerun()

if "uid" not in st.session_state:
    st.title("GEN-Z GABON")
    st.stop()

secret=st.session_state.secret
sid=SOVEREIGN.tunnel(secret)

NODE["TUNNELS"].setdefault(sid,[])
NODE["LIVE"].setdefault(sid,None)
NODE["TTU"].setdefault(sid,{"rho":0.2,"tick":0})

TTU=NODE["TTU"][sid]

# =====================================================
# PRESENCE TTL
# =====================================================

now=time.time()
NODE["PRESENCE"][st.session_state.uid]={"ts":now,"sid":sid}

active=[u for u,d in NODE["PRESENCE"].items()
        if now-d["ts"]<25 and d["sid"]==sid]

# =====================================================
# MESSAGE PUSH (BATCH SAFE)
# =====================================================

def push(msg):

    NODE["TUNNELS"][sid].append({
        "u":st.session_state.uid,
        "d":SOVEREIGN.encrypt(secret,msg),
        "ts":time.time()
    })

    # mémoire circulaire anti crash
    NODE["TUNNELS"][sid]=NODE["TUNNELS"][sid][-150:]

    TTU["rho"]=min(1.2,TTU["rho"]+0.015)

# =====================================================
# UI
# =====================================================

st.title("🏠 GEN-Z GABON FREE-KONGOSSA")
st.write(f"🟢 {len(active)} en ligne")

msg=st.text_input("Parler au tunnel")

if st.button("Envoyer"):
    if msg:
        push(msg.encode())
        st.rerun()

# =====================================================
# LIVE (DECOUPLÉ)
# =====================================================

st.divider()
st.subheader("🎥 LIVE")

ctx=webrtc_streamer(
    key=f"live-{sid}",
    mode=WebRtcMode.SENDRECV,
    media_stream_constraints={"video":True,"audio":True},
    async_processing=True,
)

if ctx.state.playing:
    NODE["LIVE"][sid]=st.session_state.uid
    TTU["rho"]+=0.005*len(active)

# =====================================================
# TTU CLOCK
# =====================================================

TTU["tick"]+=1

phi,gamma,phase,K,refresh=ttu_update(
    TTU["rho"],
    TTU["tick"]
)

st.progress(phi)
st.metric("État",phase)

# dissipation naturelle
TTU["rho"]*=0.996

# =====================================================
# FLUX (RENDER LIMITÉ)
# =====================================================

for m in reversed(NODE["TUNNELS"][sid][-40:]):

    raw=SOVEREIGN.decrypt(secret,m["d"])

    if raw:
        st.markdown(f"**{m['u']}**")
        st.markdown(
            f"<div class='msg'>{raw.decode()}</div>",
            unsafe_allow_html=True
        )

# =====================================================
# ADAPTIVE REFRESH (ANTI 10K CRASH)
# =====================================================

if "last" not in st.session_state:
    st.session_state.last=0

if time.time()-st.session_state.last>refresh:
    st.session_state.last=time.time()
    time.sleep(0.2)
    st.rerun()