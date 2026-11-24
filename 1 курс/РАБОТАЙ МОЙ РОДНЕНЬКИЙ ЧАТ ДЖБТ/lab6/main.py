import streamlit as st
import pandas as pd
import time
import random
import uuid
from datetime import datetime, timedelta

# === CONFIG & STYLE ===
st.set_page_config(page_title="DevData Generator", layout="wide")
st.markdown("""
    <style>
    .stSidebar { background-color: #1E2130; }
    .stDataFrame { border: 1px solid #334155; border-radius: 8px; }
    div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }
    button[kind="primary"] { background-color: #00D4FF; color: #121420; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# === UI SETUP ===
st.title("🛠️ DevData Generator")
st.caption("Инструмент быстрого создания синтетических датасетов для тестирования")

with st.sidebar:
    st.header("⚙️ Конфигурация")
    entity_type = st.selectbox("Тип сущности", ["Пользователи", "Транзакции", "Логи сервера", "IoT-датчики"])
    n_rows = st.slider("Количество записей", 10, 2000, 100)
    add_nulls = st.checkbox("Добавить пропуски (NULL)", value=False)
    
    generate_btn = st.button("🚀 Запустить генерацию", type="primary", use_container_width=True)

# === LOGIC & SIMULATION ===
if "df_generated" not in st.session_state:
    st.session_state.df_generated = None

if generate_btn:
    with st.spinner("⏳ Инициализация ETL-конвейера..."):
        time.sleep(1.5)
        
        # Mock data generation
        data = []
        statuses = ["ACTIVE", "INACTIVE", "PENDING", "ARCHIVED"]
        for _ in range(n_rows):
            row = {
                "Record_ID": str(uuid.uuid4())[:8],
                "Full_Name": f"User_{random.randint(1000, 9999)}",
                "Contact_Email": f"user_{random.randint(10, 99)}@test.io",
                "Created_At": datetime.now() - timedelta(days=random.randint(1, 365)),
                "Value_USD": round(random.uniform(10.0, 5000.0), 2),
                "Status_Flag": random.choice(statuses)
            }
            if add_nulls and random.random() < 0.15:
                row["Contact_Email"] = None
            data.append(row)
            
        df = pd.DataFrame(data)
        df["Created_At"] = df["Created_At"].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.df_generated = df
        st.success("✅ Генерация завершена. Валидация типов пройдена.")

# === DISPLAY ===
if st.session_state.df_generated is not None:
    st.subheader("📊 Предпросмотр данных")
    st.dataframe(st.session_state.df_generated.head(50), use_container_width=True, height=400)
    
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        csv_data = st.session_state.df_generated.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Экспорт в CSV",
            data=csv_data,
            file_name="synthetic_data_export.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col1:
        st.metric("Сгенерировано записей", len(st.session_state.df_generated))
        st.metric("Полей в схеме", len(st.session_state.df_generated.columns))
else:
    st.info("ℹ️ Настройте параметры в боковой панели и запустите генерацию.")