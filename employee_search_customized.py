
import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide", page_title="نظام الموظفين")

@st.cache_data
def load_data():
    df = pd.read_excel("Book2.xlsx")
    weekdays = ["SUN", "MON", "TUE", "WED", "THU"]
    for day in weekdays:
        df[day] = df[day].astype(str).apply(lambda x: 1 if x.strip() == "1" else 0)
    df["Absent_Days_Count"] = 5 - df[weekdays].sum(axis=1)
    return df, weekdays

df, weekdays = load_data()

st.title("🔍 نظام البحث وعرض الحضور")
query = st.text_input("أدخل اسم الموظف أو رقم الهوية")

if query:
    results = df[df["ID#"].astype(str).str.contains(query) | df["NAME (ENG)"].str.contains(query, case=False)]
    if not results.empty:
        st.success("تم العثور على النتائج:")
        st.dataframe(results)
    else:
        st.warning("لم يتم العثور على نتائج")

# تقرير الغياب من الأحد إلى الخميس
st.header("📋 تقرير الغياب من الأحد إلى الخميس")
absent_df = df[df["Absent_Days_Count"] >= 1]
report = absent_df[["ID#", "NAME (ENG)", "Absent_Days_Count"] + weekdays]
st.dataframe(report)

# زر تحميل التقرير
excel_buffer = io.BytesIO()
report.to_excel(excel_buffer, index=False)
st.download_button(
    label="📥 تحميل تقرير الغياب (Excel)",
    data=excel_buffer.getvalue(),
    file_name="Absent_Employees_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
