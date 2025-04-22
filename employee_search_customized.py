import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="نظام البحث عن الموظف", layout="wide")
st.title("🔍 نظام البحث عن معلومات الموظف")

@st.cache_data
def load_data():
    df = pd.read_excel("Book2.xlsx")
    df.columns = df.columns.str.strip()
    return df.fillna("")

df = load_data()

query = st.text_input("🔍 أدخل اسم الموظف أو رقم الهوية", help="يدعم البحث بالإنجليزية أو بالعربية")

if query.strip():
    query_lower = query.strip().lower()
    
    # البحث فقط في الأعمدة المحددة
    search_cols = ["ID#", "NAME (ENG)", "NAME (AR)"]
    mask = df[search_cols].astype(str).apply(lambda row: row.str.lower().str.contains(query_lower)).any(axis=1)
    results = df[mask]

    if not results.empty:
        st.success(f"✅ تم العثور على {len(results)} نتيجة مطابقة")
        st.dataframe(results, use_container_width=True)

        # ✅ تصدير النتائج إلى ملف Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            results.to_excel(writer, index=False, sheet_name='SearchResults')
        output.seek(0)

        st.download_button(
            "📥 تحميل النتائج كملف Excel",
            data=output,
            file_name="search_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ لم يتم العثور على نتائج")
else:
    st.info("📌 الرجاء إدخال اسم الموظف أو رقم الهوية للبحث")

with st.sidebar:
    st.header("📘 دليل الاستخدام")
    st.markdown("""
    - ابحث باستخدام الاسم أو رقم الهوية
    - يعرض البرنامج أيضًا جدول الحضور (MON إلى SUN)
    - يمكن تصدير النتائج إلى ملف Excel
    """)