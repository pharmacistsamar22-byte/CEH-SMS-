# -*- coding: utf-8 -*-
"""صفحة: لوحة التحكم (owner فقط)"""

import streamlit as st

from common import LOCATION_TEXT, TOX_MAIN_TEXT, inject_css, load_entries, require_login, show_logo, sidebar_user_box

st.set_page_config(page_title="لوحة التحكم — CEHSMS", page_icon="📊", layout="wide")
inject_css()
require_login()
sidebar_user_box()
show_logo(width=80)

if not st.session_state.get("is_owner"):
    st.error("🔒 لوحة التحكم متاحة لمالك النظام فقط.")
    st.stop()

st.header("📊 لوحة التحكم")
entries = load_entries()

if entries.empty:
    st.info("لا توجد بيانات كافية لعرض لوحة التحكم بعد.")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("إجمالي الحالات", len(entries))
c2.metric("إجمالي عدد المصابين", int(entries["casualty_count"].astype(float).sum()))
c3.metric("تحتاج إزالة تلوث", int((entries["needs_decon"] == "yes").sum()))
c4.metric("تحتاج فريق HAZMAT", int((entries["needs_hazmat_team"] == "yes").sum()))
c5.metric("حالات حرجة", int((entries["severity"] == "critical").sum()))

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("توزيع الحالات حسب درجة الخطورة")
    st.bar_chart(entries["severity"].value_counts())

    st.subheader("توزيع الحالات حسب مكان الإصابة")
    loc_counts = entries["location"].map(lambda x: LOCATION_TEXT.get(x, x)).value_counts()
    st.bar_chart(loc_counts)

with col2:
    st.subheader("توزيع الحالات حسب التصنيف السمي")
    if "tox_class_main" in entries.columns:
        tox_counts = entries["tox_class_main"].map(lambda x: TOX_MAIN_TEXT.get(x, x)).value_counts()
        st.bar_chart(tox_counts)

    st.subheader("أكثر المواد تكرارًا")
    st.bar_chart(entries["material"].value_counts().head(10))
