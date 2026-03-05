import streamlit as st
from cryptography.fernet import Fernet
from streamlit_autorefresh import st_autorefresh

import hashlib
import time
import uuid
import base64
import math
import re

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Free Kongossa",
    page_icon="🔥",
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

.story{
background:#161b22;
padding:10px;
border-radius:10px;
margin-bottom:10px;
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
        refresh=7000
    elif phi<0.6:
        refresh=4000
    elif phi<0.85:
        refresh=2000
    else:
        refresh=1000

    return phi,gamma,refresh

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
        "comments":{},
        "reposts":{},
        "stories":{},
        "followers":{},
        "hashtags":{},
        "live":{},
        "live_chat":{},
        "ttu":{}

    }

NODE=get_node()

# =====================================================
# LOGIN
# =====================================================

if "uid" not in st.session_state:

    st.title("🔥 Free Kongossa")

    pseudo=st.text_input("Pseudo")
    secret=st.text_input("Code Tunnel",type="password")

    if st.button("Entrer"):

        if pseudo and secret:

            st.session_state.uid=f"{pseudo}#{uuid.uuid4().hex[:3]}"
            st.session_state.secret=secret

            st.rerun()

    st.stop()

# =====================================================
# INIT
# =====================================================

secret=st.session_state.secret
sid=SOVEREIGN.tunnel(secret)

NODE["messages"].setdefault(sid,[])
NODE["likes"].setdefault(sid,{})
NODE["comments"].setdefault(sid,{})
NODE["reposts"].setdefault(sid,{})
NODE["live"].setdefault(sid,None)
NODE["live_chat"].setdefault(sid,[])
NODE["stories"].setdefault(sid,[])
NODE["followers"].setdefault(st.session_state.uid,set())
NODE["ttu"].setdefault(sid,{"rho":0.2,"tick":0})

TTU=NODE["ttu"][sid]

# =====================================================
# PRESENCE
# =====================================================

now=time.time()

NODE["presence"][st.session_state.uid]={"ts":now,"sid":sid}

active=[u for u,d in NODE["presence"].items()
        if now-d["ts"]<30 and d["sid"]==sid]

# =====================================================
# PUSH POST
# =====================================================

def push(data,typ):

    mid=str(uuid.uuid4())

    text=data.decode() if typ=="text" else ""

    hashtags=re.findall(r"#(\w+)",text)

    NODE["messages"][sid].append({

        "id":mid,
        "u":st.session_state.uid,
        "d":SOVEREIGN.encrypt(secret,data),
        "t":typ,
        "ts":time.time()

    })

    NODE["likes"][sid][mid]=0
    NODE["comments"][sid][mid]=[]
    NODE["reposts"][sid][mid]=0

    for h in hashtags:

        NODE["hashtags"].setdefault(h,0)
        NODE["hashtags"][h]+=1

# =====================================================
# STORIES 24H
# =====================================================

def push_story(data):

    NODE["stories"][sid].append({

        "u":st.session_state.uid,
        "d":SOVEREIGN.encrypt(secret,data),
        "ts":time.time()

    })

# =====================================================
# VIRAL SCORE
# =====================================================

def score(m):

    likes=NODE["likes"][sid][m["id"]]
    reposts=NODE["reposts"][sid][m["id"]]

    age=time.time()-m["ts"]

    return likes*3 + reposts*5 - age/500

# =====================================================
# UI HEADER
# =====================================================

st.title("🔥 Free Kongossa")

st.write(f"🟢 {len(active)} en ligne")

# =====================================================
# STORIES
# =====================================================

st.subheader("📸 Stories 24h")

for s in NODE["stories"][sid]:

    if time.time()-s["ts"]<86400:

        raw=SOVEREIGN.decrypt(secret,s["d"])

        if raw:

            st.markdown(f"**{s['u']}**")
            st.image(raw)

story=st.camera_input("Poster une story")

if story and st.button("Publier story"):

    push_story(story.getvalue())
    st.rerun()

# =====================================================
# POST CREATION
# =====================================================

txt=st.text_area("Exprime toi...")

if st.button("Publier"):

    if txt:

        push(txt.encode(),"text")
        st.rerun()

# =====================================================
# LIVE
# =====================================================

st.divider()

if NODE["live"][sid] is None:

    if st.button("🔴 Démarrer Live"):

        NODE["live"][sid]=st.session_state.uid
        st.rerun()

else:

    st.success(f"🔴 LIVE par {NODE['live'][sid]}")

    for c in NODE["live_chat"][sid][-30:]:

        st.write(f"**{c['u']}** : {c['t']}")

    msg=st.text_input("Chat live")

    if st.button("Envoyer chat"):

        NODE["live_chat"][sid].append({

            "u":st.session_state.uid,
            "t":msg

        })

        st.rerun()

# =====================================================
# FEED VIRAL
# =====================================================

st.divider()

posts=sorted(NODE["messages"][sid],key=score,reverse=True)

for m in posts[-60:]:

    raw=SOVEREIGN.decrypt(secret,m["d"])

    if raw:

        st.markdown(f"**{m['u']}**")

        st.markdown(
        f"<div class='msg'>{raw.decode()}</div>",
        unsafe_allow_html=True)

        col1,col2,col3=st.columns(3)

        if col1.button("❤️",key=m["id"]):

            NODE["likes"][sid][m["id"]]+=1
            st.rerun()

        if col2.button("🔁",key="r"+m["id"]):

            NODE["reposts"][sid][m["id"]]+=1
            push(raw,"text")
            st.rerun()

        col3.write(
        f"{NODE['likes'][sid][m['id']]} ❤️ | {NODE['reposts'][sid][m['id']]} 🔁"
        )

        # commentaires
        with st.expander("💬 commentaires"):

            for c in NODE["comments"][sid][m["id"]]:

                st.write(f"**{c['u']}** : {c['t']}")

            new=st.text_input("commenter",key="c"+m["id"])

            if st.button("envoyer",key="b"+m["id"]):

                NODE["comments"][sid][m["id"]].append({

                    "u":st.session_state.uid,
                    "t":new

                })

                st.rerun()

# =====================================================
# HASHTAGS TRENDING
# =====================================================

st.divider()

st.subheader("🔥 Trending")

for h,c in sorted(
NODE["hashtags"].items(),
key=lambda x:x[1],
reverse=True)[:10]:

    st.write(f"#{h} ({c})")

# =====================================================
# TTU
# =====================================================

TTU["tick"]+=1

phi,gamma,refresh=ttu_update(
TTU["rho"],TTU["tick"])

st.progress(phi)

# =====================================================
# AUTO REFRESH
# =====================================================

st_autorefresh(
interval=refresh,
key="refresh"
)