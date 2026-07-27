# -*- coding: utf-8 -*-
"""
common.py — عناصر مشتركة بين كل صفحات نظام CEHSMS
(الثوابت، تحميل/حفظ البيانات، تصدير Excel، إرسال البريد الإلكتروني)
"""

import io
import json
import os
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------
# مسارات الملفات
# --------------------------------------------------------------------------
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
SDS_PATH = os.path.join(APP_DIR, "sds_database.json")
ENTRIES_PATH = os.path.join(DATA_DIR, "entries.csv")

ENTRY_COLUMNS = [
    "time", "hospital_name", "patient", "patient_gender", "patient_age",
    "incident_date", "incident_time",
    "patient_profession", "location", "casualty_count", "material",
    "tox_class_main", "tox_class_sub",
    "route", "severity", "sds", "first_aid", "needs_decon",
    "needs_hazmat_team", "notes", "responder", "entry_datetime",
]

# --------------------------------------------------------------------------
# المستخدمون (Demo فقط — يُفضّل نقلها لـ st.secrets عند النشر الفعلي)
# --------------------------------------------------------------------------
USERS = {
    "owner": {"pass": "Owner#2025", "role": "مالك النظام", "is_owner": True},
    "admin": {"pass": "1234", "role": "قائد الفريق", "is_owner": False},
}

# --------------------------------------------------------------------------
# قوائم النصوص الثابتة
# --------------------------------------------------------------------------
LOCATION_TEXT = {
    "emergency": "قسم الطوارئ",
    "icu": "العناية المركزة",
    "ward": "قسم داخلي",
    "field": "موقع الحادث (ميداني)",
    "other": "أخرى",
}
ROUTE_TEXT = {
    "skin": "عن طريق الجلد",
    "inhalation": "استنشاق",
    "ingestion": "بلع",
    "eye": "العين",
    "injection": "حقن / اختراق",
    "unknown": "غير معروف",
}
SEVERITY_TEXT = {
    "mild": "بسيطة",
    "moderate": "متوسطة",
    "severe": "شديدة",
    "critical": "حرجة",
}
DECON_TEXT = {"yes": "مطلوبة", "no": "غير مطلوبة", "unknown": "غير محدد"}
HAZMAT_TEXT = {"yes": "مطلوب", "no": "غير مطلوب", "unknown": "غير محدد"}

# التصنيف السمي — الفئة الرئيسية والفئة الفرعية
# (مستورد من ملف مستقل toxicology_classification.py يحتوي على 8 فئات رئيسية
#  و38 فئة فرعية وأمثلة مواد إرشادية، على غرار تصنيف مراكز السموم الحديثة)
from toxicology_classification import (  # noqa: E402
    TOX_MAIN as TOX_MAIN_TEXT,
    TOX_SUB as TOX_SUB_OPTIONS,
    TOX_EXAMPLES,
    find_classification_by_substance,
)

OTHER_MATERIAL_LABEL = "➕ مادة أخرى غير موجودة بالقائمة..."
NO_MATERIAL_LABEL = "-- اختر مادة (اختياري) --"

# --------------------------------------------------------------------------
# اللوجو
# --------------------------------------------------------------------------
LOGO_PATH = os.path.join(APP_DIR, "assets", "logo.png")


def show_logo(width=90):
    """يعرض لوجو النظام لو الملف موجود، بدون ما يوقف التطبيق لو مش موجود."""
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=width)


def inject_css():
    """يحقن تنسيق احترافي: خط عربي واضح + محاذاة يمين صحيحة لكل عناصر
    الفورم + هوية بصرية متناسقة مع لوجو CEHSMS + الأنماط المخصّصة (الشارات والتنبيهات).
    ‼️ لازم تتنادى من أول كل صفحة (بما فيها app.py) — Streamlit بيشغّل كل صفحة
    في pages/ كسكريبت مستقل تمامًا، ومفيش وراثة تلقائية للـ CSS من app.py."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

        /* ===== الخط والاتجاه العام ===== */
        html, body, [class*="css"], .stApp, .stMarkdown, p, span, div, label,
        input, textarea, select, button {
            font-family: 'Tajawal', 'Segoe UI', Tahoma, sans-serif !important;
        }
        html, body { direction: rtl; }
        .stApp { background-color: #f7f9fb; }

        /* المحتوى الأساسي: نص وعناوين لليمين */
        [data-testid="stAppViewContainer"] .block-container {
            direction: rtl;
            text-align: right;
        }
        h1, h2, h3, h4, h5, h6 { text-align: right !important; }
        [data-testid="stMarkdownContainer"] { text-align: right; }
        [data-testid="stMarkdownContainer"] p { text-align: right; }

        /* ===== محاذاة عناوين الحقول (Labels) لليمين فعليًا ===== */
        [data-testid="stWidgetLabel"] {
            direction: rtl;
            justify-content: flex-end !important;
            text-align: right !important;
            width: 100%;
        }
        [data-testid="stWidgetLabel"] > label { width: 100%; text-align: right; }
        [data-testid="stWidgetLabel"] p { text-align: right; width: 100%; font-weight: 600; color:#1e2a3a; }

        /* ===== محاذاة محتوى الحقول نفسها ===== */
        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        .stDateInput input, .stTimeInput input {
            direction: rtl;
            text-align: right !important;
        }
        div[data-baseweb="select"] * { direction: rtl; text-align: right !important; }
        div[data-baseweb="select"] > div { justify-content: flex-end; }
        [data-testid="stFileUploaderDropzone"] { direction: rtl; text-align: right; }

        /* ===== شكل الحقول: حواف ناعمة وحدود واضحة ===== */
        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        .stDateInput input, .stTimeInput input, div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border: 1px solid #d3dae3 !important;
            background-color: #ffffff !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
            border-color: #1e3a5f !important;
            box-shadow: 0 0 0 2px rgba(30,58,95,.15) !important;
        }

        /* ===== الأزرار ===== */
        .stButton button, .stFormSubmitButton button, .stDownloadButton button {
            border-radius: 8px !important;
            font-weight: 700 !important;
            padding: .55rem 1.4rem !important;
            transition: all .15s ease-in-out;
        }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
            background-color: #1e3a5f !important;
            border-color: #1e3a5f !important;
        }
        .stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primary"]:hover {
            background-color: #16293f !important;
            transform: translateY(-1px);
        }

        /* ===== العناوين الرئيسية بشكل أوضح ===== */
        h1 { font-weight: 900 !important; color: #1e3a5f !important; font-size: 2rem !important; }
        h2 { font-weight: 700 !important; color: #1e3a5f !important; border-bottom: 3px solid #1e3a5f; padding-bottom: 8px; }
        h3 { font-weight: 700 !important; color: #2c4a6e !important; }

        /* ===== القائمة الجانبية ===== */
        section[data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
            background-color: #16293f;
        }
        section[data-testid="stSidebar"] * { color: #eef2f7 !important; }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] {
            border-radius: 8px;
            margin-bottom: 2px;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
            background-color: rgba(255,255,255,.08);
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.15); }
        section[data-testid="stSidebar"] .stButton button {
            background-color: rgba(255,255,255,.08) !important;
            border: 1px solid rgba(255,255,255,.2) !important;
            color: #fff !important;
            width: 100%;
        }

        /* ===== الحاويات (Containers) بشكل بطاقات احترافية ===== */
        [data-testid="stContainer"] [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
            box-shadow: 0 1px 4px rgba(30,58,95,.08);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border-radius: 12px;
        }

        /* ===== شارات وتنبيهات الحالة (كما كانت) ===== */
        .decon-alert{
            background: rgba(194,54,22,.1);
            border: 2px solid #c23616;
            color: #c23616;
            font-weight:700;
            border-radius:8px;
            padding:10px 14px;
            margin: 8px 0;
        }
        .decon-tag{
            display:inline-block;
            background:#c23616;
            color:#fff;
            font-weight:700;
            font-size:.75rem;
            padding:3px 9px;
            border-radius:6px;
            margin-bottom:6px;
        }
        .pending-tag{
            display:inline-block;
            background:#b8790a;
            color:#fff;
            font-weight:700;
            font-size:.72rem;
            padding:3px 9px;
            border-radius:6px;
            margin-inline-start:6px;
        }
        .locked-note{
            background: rgba(184,121,10,.1);
            border:1px solid #b8790a;
            border-radius:8px;
            padding:10px 14px;
            font-size:.9rem;
        }
        .sev-badge{
            display:inline-block;
            padding:3px 12px;
            border-radius:6px;
            font-size:.8rem;
            font-weight:700;
            color:#fff;
        }
        .datetime-tag{
            display:inline-block;
            background:#eef1f4;
            color:#334;
            font-size:.78rem;
            padding:3px 10px;
            border-radius:6px;
            margin-inline-start:6px;
        }
        .sev-0{ background:#2e8b57; }
        .sev-1{ background:#c9a227; }
        .sev-2{ background:#b8790a; }
        .sev-3{ background:#c23616; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# التخزين الدائم (Google Sheets) — مع رجوع تلقائي للتخزين المحلي
# --------------------------------------------------------------------------
# على Streamlit Community Cloud، أي ملفات تُكتب على القرص المحلي (CSV/JSON)
# بتتمسح كل ما التطبيق يعيد التشغيل أو يُنشر من جديد (تخزين غير دائم).
# عشان كده، لو تم ضبط بيانات اتصال Google Sheets في st.secrets، هيستخدمها
# التطبيق تلقائيًا كتخزين دائم؛ ولو مفيش، هيرجع للتخزين المحلي (مناسب للتجربة
# على الجهاز الشخصي فقط).
SDS_ADDITIONS_WS = "sds_additions"
ENTRIES_WS = "entries"


def has_gsheets_config():
    try:
        return "connections" in st.secrets and "gsheets" in st.secrets["connections"]
    except Exception:
        return False


@st.cache_resource
def get_gsheets_conn():
    from streamlit_gsheets import GSheetsConnection
    return st.connection("gsheets", type=GSheetsConnection)


def storage_backend():
    return "gsheets" if has_gsheets_config() else "local"


# --------------------------------------------------------------------------
# قاعدة بيانات SDS
# --------------------------------------------------------------------------
def load_sds_database():
    """المواد الأساسية (286 مادة) تُحمَّل دائمًا من الملف الثابت المرفق مع الكود،
    ثم تُضاف/تُحدَّث فوقها أي مواد جديدة أضافها المستخدمون من مصدر التخزين الدائم
    (Google Sheets) إن وُجد، وإلا من ملف محلي احتياطي."""
    with open(SDS_PATH, "r", encoding="utf-8") as f:
        base_db = json.load(f)

    additions = _load_sds_additions()
    by_name = {m["name"]: m for m in base_db}
    for a in additions:
        by_name[a["name"]] = a  # المواد المُضافة تجاوز الأساسية لو نفس الاسم
    return list(by_name.values())


@st.cache_data(ttl=30)
def load_sds_database_cached():
    return load_sds_database()


def _load_sds_additions():
    if storage_backend() == "gsheets":
        try:
            conn = get_gsheets_conn()
            df = conn.read(worksheet=SDS_ADDITIONS_WS, ttl=0)
            df = df.dropna(how="all")
            return [_row_to_sds_item(r) for _, r in df.iterrows()]
        except Exception as e:
            st.sidebar.warning(f"⚠ تعذّر تحميل إضافات SDS من Google Sheets: {e}")
            return []
    else:
        path = os.path.join(DATA_DIR, "sds_additions.json")
        if os.path.exists(path):
            try:
                return json.load(open(path, "r", encoding="utf-8"))
            except Exception:
                return []
        return []


def _row_to_sds_item(r):
    return {
        "name": str(r.get("name", "")),
        "trade": str(r.get("trade", "-")),
        "cas": str(r.get("cas", "غير متاح")),
        "nfpa": {"h": int(r.get("nfpa_h", 0) or 0), "f": int(r.get("nfpa_f", 0) or 0), "r": int(r.get("nfpa_r", 0) or 0)},
        "state": str(r.get("state", "غير محدد")),
        "uses": str(r.get("uses", "-")),
        "storage": str(r.get("storage", "-")),
        "spill": str(r.get("spill", "-")),
        "health": str(r.get("health", "-")),
        "firstAid": str(r.get("firstAid", "-")),
        "ppe": str(r.get("ppe", "-")),
        "skinDeconMandatory": bool(r.get("skinDeconMandatory", False)),
        "toxClassMain": str(r.get("toxClassMain", "other")),
        "toxClassSub": str(r.get("toxClassSub", "")),
        "pendingApproval": bool(r.get("pendingApproval", True)),
        "addedBy": str(r.get("addedBy", "-")),
        "addedAt": str(r.get("addedAt", "")),
        "sdsFileName": str(r.get("sdsFileName", "") or ""),
        "sdsFileB64": str(r.get("sdsFileB64", "") or ""),
    }


def _sds_item_to_row(item):
    return {
        "name": item["name"], "trade": item.get("trade", "-"), "cas": item.get("cas", "غير متاح"),
        "nfpa_h": item.get("nfpa", {}).get("h", 0), "nfpa_f": item.get("nfpa", {}).get("f", 0),
        "nfpa_r": item.get("nfpa", {}).get("r", 0), "state": item.get("state", "غير محدد"),
        "uses": item.get("uses", "-"), "storage": item.get("storage", "-"), "spill": item.get("spill", "-"),
        "health": item.get("health", "-"), "firstAid": item.get("firstAid", "-"), "ppe": item.get("ppe", "-"),
        "skinDeconMandatory": item.get("skinDeconMandatory", False),
        "toxClassMain": item.get("toxClassMain", "other"), "toxClassSub": item.get("toxClassSub", ""),
        "pendingApproval": item.get("pendingApproval", True), "addedBy": item.get("addedBy", "-"),
        "addedAt": item.get("addedAt", ""),
        "sdsFileName": item.get("sdsFileName", ""), "sdsFileB64": item.get("sdsFileB64", ""),
    }


def _save_sds_additions(additions):
    if storage_backend() == "gsheets":
        conn = get_gsheets_conn()
        rows = [_sds_item_to_row(a) for a in additions]
        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=[
            "name", "trade", "cas", "nfpa_h", "nfpa_f", "nfpa_r", "state", "uses",
            "storage", "spill", "health", "firstAid", "ppe", "skinDeconMandatory",
            "toxClassMain", "toxClassSub", "pendingApproval", "addedBy", "addedAt",
            "sdsFileName", "sdsFileB64",
        ])
        conn.update(worksheet=SDS_ADDITIONS_WS, data=df)
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        path = os.path.join(DATA_DIR, "sds_additions.json")
        json.dump(additions, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    load_sds_database_cached.clear()


def save_sds_database(sds_db):
    """يحفظ فقط المواد المُضافة يدويًا (مش الـ286 مادة الأساسية) في مصدر التخزين
    الدائم، عشان الملف الأساسي يفضل ثابت زي ما هو في الكود."""
    with open(SDS_PATH, "r", encoding="utf-8") as f:
        base_names = {m["name"] for m in json.load(f)}
    additions = [m for m in sds_db if m["name"] not in base_names or m.get("addedBy")]
    _save_sds_additions(additions)


MAX_SDS_FILE_BYTES_GSHEETS = 30_000   # حد آمن لخلية Google Sheets الواحدة (~50 ألف حرف بعد التحويل base64)
MAX_SDS_FILE_BYTES_LOCAL = 5_000_000  # حد معقول للتخزين المحلي (JSON)


def sds_file_size_limit():
    """يرجّع الحد الأقصى المسموح به لحجم ملف SDS المرفوع حسب وضع التخزين الحالي."""
    return MAX_SDS_FILE_BYTES_GSHEETS if storage_backend() == "gsheets" else MAX_SDS_FILE_BYTES_LOCAL


def add_new_material(sds_db, name, trade, cas, tox_main, tox_sub, first_aid,
                      hazard, ppe, storage, added_by,
                      sds_file_bytes=None, sds_file_name=None):
    """يضيف مادة جديدة لقاعدة بيانات SDS بحالة (بانتظار الاعتماد) ويحفظها فورًا
    في مصدر التخزين الدائم إن وُجد. لو اترفق ملف SDS، بيتحفظ مشفّر Base64 داخل
    نفس السجل — الملف مايظهرش لغير المالك إلا بعد اعتماد المادة."""
    sds_file_b64 = ""
    if sds_file_bytes:
        import base64
        sds_file_b64 = base64.b64encode(sds_file_bytes).decode("ascii")

    new_item = {
        "name": name,
        "trade": trade or "-",
        "cas": cas or "غير متاح",
        "nfpa": {"h": 0, "f": 0, "r": 0},
        "state": "غير محدد",
        "uses": "مادة أضيفت يدويًا بواسطة مستخدم النظام — بانتظار اعتماد المسؤول",
        "storage": storage or "غير محدد",
        "spill": "غير محدد",
        "health": hazard or "غير محدد",
        "firstAid": first_aid or "لم يتم إدخال إسعافات أولية — يرجى الرجوع لطبيب أو مسؤول السلامة.",
        "ppe": ppe or "يُنصح بارتداء معدات الوقاية الشخصية القياسية",
        "skinDeconMandatory": False,
        "toxClassMain": tox_main,
        "toxClassSub": tox_sub,
        "pendingApproval": True,
        "addedBy": added_by,
        "addedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sdsFileName": sds_file_name or "",
        "sdsFileB64": sds_file_b64,
    }
    additions = _load_sds_additions()
    additions.append(new_item)
    _save_sds_additions(additions)
    sds_db.append(new_item)
    return new_item


def update_material_approval(name, added_at, approve: bool):
    """يعتمد أو يرفض (يحذف) مادة بانتظار الموافقة، ويحفظ التغيير في التخزين الدائم."""
    additions = _load_sds_additions()
    if approve:
        for a in additions:
            if a["name"] == name and a.get("addedAt") == added_at:
                a["pendingApproval"] = False
    else:
        additions = [a for a in additions if not (a["name"] == name and a.get("addedAt") == added_at)]
    _save_sds_additions(additions)


# --------------------------------------------------------------------------
# سجل الحالات
# --------------------------------------------------------------------------
def load_entries():
    if storage_backend() == "gsheets":
        try:
            conn = get_gsheets_conn()
            df = conn.read(worksheet=ENTRIES_WS, ttl=0)
            df = df.dropna(how="all")
        except Exception as e:
            st.sidebar.warning(f"⚠ تعذّر تحميل الحالات من Google Sheets: {e}")
            df = pd.DataFrame(columns=ENTRY_COLUMNS)
    elif os.path.exists(ENTRIES_PATH):
        try:
            df = pd.read_csv(ENTRIES_PATH)
        except Exception:
            df = pd.DataFrame(columns=ENTRY_COLUMNS)
    else:
        df = pd.DataFrame(columns=ENTRY_COLUMNS)

    for col in ENTRY_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def save_entries(df: pd.DataFrame):
    if storage_backend() == "gsheets":
        conn = get_gsheets_conn()
        conn.update(worksheet=ENTRIES_WS, data=df)
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(ENTRIES_PATH, index=False)


# --------------------------------------------------------------------------
# تصدير Excel
# --------------------------------------------------------------------------
def build_excel_bytes(df: pd.DataFrame) -> bytes:
    display_df = df.copy()
    rename_map = {
        "time": "وقت التسجيل", "hospital_name": "اسم المستشفى", "patient": "اسم المريض",
        "patient_gender": "النوع", "patient_age": "العمر", "incident_date": "تاريخ الحادث",
        "incident_time": "وقت الحادث", "patient_profession": "المهنة",
        "location": "مكان الإصابة", "casualty_count": "عدد المصابين",
        "material": "المادة المشتبه بها", "tox_class_main": "التصنيف السمي - الفئة الرئيسية",
        "tox_class_sub": "التصنيف السمي - الفئة الفرعية", "route": "طريقة وصول المادة",
        "severity": "درجة الخطورة", "sds": "SDS", "first_aid": "الإسعافات الأولية",
        "needs_decon": "إزالة التلوث", "needs_hazmat_team": "فريق HAZMAT",
        "notes": "ملاحظات", "responder": "المسجّل", "entry_datetime": "وقت التسجيل الكامل",
    }
    display_df = display_df.rename(columns=rename_map)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        display_df.to_excel(writer, index=False, sheet_name="تقرير الحالات")
        worksheet = writer.sheets["تقرير الحالات"]
        for col_cells in worksheet.columns:
            max_len = max((len(str(c.value)) if c.value else 0) for c in col_cells)
            worksheet.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 45)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# إرسال البريد الإلكتروني (SMTP)
# --------------------------------------------------------------------------
def send_email_with_attachment(smtp_host, smtp_port, sender_email, sender_password,
                                recipient_email, subject, body_text,
                                attachment_bytes=None, attachment_filename=None,
                                use_tls=True):
    """يرسل بريدًا إلكترونيًا حقيقيًا عبر SMTP، مع إمكانية إرفاق ملف (مثل تقرير Excel)."""
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    if attachment_bytes is not None and attachment_filename:
        part = MIMEApplication(attachment_bytes, Name=attachment_filename)
        part["Content-Disposition"] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)

    with smtplib.SMTP(smtp_host, int(smtp_port), timeout=20) as server:
        if use_tls:
            server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient_email], msg.as_string())


def build_mailto_link(recipient, subject, body):
    """رابط mailto احتياطي يفتح برنامج البريد المحلي بدون أي إعدادات خادم (لا يدعم المرفقات)."""
    import urllib.parse
    q = urllib.parse.urlencode({"subject": subject, "body": body})
    return f"mailto:{recipient}?{q}"


# --------------------------------------------------------------------------
# الحماية: يجب استدعاؤها في أول كل صفحة فرعية
# --------------------------------------------------------------------------
def require_login():
    if not st.session_state.get("logged_in"):
        st.warning("⚠ يجب تسجيل الدخول أولاً.")
        st.page_link("app.py", label="⬅ الذهاب لصفحة تسجيل الدخول")
        st.stop()


def sidebar_user_box():
    is_owner = st.session_state.get("is_owner", False)
    with st.sidebar:
        show_logo(width=70)
        st.markdown(
            f"**{st.session_state.get('username','')}** "
            f"({st.session_state.get('role','')})" + (" 👑" if is_owner else "")
        )
        st.divider()
        if st.button("🚪 تسجيل الخروج"):
            for k in ["logged_in", "username", "role", "is_owner"]:
                st.session_state.pop(k, None)
            st.switch_page("app.py")

