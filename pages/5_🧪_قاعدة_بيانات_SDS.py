# -*- coding: utf-8 -*-
"""صفحة: قاعدة بيانات SDS"""

import streamlit as st

from common import (
    TOX_MAIN_TEXT, TOX_SUB_OPTIONS, inject_css, load_sds_database_cached,
    require_login, show_logo, sidebar_user_box, storage_backend, update_material_approval,
)

st.set_page_config(page_title="قاعدة بيانات SDS — CEHSMS", page_icon="🧪", layout="wide")
inject_css()
require_login()
sidebar_user_box()

show_logo(width=80)
st.header("🧪 قاعدة بيانات SDS")

if storage_backend() == "local":
    st.caption("💾 وضع التخزين الحالي: محلي (غير دائم على الاستضافة السحابية) — راجع إعدادات Google Sheets في README.")

is_owner = st.session_state.get("is_owner", False)
sds_db = load_sds_database_cached()

# --------------------------------------------------------------------------
# قائمة المواد بانتظار الاعتماد (مالك النظام فقط)
# --------------------------------------------------------------------------
pending = [m for m in sds_db if m.get("pendingApproval")]
if is_owner and pending:
    st.warning(f"⚠ يوجد {len(pending)} مادة بانتظار الاعتماد")
    with st.expander(f"📋 مراجعة المواد بانتظار الاعتماد ({len(pending)})", expanded=True):
        for item in list(pending):
            with st.container(border=True):
                st.markdown(f"**{item['name']}** ({item.get('trade','-')})")
                st.caption(f"أُضيفت بواسطة: {item.get('addedBy','-')} في {item.get('addedAt','-')}")
                st.write(f"الإسعافات الأولية: {item.get('firstAid','-')}")
                if item.get("sdsFileB64"):
                    import base64
                    st.download_button(
                        f"📎 معاينة ملف SDS المرفق ({item.get('sdsFileName','sds.pdf')})",
                        data=base64.b64decode(item["sdsFileB64"]),
                        file_name=item.get("sdsFileName", "sds.pdf"),
                        mime="application/pdf",
                        key=f"preview_{item['name']}_{item.get('addedAt','')}",
                    )
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("✅ اعتماد", key=f"approve_{item['name']}"):
                        update_material_approval(item["name"], item.get("addedAt"), approve=True)
                        st.rerun()
                with bc2:
                    if st.button("🗑 رفض وحذف", key=f"reject_{item['name']}"):
                        update_material_approval(item["name"], item.get("addedAt"), approve=False)
                        st.rerun()

st.divider()

# --------------------------------------------------------------------------
# البحث والتصفية
# --------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    search = st.text_input("ابحث باسم المادة (مثال: كلور، ايثانول، ميثانول...)")
with c2:
    tox_filter_main = st.selectbox(
        "تصفية حسب الفئة الرئيسية", ["الكل"] + list(TOX_MAIN_TEXT.keys()),
        format_func=lambda k: "الكل" if k == "الكل" else TOX_MAIN_TEXT[k],
    )
with c3:
    sub_options = ["الكل"] + (TOX_SUB_OPTIONS.get(tox_filter_main, []) if tox_filter_main != "الكل" else [])
    tox_filter_sub = st.selectbox("تصفية حسب الفئة الفرعية", sub_options)

filtered = sds_db
if search.strip():
    s = search.strip()
    filtered = [
        m for m in filtered
        if s in m["name"] or s in m.get("trade", "") or s in m.get("cas", "")
    ]
if tox_filter_main != "الكل":
    filtered = [m for m in filtered if m.get("toxClassMain") == tox_filter_main]
if tox_filter_sub != "الكل":
    filtered = [m for m in filtered if m.get("toxClassSub") == tox_filter_sub]

st.caption(f"عدد المواد: {len(filtered)} من إجمالي {len(sds_db)}")

names = [m["name"] for m in filtered]
if not names:
    st.warning("لا توجد نتائج مطابقة.")
    st.stop()

chosen = st.selectbox("اختر مادة لعرض التفاصيل", names)
item = next(m for m in filtered if m["name"] == chosen)

if item.get("pendingApproval"):
    st.markdown('<span class="pending-tag">⏳ بانتظار اعتماد المسؤول</span>', unsafe_allow_html=True)
if item.get("skinDeconMandatory"):
    st.markdown('<div class="decon-tag">🛑 إزالة تلوث إلزامية</div>', unsafe_allow_html=True)

st.subheader(item["name"])
st.caption(f"{item.get('trade','')} — CAS: {item.get('cas','')}")
st.write(
    f"**التصنيف السمي:** {TOX_MAIN_TEXT.get(item.get('toxClassMain',''), '-')} "
    f"— {item.get('toxClassSub','-')}"
)

c1, c2, c3 = st.columns(3)
c1.metric("NFPA — الصحة", item["nfpa"]["h"])
c2.metric("NFPA — الاشتعال", item["nfpa"]["f"])
c3.metric("NFPA — التفاعلية", item["nfpa"]["r"])

st.write(f"**الحالة الفيزيائية:** {item.get('state','-')}")
st.write(f"**الاستخدامات:** {item.get('uses','-')}")
st.write(f"**التخزين:** {item.get('storage','-')}")
st.write(f"**التسرب/الانسكاب:** {item.get('spill','-')}")
st.write(f"**التأثير على الصحة:** {item.get('health','-')}")

if item.get("skinDeconMandatory"):
    st.markdown(
        '<div class="decon-alert">🛑 إزالة التلوث إلزامية: طريقة وصول المادة '
        'عن طريق الجلد — يجب غسل جيد بالماء وخلع الملابس الملوثة فورًا</div>',
        unsafe_allow_html=True,
    )

st.write(f"**الإسعافات الأولية:** {item.get('firstAid','-')}")
st.write(f"**مهمات الوقاية:** {item.get('ppe','-')}")

# ملف SDS المرفق — يظهر لكل المستخدمين بعد اعتماد المالك فقط
if item.get("sdsFileB64"):
    if not item.get("pendingApproval") or is_owner:
        import base64
        st.download_button(
            f"📎 تحميل ملف SDS المرفق ({item.get('sdsFileName','sds.pdf')})",
            data=base64.b64decode(item["sdsFileB64"]),
            file_name=item.get("sdsFileName", "sds.pdf"),
            mime="application/pdf",
            key=f"download_{item['name']}",
        )
    else:
        st.info("📎 يوجد ملف SDS مرفق بهذه المادة — سيكون متاحًا للتحميل بعد اعتماد المسؤول.")
