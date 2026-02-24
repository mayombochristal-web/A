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
.stApp {background-color:#0e1117;color:white;}

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
# TTU ENGINE (TEMPS DISCRET STABLE)
# =====================================================

def ttu_update(rho, tick):

    K = 25 + 5 * math.sin(tick * 0.2)

    phi = 0.5 + 0.5 * math.tanh(2.5 * (rho - 0.4)) - (K / 200)
    phi = max(0.0, min(1.0, phi))

    gamma = math.exp(-4 * phi)

    if phi < 0.3:
        phase = "😴 Tunnel calme"
    elif phi < 0.6:
        phase = "🟢 Discussions actives"
    elif phi < 0.85:
        phase = "⚡ Tunnel chaud"
    else:
        phase = "🔥 VIRAL"

    return phi, gamma, phase, K

# =====================================================
# CRYPTO ENGINE
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):
        k = hashlib.pbkdf2_hmac(
            "sha256",
            secret.encode(),
            b"GABON-SOVEREIGN",
            150000
        )
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret, data):
        f = Fernet(SOVEREIGN.key(secret))
        c = f.encrypt(data)
        n = len(c)

        return [
            base64.b64encode(c[:n//3]).decode(),
            base64.b64encode(c[n//3:2*n//3]).decode(),
            base64.b64encode(c[2*n//3:]).decode()
        ]

    @staticmethod
    def decrypt(secret, frags):
        try:
            f = Fernet(SOVEREIGN.key(secret))
            combined = b"".join(base64.b64decode(x) for x in frags)
            return f.decrypt(combined)
        except:
            return None

# =====================================================
# GLOBAL NODE (ANTI CRASH)
# =====================================================

@st.cache_resource
def get_node():
    return {
        "TUNNELS": {},
        "PRESENCE": {},
        "TTU": {},
        "CLOCK": 0,
        "LAST_TICK": time.time()
    }

NODE = get_node()

# =====================================================
# SIDEBAR LOGIN (PSEUDO + CODE MEME PAGE)
# =====================================================

st.sidebar.title("🇬🇦 GEN-Z GABON")

pseudo = st.sidebar.text_input("Pseudo")
secret = st.sidebar.text_input("Code Tunnel", type="password")

enter = st.sidebar.button("Entrer")

if enter and pseudo and secret:
    st.session_state.uid = f"🇬🇦 {pseudo}#{uuid.uuid4().hex[:3]}"
    st.session_state.secret = secret
    st.rerun()

if "uid" not in st.session_state:
    st.title("🔥 FREE-KONGOSSA")
    st.info("Entre ton pseudo et le code tunnel dans la barre latérale.")
    st.stop()

secret = st.session_state.secret
sid = SOVEREIGN.tunnel(secret)

# =====================================================
# INIT TUNNEL
# =====================================================

NODE["TUNNELS"].setdefault(sid, [])
NODE["TTU"].setdefault(sid,
    {"rho":0.2,"tick":0,"phi":0.5,"gamma":1,"phase":"Init"}
)

TTU = NODE["TTU"][sid]

# =====================================================
# PRESENCE
# =====================================================

now = time.time()

NODE["PRESENCE"][st.session_state.uid] = {"ts":now,"sid":sid}

active_now = [
    u for u,d in NODE["PRESENCE"].items()
    if now-d["ts"] < 30 and d["sid"] == sid
]

# =====================================================
# TTU GLOBAL CLOCK (CLE ANTI CRASH)
# =====================================================

if now - NODE["LAST_TICK"] > 3:
    NODE["LAST_TICK"] = now
    NODE["CLOCK"] += 1

    TTU["tick"] += 1

    phi,gamma,phase,K = ttu_update(TTU["rho"],TTU["tick"])

    TTU["phi"]=phi
    TTU["gamma"]=gamma
    TTU["phase"]=phase

    TTU["rho"] = 0.98*TTU["rho"] + 0.02*(len(active_now)/5)

# =====================================================
# UI
# =====================================================

st.title("🏠 Flux Souverain")

st.markdown(
f"<div class='status-box'>🟢 {len(active_now)} Membres en ligne</div>",
unsafe_allow_html=True)

st.caption(f"Tunnel ID : {sid}")

# =====================================================
# PUSH MESSAGE (SAFE)
# =====================================================

def push(data, typ):

    frags = SOVEREIGN.encrypt(secret, data)

    NODE["TUNNELS"][sid].append({
        "u":st.session_state.uid,
        "f":frags,
        "t":typ,
        "ts":time.time()
    })

    # limite mémoire HARD (anti crash majeur)
    if len(NODE["TUNNELS"][sid]) > 300:
        NODE["TUNNELS"][sid] = NODE["TUNNELS"][sid][-300:]

    TTU["rho"] = min(1.2, TTU["rho"] + 0.03)

# =====================================================
# PUBLICATION
# =====================================================

with st.expander("➕ PUBLIER", expanded=True):

    txt = st.text_area("Message")

    if st.button("Envoyer", use_container_width=True):
        if txt:
            push(txt.encode(),"text")
            st.rerun()

# =====================================================
# DASHBOARD TTU
# =====================================================

with st.expander("🔥 État du Tunnel"):

    st.progress(TTU["phi"])

    col1,col2 = st.columns(2)
    col1.metric("📡 Synchronisation",
                f"{(1-TTU['gamma'])*100:.1f}%")
    col2.metric("Phase", TTU["phase"])

# =====================================================
# FLUX (AFFICHAGE LEGER)
# =====================================================

for m in reversed(NODE["TUNNELS"][sid][-40:]):

    raw = SOVEREIGN.decrypt(secret,m["f"])

    if raw:
        st.markdown(
        f"**{m['u']}** • {time.strftime('%H:%M',time.localtime(m['ts']))}")

        if m["t"]=="text":
            st.markdown(
            f"<div class='msg-box'>{raw.decode()}</div>",
            unsafe_allow_html=True)

# =====================================================
# REFRESH TTU INTELLIGENT
# =====================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

if time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()