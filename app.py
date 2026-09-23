import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import feedparser

BASE = Path(__file__).parent
DB = BASE / "data" / "campana.db"
DB.parent.mkdir(exist_ok=True)

st.set_page_config(page_title="Centro de Comunicaciones", page_icon="📡", layout="wide")

def db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS intelligence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, title TEXT, source TEXT, url TEXT,
        topic TEXT, sentiment TEXT, priority TEXT, notes TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, title TEXT, source TEXT, url TEXT,
        topic TEXT, status TEXT, notes TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, channel TEXT, format TEXT, topic TEXT,
        brief TEXT, draft TEXT, status TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS press (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, journalist TEXT, outlet TEXT, contact TEXT,
        topic TEXT, status TEXT, notes TEXT
    )""")
    conn.commit()
    return conn

def add(table, fields, values):
    conn = db()
    qs = ",".join(["?"] * len(values))
    conn.execute(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({qs})", values)
    conn.commit()
    conn.close()

def read_table(table):
    conn = db()
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY id DESC", conn)
    conn.close()
    return df

def rss_items(url):
    feed = feedparser.parse(url)
    rows = []
    for e in feed.entries[:30]:
        rows.append({
            "title": e.get("title",""),
            "source": feed.feed.get("title","RSS"),
            "url": e.get("link",""),
            "published": e.get("published","")
        })
    return rows

db()

st.title("📡 Centro de Comunicaciones")
st.caption("MVP — Inteligencia · Monitoreo · Contenidos · Prensa")

menu = st.sidebar.radio("Módulo", [
    "🏠 Panel",
    "🧠 1. Inteligencia",
    "📰 2. Monitoreo de medios",
    "✍️ 5. Producción de contenidos",
    "🎙️ 7. Prensa"
])

if menu == "🏠 Panel":
    intel = read_table("intelligence")
    media = read_table("media")
    content = read_table("content")
    press = read_table("press")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Inteligencia", len(intel))
    c2.metric("Monitoreo", len(media))
    c3.metric("Contenidos", len(content))
    c4.metric("Contactos prensa", len(press))

    st.subheader("Últimos movimientos")
    for name, df in [("Inteligencia", intel), ("Medios", media), ("Contenidos", content)]:
        if not df.empty:
            st.markdown(f"**{name}**")
            st.dataframe(df.head(5), use_container_width=True, hide_index=True)

elif menu == "🧠 1. Inteligencia":
    st.header("🧠 Inteligencia comunicacional")
    st.write("Registro estructurado de hechos, temas, declaraciones y señales que requieren seguimiento.")

    with st.form("intel"):
        title = st.text_input("Título / hecho")
        source = st.text_input("Fuente")
        url = st.text_input("URL")
        topic = st.text_input("Tema")
        sentiment = st.selectbox("Tipo de mención", ["Positiva", "Neutral", "Negativa", "No clasificada"])
        priority = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
        notes = st.text_area("Notas / contexto verificable")
        ok = st.form_submit_button("Guardar")
        if ok and title:
            add("intelligence",
                ["created_at","title","source","url","topic","sentiment","priority","notes"],
                [datetime.now().isoformat(timespec="minutes"),title,source,url,topic,sentiment,priority,notes])
            st.success("Registro guardado.")

    st.divider()
    df = read_table("intelligence")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "📰 2. Monitoreo de medios":
    st.header("📰 Monitoreo de medios")
    st.write("Puedes cargar fuentes RSS y convertir sus titulares en una bandeja de seguimiento.")

    rss = st.text_input("URL de fuente RSS", placeholder="https://ejemplo.com/rss")
    if st.button("Consultar RSS") and rss:
        try:
            items = rss_items(rss)
            if not items:
                st.warning("No se encontraron entradas.")
            else:
                for item in items:
                    with st.container(border=True):
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"{item['source']} · {item['published']}")
                        if item["url"]:
                            st.markdown(item["url"])
                        if st.button("Guardar en monitoreo", key=item["url"]):
                            add("media",
                                ["created_at","title","source","url","topic","status","notes"],
                                [datetime.now().isoformat(timespec="minutes"), item["title"], item["source"], item["url"], "", "Pendiente", ""])
                            st.success("Guardado.")
        except Exception as e:
            st.error(f"No se pudo consultar RSS: {e}")
    st.divider()
    st.subheader("Fuentes configuradas")
    st.info("En la siguiente fase podemos crear un catálogo de fuentes, actualización automática, deduplicación y alertas.")

    df = read_table("media")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "✍️ 5. Producción de contenidos":
    st.header("✍️ Producción de contenidos")
    st.write("Convierte un hecho o actividad en piezas para distintos canales.")

    with st.form("content"):
        channel = st.multiselect("Canales", ["Instagram", "Facebook", "X", "TikTok", "WhatsApp", "Prensa"])
        fmt = st.selectbox("Formato", ["Post", "Reel/Video", "Historia", "Hilo", "Comunicado", "Mensaje WhatsApp"])
        topic = st.text_input("Tema")
        brief = st.text_area("Brief / información de partida")
        draft = st.text_area("Borrador", height=220)
        status = st.selectbox("Estado", ["Idea", "En redacción", "Para revisión", "Aprobado", "Publicado"])
        ok = st.form_submit_button("Guardar contenido")
        if ok and brief:
            add("content",
                ["created_at","channel","format","topic","brief","draft","status"],
                [datetime.now().isoformat(timespec="minutes"), ", ".join(channel), fmt, topic, brief, draft, status])
            st.success("Contenido guardado.")

    st.divider()
    df = read_table("content")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

elif menu == "🎙️ 7. Prensa":
    st.header("🎙️ Sala de prensa")
    st.write("Base de contactos y seguimiento de oportunidades periodísticas.")

    with st.form("press"):
        journalist = st.text_input("Periodista")
        outlet = st.text_input("Medio")
        contact = st.text_input("Correo / teléfono")
        topic = st.text_input("Tema de interés")
        status = st.selectbox("Estado", ["Sin contacto", "Contactado", "Entrevista pendiente", "Entrevista realizada", "Publicado"])
        notes = st.text_area("Notas")
        ok = st.form_submit_button("Guardar contacto")
        if ok and journalist:
            add("press",
                ["created_at","journalist","outlet","contact","topic","status","notes"],
                [datetime.now().isoformat(timespec="minutes"), journalist, outlet, contact, topic, status, notes])
            st.success("Contacto guardado.")

    st.divider()
    df = read_table("press")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
