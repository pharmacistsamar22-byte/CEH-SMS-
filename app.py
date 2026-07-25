# -*- coding: utf-8 -*-
"""
نظام تتبع الحالات الكيميائية والحرجة (HAZMAT Tracker)
Chemical Emergency & Hospital Safety Management System (CEHSMS)
نسخة Python / Streamlit — تطبيق متعدد الصفحات
"""

import streamlit as st

from common import USERS, inject_css, show_logo

st.set_page_config(
    page_title="نظام تتبع الحالات الكيميائية والحرجة",
    page_icon="⚠️",
    layout="wide",
)

# ‼️ لازم تتنادى في كل صفحة (مش بس هنا) — راجع common.inject_css للتفاصيل
inject_css()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login_screen():
    show_logo(width=140)
    st.title("⚠️ نظام تتبع الحالات الكيميائية والحرجة")
    st.caption("Chemical Emergency & Hospital Safety Management System — CEHSMS")
    st.divider()
    with st.form("login_form"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True)
    if submitted:
        record = USERS.get(u)
        if record and record["pass"] == p:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.role = record["role"]
            st.session_state.is_owner = record["is_owner"]
            st.success("تم تسجيل الدخول، جارِ التحويل...")
            st.switch_page("pages/1_🧾_بيانات_الحالة.py")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")


if st.session_state.logged_in:
    show_logo(width=100)
    st.success(f"مرحبًا **{st.session_state.username}** — استخدم القائمة الجانبية للتنقل بين الصفحات.")
    st.page_link("pages/1_🧾_بيانات_الحالة.py", label="🧾 بيانات الحالة", icon="🧾")
    st.page_link("pages/2_📋_متابعة_الحالة.py", label="📋 متابعة الحالة", icon="📋")
    if st.session_state.get("is_owner"):
        st.page_link("pages/3_📊_لوحة_التحكم.py", label="📊 لوحة التحكم", icon="📊")
    st.page_link("pages/4_🐍_لدغات_الأفاعي_والعقارب.py", label="🐍🦂 لدغات الأفاعي والعقارب", icon="🐍")
    st.page_link("pages/5_🧪_قاعدة_بيانات_SDS.py", label="🧪 قاعدة بيانات SDS", icon="🧪")
    st.divider()
    if st.button("🚪 تسجيل الخروج"):
        for k in ["logged_in", "username", "role", "is_owner"]:
            st.session_state.pop(k, None)
        st.rerun()
else:
    login_screen()
