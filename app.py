import streamlit as st
import uuid, time, json, base64, requests

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="GEN-Z SOCIAL V21",
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

# =====================================================
# INIT USER
# =====================================================

if "USER" not in st.session_state:

    pseudo = st.text_input("Choisis ton pseudo ✨")

    if pseudo:
        st.session_state.USER = {
            "id": uuid.uuid4().hex[:8],
            "name": pseudo
        }
        st.rerun()

    st.stop()

USER = st.session_state.USER

# =====================================================
# NODE
# =====================================================

if "NODE" not in st.session_state:
    st.session_state.NODE = {
        "posts": [],
        "dms": {},
        "subs": {},
        "discover": {},
        "last_sync": 0
    }

NODE = st.session_state.NODE

BASE_URL = st.query_params.get("base","LOCAL")

# =====================================================
# API STATE
# =====================================================

if st.query_params.get("api")=="state":
    st.json(safe({
        "user":USER,
        "posts":NODE["posts"]
    }))
    st.stop()

# =====================================================
# SYNC
# =====================================================

def sync():
    now=time.time()
    if now-NODE["last_sync"]<SYNC_DELAY:
        return

    for url in list(NODE["subs"].values()):
        try:
            r=requests.get(url+"?api=state",timeout=3)
            data=r.json()

            NODE["discover"][data["user"]["id"]] = {
                "name":data["user"]["name"],
                "url":url
            }

            for p in data["posts"]:
                if p["id"] not in [x["id"] for x in NODE["posts"]]:
                    NODE["posts"].append(p)

        except:
            pass

    NODE["last_sync"]=now

sync()

# =====================================================
# UI
# =====================================================

st.title("🌍 GEN-Z SOCIAL")

tabs = st.tabs(["🏠 Accueil","➕ Publier","💬 Discussions","👥 Découvrir","👤 Profil"])

# =====================================================
# ACCUEIL (FEED)
# =====================================================

with tabs[0]:

    feed = sorted(NODE["posts"], key=lambda x:x["ts"], reverse=True)

    if not feed:
        st.info("Ajoute des amis dans Découvrir 👥")

    for p in feed:
        st.subheader(p["user"])
        if p["type"]=="text":
            st.write(p["data"])
        elif p["type"]=="image":
            st.image(dec(p["data"]))
        elif p["type"]=="audio":
            st.audio(dec(p["data"]))

        st.divider()

# =====================================================
# PUBLIER
# =====================================================

with tabs[1]:

    mode = st.radio("Publier",["Texte","Image","Vocal"],horizontal=True)

    def publish(data,typ):
        NODE["posts"].append({
            "id":uuid.uuid4().hex,
            "user":USER["name"],
            "type":typ,
            "data":data,
            "ts":time.time()
        })

    if mode=="Texte":
        txt=st.text_area("Exprime toi...")
        if st.button("Publier"):
            publish(txt,"text")
            st.rerun()

    elif mode=="Image":
        f=st.file_uploader("Image")
        if f and st.button("Publier image"):
            publish(enc(f.getvalue()),"image")
            st.rerun()

    elif mode=="Vocal":
        a=st.audio_input("Message vocal")
        if a and st.button("Publier vocal"):
            publish(enc(a.getvalue()),"audio")
            st.rerun()

# =====================================================
# DISCUSSIONS (DM AUTO)
# =====================================================

with tabs[2]:

    if not NODE["dms"]:
        st.info("Clique sur un profil dans Découvrir pour discuter.")

    for uid,chat in NODE["dms"].items():
        st.subheader(chat["name"])

        for m in chat["msgs"]:
            st.write(m)

        msg=st.text_input(f"Message à {chat['name']}",key=uid)

        if st.button("Envoyer",key=uid+"btn"):
            chat["msgs"].append(f"{USER['name']} : {msg}")
            st.rerun()

# =====================================================
# DECOUVRIR
# =====================================================

with tabs[3]:

    url = st.text_input("Ajouter un ami (URL node)")

    if st.button("Suivre"):
        NODE["subs"][uuid.uuid4().hex[:6]] = url
        st.success("Abonné ✅")

    st.divider()

    for uid,data in NODE["discover"].items():

        col1,col2=st.columns([3,1])

        with col1:
            st.write("👤",data["name"])

        with col2:
            if st.button("Message",key=uid):
                if uid not in NODE["dms"]:
                    NODE["dms"][uid]={
                        "name":data["name"],
                        "msgs":[]
                    }

# =====================================================
# PROFIL
# =====================================================

with tabs[4]:

    st.subheader(USER["name"])
    st.write("ID :",USER["id"])

    share = f"?node={USER['id']}&url={BASE_URL}"

    st.code(share)
    st.caption("Partage ce lien pour que tes amis te suivent.")

# =====================================================
# AUTO REFRESH
# =====================================================

time.sleep(4)
st.rerun()
