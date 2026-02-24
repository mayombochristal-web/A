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

.msg-box{
padding:14px;
border-radius:14px;
background:#1e1e1e;
margin-bottom:10px;
border-left:5px solid #2e7d32;
}

.login-box{
padding:25px;
border-radius:15px;
background:#161b22;
text-align:center;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TTU ENGINE (ANTI CRASH)
# =====================================================

def ttu_update(rho, tick):

    K = 25 + 5 * math.sin(tick * 0.2)

    phi = 0.5 + 0.5 * math.tanh(2.5 * (rho - 0.4)) - (K / 200)
    phi = max(0, min(1, phi))

    gamma = math.exp(-4 * phi)

    # temps adaptatif TTU
    if phi < 0.3:
        phase = "😴 Tunnel calme"
        refresh = 7
    elif phi < 0.6:
        phase = "🟢 Discussions actives"
        refresh = 4
    elif phi < 0.85:
        phase = "⚡ Tunnel chaud"
        refresh = 2
    else:
        phase = "🔥 VIRAL"
        refresh = 1

    return phi, gamma, phase, K, refresh

# =====================================================
# CRYPTO
# =====================================================

class SOVEREIGN:

    @staticmethod
    def tunnel(secret):
        return hashlib.sha256(secret.encode()).hexdigest()[:20]

    @staticmethod
    def key(secret):
        k = hashlib.pbkdf2_hmac(
            "sha256", secret.encode(),
            b"GABON-SOVEREIGN", 150000
        )
        return base64.urlsafe_b64encode(k[:32])

    @staticmethod
    def encrypt(secret, data):
        f = Fernet(SOVEREIGN.key(secret))
        return base64.b64encode(f.encrypt(data)).decode()

    @staticmethod
    def decrypt(secret, data):
        try:
            f = Fernet(SOVEREIGN.key(secret))
            return f.decrypt(base64.b64decode(data))
        except:
            return None

# =====================================================
# NODE GLOBAL
# =====================================================

@st.cache_resource
def get_node():
    return {"TUNNELS": {}, "PRESENCE": {}, "TTU": {}}

NODE = get_node()

# =====================================================
# LOGIN PREMIÈRE PAGE
# =====================================================

if "uid" not in st.session_state:

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.title("🇬🇦 GEN-Z GABON")
    st.subheader("FREE-KONGOSSA")

    pseudo = st.text_input("Pseudo")
    secret = st.text_input("Code Tunnel Secret", type="password")

    if st.button("ENTRER LE TUNNEL", use_container_width=True):
        if pseudo and secret:
            st.session_state.uid = f"🇬🇦 {pseudo}#{uuid.uuid4().hex[:3]}"
            st.session_state.secret = secret
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =====================================================
# INIT SESSION
# =====================================================

secret = st.session_state.secret
sid = SOVEREIGN.tunnel(secret)

NODE["TUNNELS"].setdefault(sid, [])
NODE["TTU"].setdefault(sid, {"rho":0.2,"tick":0})

TTU = NODE["TTU"][sid]

# =====================================================
# PRESENCE
# =====================================================

now = time.time()
NODE["PRESENCE"][st.session_state.uid] = {"ts": now, "sid": sid}

active_now = [
    u for u,d in NODE["PRESENCE"].items()
    if now-d["ts"] < 30 and d["sid"] == sid
]

# =====================================================
# MESSAGE PUSH (SAFE)
# =====================================================

def push(data):

    NODE["TUNNELS"][sid].append({
        "u": st.session_state.uid,
        "d": SOVEREIGN.encrypt(secret,data),
        "ts": time.time()
    })

    # mémoire circulaire anti crash
    NODE["TUNNELS"][sid] = NODE["TUNNELS"][sid][-150:]

    TTU["rho"] = min(1.2, TTU["rho"] + 0.02)

# =====================================================
# UI PRINCIPALE
# =====================================================

st.title("🏠 Flux Souverain")
st.write(f"🟢 {len(active_now)} membres en ligne")

msg = st.text_input("Parler au tunnel")

if st.button("Envoyer"):
    if msg:
        push(msg.encode())
        st.rerun()

st.divider()

# =====================================================
# TTU UPDATE
# =====================================================

TTU["tick"] += 1

phi, gamma, phase, K, refresh = ttu_update(
    TTU["rho"], TTU["tick"]
)

TTU["rho"] *= 0.996

# =====================================================
# DASHBOARD TTU
# =====================================================

with st.expander("🔥 État du Tunnel"):

    st.progress(phi)
    st.metric("Phase", phase)
    st.metric("Synchronisation", f"{(1-gamma)*100:.1f}%")

# =====================================================
# FLUX
# =====================================================

for m in reversed(NODE["TUNNELS"][sid][-40:]):

    raw = SOVEREIGN.decrypt(secret,m["d"])

    if raw:
        st.markdown(f"**{m['u']}**")
        st.markdown(
            f"<div class='msg-box'>{raw.decode()}</div>",
            unsafe_allow_html=True
        )

# =====================================================
# HORLOGE TTU ADAPTATIVE (ANTI CRASH)
# =====================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

if time.time() - st.session_state.last_refresh > refresh:
    st.session_state.last_refresh = time.time()
    time.sleep(0.2)
    st.rerun()