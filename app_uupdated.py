import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

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

# ---------- Header Layout ---------- #
col_logo, col_upload = st.columns([1, 3])

with col_logo:
    logo = Image.open("logo.png")
    st.image(logo, width=250)

with col_upload:
    st.markdown("<div class='section-header'>يرجى تحميل بيانات الموظفين</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع ملف", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    # Tabs Section
    tab1, tab2, tab3, tab4 = st.tabs([" نظرة عامة", " تحليلات بصرية", " البيانات المفقودة", " عرض البيانات"])

    with tab1:
        total = df.shape[0]
        complete = df.dropna().shape[0]
        missing_total = df.isnull().any(axis=1).sum()
        complete_pct = round((complete / total) * 100, 1) if total else 0
        missing_pct = round((missing_total / total) * 100, 1) if total else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class='metric-box' style='background-color:#1e3d59;'>
                    <h4> عدد الموظفين</h4>
                    <h2>{total}</h2>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class='metric-box' style='background-color:#2a4d6f;'>
                    <h4>السجلات المكتمله</h4>
                    <h2>{complete} ({complete_pct}%)</h2>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class='metric-box' style='background-color:#4a7ca8;'>
                    <h4>السجلات الناقصة</h4>
                    <h2>{missing_total} ({missing_pct}%)</h2>
                </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-header'> التحليلات البصرية</div>", unsafe_allow_html=True)

        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

        if 'الجنس' in df.columns:
            gender_counts = df['الجنس'].value_counts(normalize=True) * 100
            with kpi_col1:
                fig = go.Figure(go.Pie(values=[gender_counts.get('أنثى', 0), 100 - gender_counts.get('أنثى', 0)],
                                       labels=['إناث', 'أخرى'], hole=0.6,
                                       marker_colors=['#567C8D', '#C8D9E6'], textinfo='none'))
                fig.update_layout(title='نسبة الإناث', title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)

            with kpi_col2:
                fig = go.Figure(go.Pie(values=[gender_counts.get('ذكر', 0), 100 - gender_counts.get('ذكر', 0)],
                                       labels=['ذكور', 'أخرى'], hole=0.6,
                                       marker_colors=['#2F4156', '#C8D9E6'], textinfo='none'))
                fig.update_layout(title='نسبة الذكور', title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)

        if 'المستوى التعليمي' in df.columns:
            edu_mode = df['المستوى التعليمي'].mode()[0] if not df['المستوى التعليمي'].mode().empty else "غير معروف"
            with kpi_col3:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=100,
                    title={'text': f"الفئة الأكثر: {edu_mode}"},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "#2F4156"},
                           'bgcolor': "#C8D9E6"}))
                st.plotly_chart(fig, use_container_width=True)

        fcol1, fcol2 = st.columns([1, 3])
        with fcol1:
            selected_gender = st.selectbox("فلتر الجنس", df['الجنس'].dropna().unique())
            filtered_df = df[df['الجنس'] == selected_gender]

        with fcol2:
            st.subheader(" Bar Chart للجنس")
            gender_counts = df['الجنس'].value_counts().reset_index()
            gender_counts.columns = ['الجنس', 'العدد']
            fig_gender = px.bar(gender_counts, x='الجنس', y='العدد',
                                color='الجنس', color_discrete_sequence=['#2F4156', '#567C8D'])
            fig_gender.update_layout(title='توزيع الموظفين حسب الجنس', title_x=0.5)
            st.plotly_chart(fig_gender, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            if 'الديانة' in df.columns:
                st.subheader("Bar Chart للديانة")
                religion_counts = df['الديانة'].value_counts().reset_index()
                religion_counts.columns = ['الديانة', 'العدد']
                fig_religion = px.bar(religion_counts, x='الديانة', y='العدد',
                                      color='الديانة', color_discrete_sequence=px.colors.sequential.Blues)
                fig_religion.update_layout(title='توزيع الموظفين حسب الديانة', title_x=0.5)
                st.plotly_chart(fig_religion, use_container_width=True)

        with col4:
            if 'الدائرة' in df.columns:
                st.subheader("Pie Chart حسب الدائرة")
                dept_counts = df['الدائرة'].value_counts()
                fig_dept = go.Figure(data=[go.Pie(labels=dept_counts.index,
                                                  values=dept_counts.values,
                                                  hole=0.3,
                                                  marker=dict(colors=px.colors.sequential.Blues),
                                                  textinfo='label+percent')])
                fig_dept.update_layout(title='نسبة الموظفين حسب الدائرة', title_x=0.5)
                st.plotly_chart(fig_dept, use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            if 'المستوى التعليمي' in df.columns:
                st.subheader(" Treemap للمستوى التعليمي")
                edu_counts = df['المستوى التعليمي'].value_counts().reset_index()
                edu_counts.columns = ['المستوى التعليمي', 'العدد']
                fig_tree = px.treemap(edu_counts, path=['المستوى التعليمي'], values='العدد',
                                      color_discrete_sequence=['#2F4156', '#567C8D'])
                fig_tree.update_layout(title='Treemap - المستوى التعليمي', title_x=0.5)
                st.plotly_chart(fig_tree, use_container_width=True)

        with col6:
            if 'العمر' in df.columns:
                st.subheader(" Histogram للعمر")
                fig_hist = px.histogram(df, x='العمر', nbins=20, color_discrete_sequence=['#2F4156'])
                fig_hist.update_layout(title='Histogram - توزيع الأعمار', title_x=0.5)
                st.plotly_chart(fig_hist, use_container_width=True)

        col7, col8 = st.columns(2)
        with col7:
            if 'الجنس' in df.columns and 'العمر' in df.columns:
                st.subheader(" Boxplot للعمر حسب الجنس")
                fig_box = px.box(df, x='الجنس', y='العمر', color='الجنس',
                                color_discrete_sequence=['#2F4156', '#C8D9E6'])
                fig_box.update_layout(title='Boxplot - العمر حسب الجنس', title_x=0.5)
                st.plotly_chart(fig_box, use_container_width=True)

        with col8:
            st.subheader(" مقارنة دوائر Pie Chart")
            if 'الدائرة' in df.columns:
                circle_counts = df['الدائرة'].value_counts().nlargest(5)
                fig_circle = px.pie(values=circle_counts.values, names=circle_counts.index,
                                    hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
                fig_circle.update_layout(title='أكثر الدوائر تمثيلًا', title_x=0.5)
                st.plotly_chart(fig_circle, use_container_width=True)

    with tab3:
        missing_percent = df.isnull().mean() * 100
        missing_count = df.isnull().sum()

        missing_df = pd.DataFrame({
            'العمود': df.columns,
            'عدد القيم المفقودة': missing_count,
            'النسبة المئوية': missing_percent
        })

        missing_df = missing_df[missing_df['عدد القيم المفقودة'] > 0]

        fig_missing = px.bar(
            missing_df,
            x='العمود',
            y='عدد القيم المفقودة',
            color='النسبة المئوية',
            text=missing_df.apply(lambda row: f"{row['عدد القيم المفقودة']} | {round(row['النسبة المئوية'], 1)}%", axis=1),
            color_continuous_scale=['#C8D9E6', '#2F4156']
        )
        fig_missing.update_layout(
            title="عدد القيم المفقودة ونسبتها لكل عمود",
            title_x=0.5,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_missing, use_container_width=True)

        st.markdown("###  تحليل مفقودات عمود محدد")
        selected_column = st.selectbox("اختر عمود", df.columns)

        if selected_column:
            total = df.shape[0]
            missing = df[selected_column].isnull().sum()
            present = total - missing

            values = [present, missing]
            labels = ['موجودة', 'مفقودة']

            fig_donut = px.pie(
                names=labels,
                values=values,
                hole=0.5,
                color=labels,
                color_discrete_map={
                    'مفقودة': '#C8D9E6',
                    'موجودة': '#2F4156'
                }
            )

            fig_donut.update_traces(
                text=[f'{v} | {round(v/total*100)}%' for v in values],
                textinfo='text+label'
            )
            fig_donut.update_layout(title=f"نسبة البيانات في العمود: {selected_column}", title_x=0.5)
            st.plotly_chart(fig_donut, use_container_width=True)

    with tab4:
        st.markdown("<div class='section-header'> فلترة حسب القيم </div>", unsafe_allow_html=True)
        filter_cols = st.multiselect("اختر أعمدة للفلترة:", df.columns)
        filtered_df = df.copy()
        for col in filter_cols:
            options = df[col].dropna().unique().tolist()
            selected = st.multiselect(f"{col}", options)
            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]

        st.markdown("<div class='section-header'> البيانات بعد الفلترة</div>", unsafe_allow_html=True)
        st.dataframe(filtered_df)

else:
    st.info("             ")

