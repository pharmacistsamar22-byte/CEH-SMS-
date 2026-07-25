# -*- coding: utf-8 -*-
"""
toxicology_classification.py
تصنيف السموم الشامل لنظام CEHSMS — على غرار التصنيف المعتمد في مراكز السموم الحديثة.

ده ملف مستقل تمامًا (مفيش فيه أي اعتماد على باقي المشروع)، يقدر يتستورد
في common.py أو في أي صفحة مباشرة:

    from toxicology_classification import TOX_MAIN, TOX_SUB, TOX_EXAMPLES

الهيكل:
    TOX_MAIN     : dict {key -> الاسم المعروض (عربي/إنجليزي)}         — الفئة الرئيسية
    TOX_SUB      : dict {key -> [قائمة الفئات الفرعية]}                — الفئة الفرعية لكل رئيسية
    TOX_EXAMPLES : dict {(الفئة الرئيسية, الفئة الفرعية) -> [أمثلة مواد]} — مواد إرشادية لكل فئة فرعية
"""

# ============================================================================
# 1) الفئات الرئيسية (Main Categories) — 8 فئات
# ============================================================================
TOX_MAIN = {
    "chemical": "1. Chemical Toxicology — السموم الكيميائية",
    "pesticides": "2. Pesticide Toxicology — سموم المبيدات",
    "pharma": "3. Pharmaceutical Poisoning — التسممات الدوائية",
    "biological": "4. Biological Toxins & Envenomation — السموم الحيوية واللدغات",
    "food_plant": "5. Food & Natural Toxins — السموم الغذائية والطبيعية",
    "occupational": "6. Occupational & Industrial Exposure — التعرضات المهنية والصناعية",
    "burns": "7. Chemical Burns & Decontamination — الحروق الكيميائية وإزالة التلوث",
    "cbrn": "8. CBRN Toxicology — التهديدات غير التقليدية",
    "other": "مادة كيميائية أخرى — غير مصنفة",
}

# ============================================================================
# 2) الفئات الفرعية (Sub-Categories) لكل فئة رئيسية
# ============================================================================
TOX_SUB = {
    "chemical": [
        "Corrosives — المواد الكاوية",
        "Toxic Gases — الغازات السامة",
        "Hydrocarbons & Solvents — المذيبات والهيدروكربونات",
        "Heavy Metals — المعادن الثقيلة",
        "Toxic Alcohols — الكحولات السامة",
    ],
    "pesticides": [
        "Organophosphates — فوسفات عضوي",
        "Carbamates — كارباميت",
        "Rodenticides — مبيدات قوارض",
        "Herbicides — مبيدات أعشاب",
        "Insecticides — مبيدات حشرية",
    ],
    "pharma": [
        "Analgesics — مسكنات",
        "Sedatives & Hypnotics — مهدئات ومنومات",
        "Antidepressants — مضادات اكتئاب",
        "Antipsychotics — مضادات ذهان",
        "Cardiovascular Drugs — أدوية قلبية وعائية",
        "Antidiabetics — أدوية سكر",
        "Opioids — مواد أفيونية",
    ],
    "biological": [
        "Snake Envenomation — لدغات الأفاعي",
        "Scorpion Envenomation — لسعات العقارب",
        "Spider Envenomation — لدغات العناكب",
        "Marine Toxins — سموم بحرية",
        "Insect Stings — لسعات حشرية",
    ],
    "food_plant": [
        "Food Poisoning — تسمم غذائي",
        "Mushroom Toxicity — سمية الفطر",
        "Plant Poisoning — تسمم نباتي",
        "Mycotoxins — السموم الفطرية",
    ],
    "occupational": [
        "Factory Chemicals — كيماويات المصانع",
        "Petrochemical Exposure — التعرض للبتروكيماويات",
        "Agricultural Exposure — التعرض الزراعي",
        "Laboratory Chemicals — كيماويات المعامل",
    ],
    "burns": [
        "Skin Exposure — تعرض جلدي",
        "Eye Exposure — تعرض للعين",
        "Inhalation Exposure — تعرض استنشاقي",
        "Mass Chemical Exposure — تعرض كيميائي جماعي",
    ],
    "cbrn": [
        "Chemical Agents — عوامل كيميائية",
        "Biological Agents — عوامل بيولوجية",
        "Radiological Exposure — تعرض إشعاعي",
    ],
    "other": [
        "مادة كيميائية أخرى — غير مصنفة",
    ],
}

# ============================================================================
# 3) أمثلة مواد إرشادية لكل فئة فرعية — (الفئة الرئيسية، الفئة الفرعية) -> أمثلة
#    مفتاح الـ tuple بيستخدم القيمة الكاملة زي ما هي مكتوبة في TOX_SUB أعلاه
# ============================================================================
TOX_EXAMPLES = {
    ("chemical", "Corrosives — المواد الكاوية"): [
        "Hydrochloric Acid", "Sulfuric Acid", "Nitric Acid",
        "Caustic Soda (NaOH)", "Potassium Hydroxide", "Battery Acid",
    ],
    ("chemical", "Toxic Gases — الغازات السامة"): [
        "Chlorine", "Ammonia", "Hydrogen Sulfide", "Carbon Monoxide", "Nitrogen Dioxide",
    ],
    ("chemical", "Hydrocarbons & Solvents — المذيبات والهيدروكربونات"): [
        "Kerosene", "Benzene", "Toluene", "Xylene", "Paint Thinner",
    ],
    ("chemical", "Heavy Metals — المعادن الثقيلة"): [
        "Lead", "Mercury", "Arsenic", "Cadmium",
    ],
    ("chemical", "Toxic Alcohols — الكحولات السامة"): [
        "Methanol", "Ethylene Glycol", "Isopropanol",
    ],

    ("pesticides", "Organophosphates — فوسفات عضوي"): [
        "Malathion", "Chlorpyrifos", "Diazinon",
    ],
    ("pesticides", "Carbamates — كارباميت"): [
        "Carbaryl", "Methomyl",
    ],
    ("pesticides", "Rodenticides — مبيدات قوارض"): [
        "Zinc Phosphide", "Warfarin", "Bromadiolone",
    ],
    ("pesticides", "Herbicides — مبيدات أعشاب"): [
        "Paraquat", "Glyphosate",
    ],
    ("pesticides", "Insecticides — مبيدات حشرية"): [
        "Pyrethroids",
    ],

    ("pharma", "Analgesics — مسكنات"): [
        "Paracetamol", "Salicylates",
    ],
    ("pharma", "Sedatives & Hypnotics — مهدئات ومنومات"): [
        "Benzodiazepines", "Barbiturates",
    ],
    ("pharma", "Antidepressants — مضادات اكتئاب"): [],
    ("pharma", "Antipsychotics — مضادات ذهان"): [],
    ("pharma", "Cardiovascular Drugs — أدوية قلبية وعائية"): [],
    ("pharma", "Antidiabetics — أدوية سكر"): [],
    ("pharma", "Opioids — مواد أفيونية"): [],

    ("biological", "Snake Envenomation — لدغات الأفاعي"): [
        "Egyptian Cobra", "Horned Viper", "Carpet Viper",
    ],
    ("biological", "Scorpion Envenomation — لسعات العقارب"): [
        "Androctonus spp.", "Leiurus quinquestriatus",
    ],
    ("biological", "Spider Envenomation — لدغات العناكب"): [],
    ("biological", "Marine Toxins — سموم بحرية"): [
        "Jellyfish", "Stonefish", "Puffer Fish",
    ],
    ("biological", "Insect Stings — لسعات حشرية"): [
        "Bee", "Wasp", "Hornet",
    ],

    ("food_plant", "Food Poisoning — تسمم غذائي"): [],
    ("food_plant", "Mushroom Toxicity — سمية الفطر"): [],
    ("food_plant", "Plant Poisoning — تسمم نباتي"): [
        "Datura", "Oleander", "Castor Bean",
    ],
    ("food_plant", "Mycotoxins — السموم الفطرية"): [],

    ("occupational", "Factory Chemicals — كيماويات المصانع"): [],
    ("occupational", "Petrochemical Exposure — التعرض للبتروكيماويات"): [],
    ("occupational", "Agricultural Exposure — التعرض الزراعي"): [],
    ("occupational", "Laboratory Chemicals — كيماويات المعامل"): [],

    ("burns", "Skin Exposure — تعرض جلدي"): [],
    ("burns", "Eye Exposure — تعرض للعين"): [],
    ("burns", "Inhalation Exposure — تعرض استنشاقي"): [],
    ("burns", "Mass Chemical Exposure — تعرض كيميائي جماعي"): [],

    ("cbrn", "Chemical Agents — عوامل كيميائية"): [
        "Nerve Agents", "Blister Agents", "Choking Agents",
    ],
    ("cbrn", "Biological Agents — عوامل بيولوجية"): [],
    ("cbrn", "Radiological Exposure — تعرض إشعاعي"): [],

    ("other", "مادة كيميائية أخرى — غير مصنفة"): [],
}


# ============================================================================
# 4) دوال مساعدة (Helper Functions)
# ============================================================================
def get_sub_categories(main_key: str):
    """يرجّع قائمة الفئات الفرعية لفئة رئيسية معينة."""
    return TOX_SUB.get(main_key, [])


def get_examples(main_key: str, sub_label: str):
    """يرجّع أمثلة المواد لفئة فرعية معينة."""
    return TOX_EXAMPLES.get((main_key, sub_label), [])


def get_all_examples_flat():
    """
    يرجّع كل الأمثلة في قائمة واحدة مسطّحة، كل عنصر فيها dict فيه:
    substance, main_key, main_label, sub_label — مفيدة لبناء قوائم بحث/اقتراح
    تلقائي (Autocomplete) في نموذج تسجيل الحالة.
    """
    flat = []
    for (main_key, sub_label), substances in TOX_EXAMPLES.items():
        for s in substances:
            flat.append({
                "substance": s,
                "main_key": main_key,
                "main_label": TOX_MAIN[main_key],
                "sub_label": sub_label,
            })
    return flat


def find_classification_by_substance(substance_name: str):
    """
    يدور على اسم مادة معينة (مطابقة جزئية غير حساسة لحالة الأحرف) داخل كل
    الأمثلة، ويرجّع أول تصنيف (رئيسي/فرعي) يطابقها، أو None لو مفيش تطابق.
    مفيد لاقتراح تصنيف تلقائي لما المستخدم يكتب اسم مادة معروفة.
    """
    q = substance_name.strip().lower()
    if not q:
        return None
    for (main_key, sub_label), substances in TOX_EXAMPLES.items():
        for s in substances:
            if q in s.lower() or s.lower() in q:
                return {"main_key": main_key, "main_label": TOX_MAIN[main_key], "sub_label": sub_label}
    return None


def get_main_category_keys():
    """يرجّع كل مفاتيح الفئات الرئيسية بالترتيب."""
    return list(TOX_MAIN.keys())


# ============================================================================
# اختبار سريع مستقل (يشتغل لو الملف اتنفذ لوحده، من غير Streamlit)
# ============================================================================
if __name__ == "__main__":
    print("عدد الفئات الرئيسية:", len(TOX_MAIN))
    total_sub = sum(len(v) for v in TOX_SUB.values())
    print("عدد الفئات الفرعية الكلي:", total_sub)
    total_examples = sum(len(v) for v in TOX_EXAMPLES.values())
    print("عدد الأمثلة الكلي:", total_examples)

    print("\n--- تجربة البحث عن تصنيف لمادة 'Methanol' ---")
    result = find_classification_by_substance("Methanol")
    print(result)

    print("\n--- الفئات الفرعية لـ Chemical Toxicology ---")
    for sub in get_sub_categories("chemical"):
        print(" -", sub, "| أمثلة:", get_examples("chemical", sub))
