import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="نظام الموظفين", layout="wide")
st.markdown("<h1 style='text-align: center; color: #0066cc;'>🔎 نظام البحث وتقارير الحضور</h1>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("Book2.xlsx")
    df.columns = df.columns.str.strip()
    return df.fillna("")

df = load_data()

# 🧠 الوظيفة الذكية لتحديد الغياب أو الدوام الكامل
def analyze_attendance(data, mode="missing_weekdays"):
    weekdays = ["SUN", "MON", "TUE", "WED", "THU"]
    weekends = ["FRI", "SAT"]

    if mode == "missing_weekdays":
        return data[~data[weekdays].apply(lambda x: all(day.strip() != "" for day in x), axis=1)]
    elif mode == "only_weekend":
        return data[
            (data[weekdays].apply(lambda x: all(day.strip() == "" for day in x), axis=1)) &
            (data[weekends].apply(lambda x: any(day.strip() != "" for day in x), axis=1))
        ]
    elif mode == "full_weekdays":
        return data[data[weekdays].apply(lambda x: all(day.strip() != "" for day in x), axis=1)]

# 📌 البحث العادي
query = st.text_input("🔍 أدخل اسم الموظف أو رقم الهوية")

if query.strip():
    query_lower = query.strip().lower()
    search_cols = ["ID#", "NAME (ENG)", "NAME (AR)"]
    mask = df[search_cols].astype(str).apply(lambda row: row.str.lower().str.contains(query_lower)).any(axis=1)
    results = df[mask]

    if not results.empty:
        st.success(f"✅ تم العثور على {len(results)} نتيجة")
        for _, row in results.iterrows():
            with st.container():
                st.markdown(f"### 🧾 {row.get('NAME (AR)', '')} ({row.get('NAME (ENG)', '')})")
                st.markdown(f"- **الرقم الوظيفي:** `{row.get('ID#', '')}`")
                st.markdown(f"- **الجنسية:** `{row.get('NATIONALITY', '')}`")
                st.markdown(f"- **الوظيفة:** `{row.get('POSITION', '')}`")
                st.markdown(f"- **الموقع:** `{row.get('LOCATION', '')}`")
                
                with st.expander("📅 جدول الحضور الأسبوعي"):
                    days = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]
                    schedule = {day: row.get(day, "") for day in days if day in row}
                    sched_df = pd.DataFrame(schedule.items(), columns=["اليوم", "الدوام"])
                    st.table(sched_df)

        # زر تصدير
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            results.to_excel(writer, index=False, sheet_name='SearchResults')
        output.seek(0)
        st.download_button("📥 تحميل النتائج كـ Excel", data=output, file_name="search_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("❌ لم يتم العثور على نتائج")
else:
    st.info("📌 أدخل اسم أو رقم الموظف للبحث")

# 📊 تحليلات إضافية
st.markdown("---")
st.subheader("📋 تقارير الحضور الذكية")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤 الموظفون الغائبون من الأحد إلى الخميس"):
        missing = analyze_attendance(df, mode="missing_weekdays")
        st.write(f"🔸 عدد الموظفين: {len(missing)}")
        st.dataframe(missing)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            missing.to_excel(writer, index=False, sheet_name="Missing Weekdays")
        out.seek(0)
        st.download_button("📥 تحميل التقرير", data=out, file_name="missing_weekdays.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with col2:
    if st.button("📅 الموظفون الذين حضروا الجمعة أو السبت فقط"):
        weekend = analyze_attendance(df, mode="only_weekend")
        st.write(f"🔹 عدد الموظفين: {len(weekend)}")
        st.dataframe(weekend)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            weekend.to_excel(writer, index=False, sheet_name="Weekend Only")
        out.seek(0)
        st.download_button("📥 تحميل التقرير", data=out, file_name="weekend_only.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with col3:
    if st.button("✅ الموظفون الذين حضروا الأحد إلى الخميس كامل"):
        full_week = analyze_attendance(df, mode="full_weekdays")
        st.write(f"🟢 عدد الموظفين: {len(full_week)}")
        st.dataframe(full_week)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            full_week.to_excel(writer, index=False, sheet_name="Full Weekdays")
        out.seek(0)
        st.download_button("📥 تحميل التقرير", data=out, file_name="full_weekdays.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# الشريط الجانبي
with st.sidebar:
    st.image("Unknown.jpeg", width=120)
    st.header("📘 دليل الاستخدام")
    st.markdown("ابحث باسم أو رقم الموظف أو استخدم التقارير الذكية.")
    st.caption("© فريق التقنية 2025")
