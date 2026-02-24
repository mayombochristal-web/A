import streamlit as st
import uuid, time, json, base64, hashlib, requests

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="GEN-Z ATTRACTOR",
    page_icon="🌍",
    layout="centered"
)

SYNC_DELAY = 5

# =====================================================
# UTILS
# =====================================================

def safe(x):
    return json.loads(json.dumps(x))

def enc(b):
    return base64.b64encode(b).decode()

def dec(s):
    return base64.b64decode(s.encode())

def dm_id(a,b):
    return hashlib.sha256("".join(sorted([a,b])).encode()).hexdigest()[:16]

# =====================================================
# USER INIT
# =====================================================

if "USER" not in st.session_state:

    name = st.text_input("Ton pseudo 🌟")

    if name:
        st.session_state.USER={
            "id":uuid.uuid4().hex[:8],
            "name":name
        }
        st.rerun()

    st.stop()

USER=st.session_state.USER

# =====================================================
# NODE STATE
# =====================================================

if "NODE" not in st.session_state:
    st.session_state.NODE={
        "global":{"version":0,"messages":[]},
        "dms":{},
        "subs":{},
        "discover":{},
        "seen":set(),
        "last_sync":0
    }

NODE=st.session_state.NODE

BASE_URL = st.query_params.get("base","LOCAL")

# =====================================================
# API
# =====================================================

if st.query_params.get("api")=="state":
    st.json(safe({
        "user":USER,
        "global":NODE["global"],
        "dms":NODE["dms"]
    }))
    st.stop()

# =====================================================
# MERGE SAFE
# =====================================================

def add_msg(container,msg):
    if msg["id"] in NODE["seen"]:
        return
    NODE["seen"].add(msg["id"])
    container.append(msg)

def merge(remote):

    for m in remote["global"]["messages"]:
        add_msg(NODE["global"]["messages"],m)

    for tid,chat in remote["dms"].items():

        if tid not in NODE["dms"]:
            NODE["dms"][tid]=chat
        else:
            for m in chat["messages"]:
                add_msg(NODE["dms"][tid]["messages"],m)

# =====================================================
# SYNC
# =====================================================

def sync():

    now=time.time()
    if now-NODE["last_sync"]<SYNC_DELAY:
        return

    for url in NODE["subs"].values():

        try:
            r=requests.get(url+"?api=state",timeout=3)
            data=r.json()

            NODE["discover"][data["user"]["id"]]={
                "name":data["user"]["name"],
                "url":url
            }

            merge(data)

        except:
            pass

    NODE["last_sync"]=now

sync()

# =====================================================
# SEND
# =====================================================

def post_global(text,typ,data):
    msg={
        "id":uuid.uuid4().hex,
        "user":USER["name"],
        "type":typ,
        "data":data,
        "ts":time.time()
    }
    add_msg(NODE["global"]["messages"],msg)

def post_dm(target_id,text):

    tid=dm_id(USER["id"],target_id)

    if tid not in NODE["dms"]:
        NODE["dms"][tid]={
            "users":[USER["id"],target_id],
            "messages":[]
        }

    msg={
        "id":uuid.uuid4().hex,
        "user":USER["name"],
        "type":"text",
        "data":text,
        "ts":time.time()
    }

    add_msg(NODE["dms"][tid]["messages"],msg)

# =====================================================
# UI
# =====================================================

st.title("🌍 GEN-Z ATTRACTOR")

tabs=st.tabs(["🏠 Global","➕ Publier","💬 Privé","👥 Découvrir","👤 Profil"])

# =====================================================
# GLOBAL
# =====================================================

with tabs[0]:

    feed=sorted(NODE["global"]["messages"],
                key=lambda x:x["ts"],
                reverse=True)

    for m in feed:
        st.subheader(m["user"])

        if m["type"]=="text":
            st.write(m["data"])
        elif m["type"]=="image":
            st.image(dec(m["data"]))
        elif m["type"]=="audio":
            st.audio(dec(m["data"]))

        st.divider()

# =====================================================
# PUBLIER
# =====================================================

with tabs[1]:

    scope=st.radio("Visibilité",["Public 🌍","Privé 💬"])

    mode=st.radio("Type",["Texte","Image","Vocal"],horizontal=True)

    if scope=="Public 🌍":

        if mode=="Texte":
            txt=st.text_area("Message")
            if st.button("Publier"):
                post_global(txt,"text",txt)
                st.rerun()

        elif mode=="Image":
            f=st.file_uploader("Image")
            if f and st.button("Publier image"):
                post_global("", "image",enc(f.getvalue()))
                st.rerun()

        elif mode=="Vocal":
            a=st.audio_input("Vocal")
            if a and st.button("Publier vocal"):
                post_global("", "audio",enc(a.getvalue()))
                st.rerun()

    else:
        st.info("Choisis une personne dans Privé 💬")

# =====================================================
# DM
# =====================================================

with tabs[2]:

    if not NODE["discover"]:
        st.info("Ajoute quelqu’un dans Découvrir.")

    for uid,data in NODE["discover"].items():

        st.subheader(data["name"])

        tid=dm_id(USER["id"],uid)

        msgs=NODE["dms"].get(tid,{"messages":[]})["messages"]

        for m in msgs:
            st.write(f"{m['user']} : {m['data']}")

        msg=st.text_input("Message",key=tid)

        if st.button("Envoyer",key=tid+"btn"):
            post_dm(uid,msg)
            st.rerun()

        st.divider()

# =====================================================
# DISCOVER
# =====================================================

with tabs[3]:

    url=st.text_input("Ajouter un node")

    if st.button("Suivre"):
        NODE["subs"][uuid.uuid4().hex[:6]]=url
        st.success("Abonné ✅")

    for d in NODE["discover"].values():
        st.write("👤",d["name"])

# =====================================================
# PROFILE
# =====================================================

with tabs[4]:

    st.subheader(USER["name"])
    st.write("ID :",USER["id"])

    link=f"{BASE_URL}?node={USER['id']}&url={BASE_URL}"
    st.code(link)

# =====================================================
# REFRESH
# =====================================================

time.sleep(4)
st.rerun()
