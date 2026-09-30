"""Run manually only: streamlit run web/auto_highlights/prototype_app.py"""
import streamlit as st
from web.auto_highlights.creator_hub_ui import render_auto_highlights_prototype

st.set_page_config(page_title="GSF Auto Highlights prototype",layout="centered")
sample=[{"title":"FC27 — Live 30 settembre","highlights":[
 {"id":"1","score_percent":94,"reason":"reazione","start_seconds":6130},
 {"id":"2","score_percent":89,"reason":"azione","start_seconds":8200},
 {"id":"3","score_percent":84,"reason":"picco audio","start_seconds":10280},
]}]
render_auto_highlights_prototype(st,connected_twitch=True,folders=sample)
