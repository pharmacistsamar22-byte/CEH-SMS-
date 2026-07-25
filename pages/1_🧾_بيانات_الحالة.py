# -*- coding: utf-8 -*-
"""صفحة: بيانات الحالة (تسجيل حالة جديدة)"""

from datetime import datetime

import pandas as pd
import streamlit as st

from common import (
    DECON_TEXT, HAZMAT_TEXT, LOCATION_TEXT, NO_MATERIAL_LABEL,
    OTHER_MATERIAL_LABEL, ROUTE_TEXT, SEVERITY_TEXT, TOX_MAIN_TEXT, TOX_SUB_OPTIONS,
    add_new_material, build_mailto_link, inject_css, load_entries, load_sds_database_cached,
    require_login, save_entries, sds_file_size_limit, show_logo, sidebar_user_box,
    storage_backend,
)

st.set_page_config(page_title="بيانات الحالة — CEHSMS", page_icon="🧾", layout="wide")
inject_css()
require_login()
sidebar_user_box()

show_logo(width=80)
st.header("🧾 بيانات الحالة")
if storage_backend() == "local":
    st.caption("💾 وضع التخزين الحالي: محلي (غير دائم على الاستضافة السحابية) — راجع إعدادات Google Sheets في README.")

# إشعار نجاح إضافة مادة جديدة (من السايكل السابق) + رابط إخطار المالك بالبريد
if st.session_state.get("material_added_notify"):
    info = st.session_state.pop("material_added_notify")
    st.success("✅ تمت إضافة المادة بنجاح — بانتظار اعتماد المسؤول.")
    if info.get("email"):
        link = build_mailto_link(info["email"], info["subject"], info["body"])
        st.markdown(f"[📧 اضغط هنا لفتح بريدك وإرسال طلب الموافقة إلى {info['email']}]({link})")

sds_db = load_sds_database_cached()
material_names = [NO_MATERIAL_LABEL] + [m["name"] for m in sds_db] + [OTHER_MATERIAL_LABEL]

# لو مادة جديدة اتضافت في السايكل اللي فات، نختارها تلقائيًا في القائمة
# (لازم يحصل ده قبل إنشاء عنصر selectbox المرتبط بنفس الـ key)
if "pending_new_material_name" in st.session_state:
    pending_name = st.session_state.pop("pending_new_material_name")
    if pending_name in material_names:
        st.session_state["material_select"] = pending_name

# ------------------------------------------------------------------------
# اختيار التصنيف السمي والمادة *خارج* الفورم حتى تتحدث القوائم فورًا
# ------------------------------------------------------------------------
st.subheader("التصنيف السمي للمادة")
tcol1, tcol2 = st.columns(2)
with tcol1:
    tox_main = st.selectbox(
        "الفئة الرئيسية", list(TOX_MAIN_TEXT.keys()),
        format_func=lambda k: TOX_MAIN_TEXT[k], key="tox_main_select",
    )
with tcol2:
    tox_sub = st.selectbox(
        "الفئة الفرعية", TOX_SUB_OPTIONS[tox_main], key="tox_sub_select_" + tox_main,
    )

st.subheader("المادة المشتبه بها")
material_sel = st.selectbox("اختر من القائمة أو أضف مادة جديدة", material_names, key="material_select")

if material_sel == OTHER_MATERIAL_LABEL:
    st.info("مادة غير موجودة بالقاعدة — يمكنك إضافتها الآن، وستُحفظ بحالة **بانتظار اعتماد المسؤول**.")
    with st.expander("➕ إضافة مادة جديدة", expanded=True):
        nm_name = st.text_input("اسم المادة *", key="nm_name")
        nm_trade = st.text_input("الاسم التجاري", key="nm_trade")
        nm_cas = st.text_input("رقم CAS (إن وجد)", key="nm_cas")
        nm_hazard = st.text_area("خطورة التعرض / التأثير الصحي", key="nm_hazard")
        nm_storage = st.text_input("شروط التخزين", key="nm_storage")
        nm_ppe = st.text_input("معدات الوقاية الشخصية اللازمة", key="nm_ppe")
        nm_firstaid = st.text_area("الإسعافات الأولية", key="nm_firstaid")
        st.caption(
            f"📎 يمكن رفع ملف SDS الخاص بالمادة (PDF) — الحد الأقصى للحجم في وضع "
            f"التخزين الحالي: {sds_file_size_limit() // 1000} كيلوبايت تقريبًا. "
            f"الملف سيكون متاحًا للتحميل لباقي المستخدمين **بعد اعتماد المالك فقط**."
        )
        nm_sds_file = st.file_uploader("رفع ملف SDS (PDF) — اختياري", type=["pdf"], key="nm_sds_file")
        owner_email = st.text_input(
            "بريد مسؤول النظام لإخطاره بالإضافة (اختياري)", key="nm_owner_email",
            placeholder="owner@hospital.com",
        )
        if st.button("💾 حفظ المادة الجديدة"):
            if not nm_name.strip():
                st.error("من فضلك اكتب اسم المادة أولًا.")
            else:
                sds_file_bytes = None
                sds_file_name = None
                if nm_sds_file is not None:
                    file_bytes = nm_sds_file.getvalue()
                    if len(file_bytes) > sds_file_size_limit():
                        st.warning(
                            f"⚠ حجم الملف ({len(file_bytes)//1000} كيلوبايت) أكبر من الحد "
                            f"المسموح به ({sds_file_size_limit()//1000} كيلوبايت) في وضع "
                            "التخزين الحالي. سيتم حفظ بيانات المادة بدون إرفاق الملف."
                        )
                    else:
                        sds_file_bytes = file_bytes
                        sds_file_name = nm_sds_file.name
                item = add_new_material(
                    sds_db, nm_name.strip(), nm_trade.strip(), nm_cas.strip(),
                    tox_main, tox_sub, nm_firstaid.strip(), nm_hazard.strip(),
                    nm_ppe.strip(), nm_storage.strip(),
                    added_by=st.session_state.username,
                    sds_file_bytes=sds_file_bytes, sds_file_name=sds_file_name,
                )
                # نخزّن اسم المادة الجديدة في session_state عشان تُختار تلقائيًا
                # في القائمة بعد إعادة تشغيل الصفحة (rerun) — لازم كده عشان
                # الحقول (زي material_select) بتتصفّر بعد كل تفاعل جديد
                st.session_state["pending_new_material_name"] = item["name"]
                notify = {"email": owner_email.strip()}
                if owner_email.strip():
                    body = (
                        f"تمت إضافة مادة كيميائية جديدة تحتاج مراجعة واعتماد رسمي:\n\n"
                        f"اسم المادة: {item['name']}\n"
                        f"الاسم التجاري: {item['trade']}\n"
                        f"رقم CAS: {item['cas']}\n"
                        f"التصنيف: {TOX_MAIN_TEXT[tox_main]} — {tox_sub}\n"
                        f"الإسعافات الأولية: {item['firstAid']}\n\n"
                        f"تمت الإضافة بواسطة: {st.session_state.username}\n"
                        f"التاريخ: {item['addedAt']}\n\n"
                        f"برجاء مراجعة قاعدة بيانات SDS واعتماد إدراجها بشكل نهائي."
                    )
                    notify["subject"] = f"طلب موافقة على إضافة مادة كيميائية جديدة — {item['name']}"
                    notify["body"] = body
                st.session_state["material_added_notify"] = notify
                st.rerun()
# عرض ملخص المادة المختارة (لو مادة معروفة بالفعل)
selected_item = None
if material_sel not in (NO_MATERIAL_LABEL, OTHER_MATERIAL_LABEL):
    selected_item = next((m for m in sds_db if m["name"] == material_sel), None)
    if selected_item:
        pending_badge = ' <span class="pending-tag">بانتظار الاعتماد</span>' if selected_item.get("pendingApproval") else ""
        st.markdown(f"### ⚕ الإسعافات الأولية — {selected_item['name']}{pending_badge}", unsafe_allow_html=True)
        if selected_item.get("skinDeconMandatory"):
            st.markdown(
                '<div class="decon-alert">🛑 إزالة التلوث إلزامية: طريقة وصول المادة عن طريق الجلد '
                '— يجب غسل جيد بالماء وخلع الملابس الملوثة فورًا</div>',
                unsafe_allow_html=True,
            )
        st.write(selected_item["firstAid"])
        st.caption(
            f"NFPA — الصحة: {selected_item['nfpa']['h']} · الاشتعال: {selected_item['nfpa']['f']} "
            f"· التفاعلية: {selected_item['nfpa']['r']} · مهمات الوقاية: {selected_item['ppe']}"
        )

st.divider()

# ------------------------------------------------------------------------
# فورم بيانات الحالة (بدون خانة المادة/التصنيف، عشان دي بتتحدث فورًا برّه الفورم)
# ------------------------------------------------------------------------
with st.form("new_case_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        hospital_name = st.text_input("اسم المستشفى *")
        incident_date = st.date_input("📅 تاريخ الحادث", value=datetime.now().date())
        incident_time = st.time_input("⏰ وقت الحادث", value=datetime.now().time())
        patient = st.text_input("اسم المريض / الحالة *")
        patient_gender = st.selectbox("النوع", ["ذكر", "أنثى"])
        patient_age = st.number_input("العمر", min_value=0, max_value=120, step=1)
        patient_profession = st.text_input("المهنة")
    with c2:
        location = st.selectbox(
            "مكان الإصابة", list(LOCATION_TEXT.keys()),
            format_func=lambda k: LOCATION_TEXT[k],
        )
        casualty_count = st.number_input("عدد المصابين", min_value=1, step=1, value=1)
        route = st.selectbox(
            "طريقة وصول المادة *", list(ROUTE_TEXT.keys()),
            format_func=lambda k: ROUTE_TEXT[k],
        )
        severity = st.selectbox(
            "درجة الخطورة", list(SEVERITY_TEXT.keys()),
            format_func=lambda k: SEVERITY_TEXT[k],
        )

    notes = st.text_area("الوصف / الأعراض / الإجراء المتخذ")

    c3, c4 = st.columns(2)
    with c3:
        needs_decon = st.selectbox(
            "الحاجة لإزالة التلوث (Decontamination)",
            list(DECON_TEXT.keys()), format_func=lambda k: DECON_TEXT[k],
        )
    with c4:
        needs_hazmat_team = st.selectbox(
            "الحاجة لتفعيل فريق HAZMAT",
            list(HAZMAT_TEXT.keys()), format_func=lambda k: HAZMAT_TEXT[k],
        )

    submitted = st.form_submit_button("➕ تسجيل الحالة", use_container_width=True)

if submitted:
    missing = []
    if not hospital_name.strip():
        missing.append("اسم المستشفى")
    if not patient.strip():
        missing.append("اسم المريض")
    if material_sel in (NO_MATERIAL_LABEL, OTHER_MATERIAL_LABEL):
        missing.append("اسم المادة (اختر مادة من القائمة، أو أضف مادة جديدة واحفظها أولًا)")

    if missing:
        st.error("⚠ برجاء تعبئة الحقول الإلزامية التالية: " + "، ".join(missing))
    else:
        material_name_final = material_sel
        item = selected_item
        first_aid = item["firstAid"] if item else ""
        sds_ref = item["cas"] if item else "-"

        entries = load_entries()
        new_row = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "hospital_name": hospital_name,
            "incident_date": str(incident_date),
            "incident_time": incident_time.strftime("%H:%M"),
            "patient": patient,
            "patient_gender": patient_gender,
            "patient_age": patient_age,
            "patient_profession": patient_profession,
            "location": location,
            "casualty_count": casualty_count,
            "material": material_name_final,
            "tox_class_main": tox_main,
            "tox_class_sub": tox_sub,
            "route": route,
            "severity": severity,
            "sds": sds_ref,
            "first_aid": first_aid,
            "needs_decon": needs_decon,
            "needs_hazmat_team": needs_hazmat_team,
            "notes": notes,
            "responder": st.session_state.username,
            "entry_datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        entries = pd.concat([entries, pd.DataFrame([new_row])], ignore_index=True)
        save_entries(entries)
        st.success("تم تسجيل الحالة بنجاح ✅")
        st.balloons()
