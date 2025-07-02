import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

# --------- CSS Style ---------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f5f8fc;
    }
    .metric-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    .section-header {
        font-size: 20px;
        color: #1e3d59;
        margin-top: 20px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --------- Logo and Upload ---------
col_logo, col_upload = st.columns([1, 3])

with col_logo:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=180)
    except:
        st.warning("الشعار غير متوفر!")

with col_upload:
    st.markdown("<div class='section-header'>يرجى تحميل بيانات الموظفين</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    # --------- Unified Filtering (استبعاد الجهات + عمال البلدية) ---------
    excluded_departments = ['HC.نادي عجمان للفروسية', 'PD.الشرطة المحلية لإمارة عجمان', 'RC.الديوان الأميري']
    if 'الدائرة' in df.columns:
        df = df[~df['الدائرة'].isin(excluded_departments)]

    if 'الدائرة' in df.columns and 'الوظيفة' in df.columns:
        filtered_df = df[~((df['الدائرة'] == 'AM.دائرة البلدية والتخطيط') & (df['الوظيفة'] == 'عامل'))].copy()
    else:
        filtered_df = df.copy()
    # -------------------------------------------------------------------

    # --------- حساب العمر ---------
    def calculate_age(birthdate):
        if pd.isnull(birthdate):
            return None
        return datetime.now().year - pd.to_datetime(birthdate).year

    if "تاريخ الميلاد" in filtered_df.columns:
        filtered_df["العمر"] = filtered_df["تاريخ الميلاد"].apply(calculate_age)

    # --------- Tabs ---------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([" نظرة عامة", " تحليلات بصرية", " البيانات المفقودة", " عرض البيانات", " الموظفون فوق 60"])

    # --------- Tab 1 ---------
    with tab1:
        st.markdown("### نظرة عامة للموظفين المواطنين فقط")
        df_citizens = filtered_df[filtered_df['الجنسية'] == 'إماراتية'].copy()
        st.write(df_citizens)

    # --------- Tab 2 ---------
    with tab2:
        st.markdown("### التحليلات البصرية")

        if 'الجنس' in filtered_df.columns:
            gender_counts = filtered_df['الجنس'].value_counts().reset_index()
            gender_counts.columns = ['الجنس', 'العدد']
            fig = px.bar(gender_counts, x='الجنس', y='العدد')
            st.plotly_chart(fig, use_container_width=True)

    # --------- Tab 3 ---------
    with tab3:
        st.markdown("### تحليل البيانات المفقودة")

        missing_count = filtered_df.isnull().sum()
        missing_percent = filtered_df.isnull().mean() * 100

        missing_df = pd.DataFrame({
            'العمود': missing_count.index,
            'عدد القيم المفقودة': missing_count.values,
            'النسبة المئوية': missing_percent.values.round(2)
        }).query("`عدد القيم المفقودة` > 0")

        st.dataframe(missing_df)

    # --------- Tab 4 ---------
    with tab4:
        st.markdown("<div class='section-header'> عرض البيانات بعد الفلترة</div>", unsafe_allow_html=True)
        st.dataframe(filtered_df)

    # --------- Tab 5 ---------
    with tab5:
        st.markdown("### الموظفون فوق 60 سنة")
        over_60 = filtered_df[filtered_df["العمر"] > 60]
        st.dataframe(over_60)

else:
    st.warning("يرجى رفع ملف بيانات الموظفين أولًا.")


