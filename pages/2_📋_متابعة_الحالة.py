# -*- coding: utf-8 -*-
"""صفحة: متابعة الحالة — سجل الحالات المسجّلة"""

import streamlit as st

from common import (
    DECON_TEXT, HAZMAT_TEXT, LOCATION_TEXT, ROUTE_TEXT, SEVERITY_TEXT,
    TOX_MAIN_TEXT, build_excel_bytes, inject_css, load_entries, require_login,
    send_email_with_attachment, show_logo, sidebar_user_box, storage_backend,
)

st.set_page_config(page_title="متابعة الحالة — CEHSMS", page_icon="📋", layout="wide")
inject_css()
require_login()
sidebar_user_box()

show_logo(width=80)
st.header("📋 متابعة الحالة — سجل الحالات المسجّلة")
if storage_backend() == "local":
    st.caption("💾 وضع التخزين الحالي: محلي (غير دائم على الاستضافة السحابية) — راجع إعدادات Google Sheets في README.")

entries = load_entries()
is_owner = st.session_state.get("is_owner", False)

if entries.empty:
    st.info("لا توجد حالات مسجّلة بعد.")
    st.stop()

for i, e in entries.iloc[::-1].iterrows():
    sev = e.get("severity", "mild")
    sev_class = {"mild": "sev-0", "moderate": "sev-1",
                 "severe": "sev-2", "critical": "sev-3"}.get(sev, "sev-0")
    with st.container(border=True):
        st.markdown(
            f'<span class="sev-badge {sev_class}">{SEVERITY_TEXT.get(sev, sev)}</span> '
            f'&nbsp; <b>{e.get("time","")}</b> — المستشفى: {e.get("hospital_name","")} '
            f'<span class="datetime-tag">📅 {e.get("incident_date","")} '
            f'⏰ {e.get("incident_time","")}</span>',
            unsafe_allow_html=True,
        )
        if is_owner:
            st.write(
                f"**{e.get('patient','')}** — {e.get('patient_gender','')} — "
                f"العمر: {e.get('patient_age','')} — المهنة: {e.get('patient_profession','')}"
            )
        else:
            st.markdown(
                f"**حالة رقم {i+1}** — 🔒 بيانات المريض الشخصية محجوبة "
                "(متاحة لمالك النظام فقط)"
            )
        st.write(
            f"مكان الإصابة: {LOCATION_TEXT.get(e.get('location',''), e.get('location',''))}"
            f" — عدد المصابين: {e.get('casualty_count','')}"
        )
        st.write(
            f"المادة: {e.get('material','')} — طريقة الوصول: "
            f"{ROUTE_TEXT.get(e.get('route',''), e.get('route',''))}"
        )
        tox_main_val = e.get('tox_class_main', '')
        if tox_main_val:
            st.write(f"التصنيف السمي: {TOX_MAIN_TEXT.get(tox_main_val, tox_main_val)} — {e.get('tox_class_sub','')}")
        st.write(f"إزالة التلوث: {DECON_TEXT.get(e.get('needs_decon',''), '')} "
                  f"— فريق HAZMAT: {HAZMAT_TEXT.get(e.get('needs_hazmat_team',''), '')}")
        if is_owner:
            if str(e.get("notes", "")).strip() and str(e.get("notes")) != "nan":
                st.write(f"ملاحظات: {e.get('notes')}")
            st.caption(f"المسجّل: {e.get('responder','')} — وقت التسجيل: {e.get('entry_datetime','')}")

st.divider()

if not is_owner:
    st.markdown(
        '<div class="locked-note">🔒 تصدير البيانات وإرسالها بالبريد متاح لمالك النظام فقط، '
        'لأنها تحتوي على بيانات المرضى الحساسة.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# --------------------------------------------------------------------------
# تصدير البيانات (مالك النظام فقط)
# --------------------------------------------------------------------------
st.subheader("📤 تصدير البيانات")

excel_bytes = build_excel_bytes(entries)

c1, c2, c3 = st.columns(3)
with c1:
    st.download_button(
        "⬇️ تحميل Excel", excel_bytes,
        file_name="hazmat_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with c2:
    st.download_button(
        "⬇️ تحميل CSV", entries.to_csv(index=False).encode("utf-8-sig"),
        file_name="hazmat_report.csv", mime="text/csv",
        use_container_width=True,
    )
with c3:
    st.download_button(
        "⬇️ تحميل JSON",
        entries.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"),
        file_name="hazmat_report.json", mime="application/json",
        use_container_width=True,
    )

st.divider()

# --------------------------------------------------------------------------
# إرسال التقرير بالبريد الإلكتروني (SMTP حقيقي)
# --------------------------------------------------------------------------
st.subheader("📧 إرسال التقرير بالبريد الإلكتروني")
st.caption(
    "الإرسال يتم مباشرة من خادم التطبيق عبر SMTP. بيانات الدخول لا تُحفظ على القرص، "
    "وتبقى فقط طوال الجلسة الحالية."
)

with st.form("email_form"):
    ec1, ec2 = st.columns(2)
    with ec1:
        smtp_host = st.text_input("خادم SMTP", value=st.session_state.get("smtp_host", "smtp.gmail.com"))
        smtp_port = st.text_input("المنفذ (Port)", value=st.session_state.get("smtp_port", "587"))
        sender_email = st.text_input("البريد المرسِل", value=st.session_state.get("sender_email", ""))
    with ec2:
        sender_password = st.text_input("كلمة مرور التطبيق (App Password)", type="password")
        recipient_email = st.text_input("البريد المستلم *")
        subject = st.text_input("عنوان الرسالة", value="تقرير حالات HAZMAT")

    body_text = st.text_area("نص الرسالة", value="مرفق تقرير الحالات المسجّلة في نظام CEHSMS.")
    send_btn = st.form_submit_button("📨 إرسال التقرير الآن (Excel مرفق)", use_container_width=True)

if send_btn:
    if not (smtp_host and smtp_port and sender_email and sender_password and recipient_email):
        st.error("⚠ برجاء تعبئة كل بيانات إعدادات البريد والمستلم قبل الإرسال.")
    else:
        st.session_state["smtp_host"] = smtp_host
        st.session_state["smtp_port"] = smtp_port
        st.session_state["sender_email"] = sender_email
        try:
            send_email_with_attachment(
                smtp_host, smtp_port, sender_email, sender_password, recipient_email,
                subject, body_text, attachment_bytes=excel_bytes,
                attachment_filename="hazmat_report.xlsx",
            )
            st.success(f"✅ تم إرسال التقرير بنجاح إلى {recipient_email}")
        except Exception as e:
            st.error(f"❌ فشل الإرسال: {e}")
            st.info(
                "تلميحات شائعة: لو بتستخدم Gmail لازم تفعّل 'App Passwords' من إعدادات الأمان "
                "(مش كلمة مرور الحساب العادية)، وتأكد من صحة اسم الخادم والمنفذ."
            )
