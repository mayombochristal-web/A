# SAFE IMPORT WEBRTC
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode
    WEBRTC_AVAILABLE = True
except:
    WEBRTC_AVAILABLE = False
import streamlit as st
from cryptography.fernet import Fernet
import hashlib, time, uuid, base64, json, math

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
.stApp {background:#0e1117;color:white;}

.status-box{
padding:10px;border-radius:10px;
border:1px solid #00ff88;
background:#001a00;text-align:center;font-weight:bold;
}

.msg-box{
padding:15px;border-radius:15px;background:#1e1e1e;
margin-bottom:10px;border-left:5px solid #2e7d32;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TTU ENGINE
# =====================================================

def ttu_update(rho,tick):

    K=25+5*math.sin(tick*0.2)

    phi=0.5+0.5*math.tanh(2.5*(rho-0.4))-(K/200)
    phi=max(0,min(1,phi))

    gamma=math.exp(-4*phi)

    if phi<0.3:
        phase="😴 Calme"
    elif phi<0.6:
        phase="🟢 Actif"
    elif phi<0.85:
        phase="⚡ Chaud"
    else:
        phase="🔥 VIRAL"

    return phi,gamma,phase,K

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
        f=Fernet(SOVEREIGN.key(secret))
        c=f.encrypt(data)
        n=len(c)
        return [
            base64.b64encode(c[:n//3]).decode(),
            base64.b64encode(c[n//3:2*n//3]).decode(),
            base64.b64encode(c[2*n//3:]).decode()
        ]

    @staticmethod
    def decrypt(secret,frags):
        try:
            f=Fernet(SOVEREIGN.key(secret))
            combined=b"".join(base64.b64decode(x) for x in frags)
            return f.decrypt(combined)
        except:
            return None

# =====================================================
# GLOBAL NODE
# =====================================================

@st.cache_resource
def get_node():
    return {
        "TUNNELS":{},
        "PRESENCE":{},
        "TTU":{},
        "LIVE":{},
        "LAST_TICK":time.time()
    }

NODE=get_node()

# =====================================================
# SIDEBAR LOGIN
# =====================================================

st.sidebar.title("🇬🇦 GEN-Z GABON")

pseudo=st.sidebar.text_input("Pseudo")
secret=st.sidebar.text_input("Code Tunnel",type="password")

if st.sidebar.button("Entrer") and pseudo and secret:
    st.session_state.uid=f"🇬🇦 {pseudo}#{uuid.uuid4().hex[:3]}"
    st.session_state.secret=secret
    st.rerun()

if "uid" not in st.session_state:
    st.title("🔥 FREE-KONGOSSA")
    st.stop()

secret=st.session_state.secret
sid=SOVEREIGN.tunnel(secret)

NODE["TUNNELS"].setdefault(sid,[])
NODE["LIVE"].setdefault(sid,None)

NODE["TTU"].setdefault(sid,{
    "rho":0.2,"tick":0,"phi":0.5,"gamma":1,"phase":"Init"
})

TTU=NODE["TTU"][sid]

# =====================================================
# PRESENCE
# =====================================================

now=time.time()
NODE["PRESENCE"][st.session_state.uid]={"ts":now,"sid":sid}

active_now=[u for u,d in NODE["PRESENCE"].items()
            if now-d["ts"]<30 and d["sid"]==sid]

# =====================================================
# HORLOGE TTU
# =====================================================

if now-NODE["LAST_TICK"]>3:
    NODE["LAST_TICK"]=now

    TTU["tick"]+=1
    phi,gamma,phase,K=ttu_update(TTU["rho"],TTU["tick"])

    TTU["phi"]=phi
    TTU["gamma"]=gamma
    TTU["phase"]=phase

    TTU["rho"]=0.98*TTU["rho"]+0.02*(len(active_now)/5)

# =====================================================
# UI
# =====================================================

st.title("🏠 Flux Souverain")

st.markdown(
f"<div class='status-box'>🟢 {len(active_now)} membres en ligne</div>",
unsafe_allow_html=True)

# =====================================================
# PUSH
# =====================================================

def push(data,typ):

    frags=SOVEREIGN.encrypt(secret,data)

    NODE["TUNNELS"][sid].append({
        "u":st.session_state.uid,
        "f":frags,
        "t":typ,
        "ts":time.time()
    })

    NODE["TUNNELS"][sid]=NODE["TUNNELS"][sid][-300:]

    TTU["rho"]=min(1.2,TTU["rho"]+0.03)

# =====================================================
# PUBLICATION + LIVE
# =====================================================

with st.expander("➕ PUBLIER / LIVE",expanded=True):

    tab1,tab2,tab3,tab4=st.tabs(
        ["💬 Texte","📷 Caméra","🎤 Micro","🎥 LIVE"]
    )

    # TEXT
    with tab1:
        txt=st.text_area("Message")
        if st.button("Envoyer texte"):
            if txt:
                push(txt.encode(),"text")
                st.rerun()

    # CAMERA
    with tab2:
        img=st.camera_input("Prendre photo")
        file=st.file_uploader("ou télécharger",type=["png","jpg","mp4"])

        if img and st.button("Publier photo"):
            push(img.getvalue(),"image/jpeg")
            st.rerun()

        if file and st.button("Publier fichier"):
            push(file.getvalue(),file.type)
            st.rerun()

    # MICRO
    with tab3:
        audio=st.audio_input("Enregistrer vocal")

        if audio and st.button("Envoyer vocal"):
            push(audio.getvalue(),"audio/wav")
            st.rerun()

    # LIVE MODE
    with tab4:

        if NODE["LIVE"][sid] is None:

            if st.button("🔴 Démarrer LIVE"):
                NODE["LIVE"][sid]=st.session_state.uid
                st.rerun()

        else:
            st.warning(f"🔴 LIVE par {NODE['LIVE'][sid]}")

            frame=st.camera_input("LIVE caméra")

            if frame:
                push(frame.getvalue(),"image/jpeg")

            if st.button("⛔ Stop LIVE"):
                NODE["LIVE"][sid]=None
                st.rerun()

# =====================================================
# DASHBOARD TTU
# =====================================================

with st.expander("🔥 État du Tunnel"):
    st.progress(TTU["phi"])
    st.metric("Phase",TTU["phase"])

# =====================================================
# FLUX
# =====================================================

for m in reversed(NODE["TUNNELS"][sid][-40:]):

    raw=SOVEREIGN.decrypt(secret,m["f"])

    if raw:
        st.markdown(
        f"**{m['u']}** • {time.strftime('%H:%M',time.localtime(m['ts']))}")

        if m["t"]=="text":
            st.markdown(
            f"<div class='msg-box'>{raw.decode()}</div>",
            unsafe_allow_html=True)
        elif "image" in m["t"]:
            st.image(raw)
        elif "video" in m["t"]:
            st.video(raw)
        else:
            st.audio(raw)

# =====================================================
# REFRESH INTELLIGENT
# =====================================================

if "refresh" not in st.session_state:
    st.session_state.refresh=0

if time.time()-st.session_state.refresh>5:
    st.session_state.refresh=time.time()
    st.rerun()
