import streamlit as st
import uuid, time, json, base64, requests

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="GEN-Z GABON • V20",
    page_icon="🇬🇦",
    layout="centered"
)

SYNC_INTERVAL = 6

# =====================================================
# SAFE JSON
# =====================================================

def safe(obj):
    return json.loads(json.dumps(obj))

def b64e(b):
    return base64.b64encode(b).decode()

def b64d(s):
    return base64.b64decode(s.encode())

# =====================================================
# NODE INIT
# =====================================================

if "NODE" not in st.session_state:
    st.session_state.NODE = {
        "ID": uuid.uuid4().hex[:8],
        "TUNNELS": {"public":{"version":0,"messages":[]}},
        "SUBS": {},
        "LAST_SYNC": 0,
        "PUBLIC": False
    }

NODE = st.session_state.NODE

BASE_URL = st.query_params.get("base","LOCAL")

# =====================================================
# AUTO SUBSCRIBE VIA LINK
# =====================================================

if "node" in st.query_params:
    nid = st.query_params["node"]
    url = st.query_params.get("url","")
    if nid and url:
        NODE["SUBS"][nid]=url

# =====================================================
# API MODE
# =====================================================

if st.query_params.get("api")=="state":
    st.json(safe({
        "ID":NODE["ID"],
        "TUNNELS":NODE["TUNNELS"]
    }))
    st.stop()

# =====================================================
# SYNC ENGINE
# =====================================================

def merge(remote):
    for t,data in remote.items():
        if t not in NODE["TUNNELS"]:
            NODE["TUNNELS"][t]=data
        else:
            if data["version"]>NODE["TUNNELS"][t]["version"]:
                NODE["TUNNELS"][t]=data

def auto_sync():
    now=time.time()
    if now-NODE["LAST_SYNC"]<SYNC_INTERVAL:
        return

    for nid,url in list(NODE["SUBS"].items()):
        try:
            r=requests.get(url+"?api=state",timeout=3)
            data=r.json()
            merge(data["TUNNELS"])
        except:
            pass

    NODE["LAST_SYNC"]=now

auto_sync()

# =====================================================
# UI
# =====================================================

st.title("🇬🇦 GEN-Z GABON — V20")

tabs=st.tabs(["💬 Signaux","➕ Nouveau signal","🌐 Nodes","👤 Mon node"])

# =====================================================
# SIGNaux
# =====================================================

with tabs[0]:

    msgs=NODE["TUNNELS"]["public"]["messages"]

    for m in reversed(msgs):

        st.caption(m["user"])

        if m["type"]=="text":
            st.write(m["data"])

        elif m["type"]=="image":
            st.image(b64d(m["data"]))

        elif m["type"]=="audio":
            st.audio(b64d(m["data"]))

# =====================================================
# NOUVEAU SIGNAL (UX V16)
# =====================================================

with tabs[1]:

    mode=st.radio(
        "Type",
        ["Texte","Image","Vocal"],
        horizontal=True
    )

    def push(data,typ):
        t=NODE["TUNNELS"]["public"]
        t["version"]+=1
        t["messages"].append({
            "id":uuid.uuid4().hex,
            "user":NODE["ID"],
            "type":typ,
            "data":data,
            "ts":time.time()
        })

    if mode=="Texte":
        txt=st.text_area("Message")
        if st.button("Envoyer"):
            push(txt,"text")
            st.rerun()

    elif mode=="Image":
        f=st.file_uploader("Image")
        if f and st.button("Envoyer image"):
            push(b64e(f.getvalue()),"image")
            st.rerun()

    elif mode=="Vocal":
        a=st.audio_input("Micro")
        if a and st.button("Envoyer vocal"):
            push(b64e(a.getvalue()),"audio")
            st.rerun()

# =====================================================
# NODES
# =====================================================

with tabs[2]:

    st.subheader("S'abonner à un node")

    url=st.text_input("URL du node")

    if st.button("S'abonner"):
        nid=uuid.uuid4().hex[:6]
        NODE["SUBS"][nid]=url
        st.success("Node ajouté ✅")

    st.divider()

    st.subheader("Nodes suivis")

    for nid,url in NODE["SUBS"].items():
        st.write(f"🟢 {nid} → {url}")

# =====================================================
# MON NODE
# =====================================================

with tabs[3]:

    st.write("ID Node :",NODE["ID"])

    share_link=f"?node={NODE['ID']}&url={BASE_URL}"

    st.code(share_link)

    st.caption("Partage ce lien pour que quelqu’un s’abonne automatiquement.")

# =====================================================
# AUTO REFRESH
# =====================================================

time.sleep(4)
st.rerun()
