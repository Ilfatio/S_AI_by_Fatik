import streamlit as st
import os
import plotly.graph_objects as go
from scoring import ScoringSystem

st.set_page_config(page_title="Альтернативный Скоринг", layout="wide", page_icon="")

st.title("📊 Альтернативный Скоринг (Сбер)")
# Стилизация под Сбер
st.markdown("""
<style>
    /* Зеленая главная кнопка */
    .stButton>button {
        background-color: #21A038 !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #1a802d !important;
    }
    /* Зеленая полоска для метрик */
    .stMetric {
        border-left: 4px solid #21A038;
        padding-left: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        padding-top: 5px;
        padding-bottom: 5px;
    }
    /* Убираем стандартный футер Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Инициализация системы
scoring = ScoringSystem()
data_dir = scoring.data_dir

# Боковая панель
st.sidebar.header("️ Настройки")
use_mock_data = st.sidebar.checkbox("Использовать демо-данные", value=True)

if use_mock_data:
    bank_file = os.path.join(data_dir, "mock_bank.csv")
    telegram_file = os.path.join(data_dir, "mock_telegram.json")
    st.sidebar.success("Загружены тестовые данные")
else:
    bank_file = st.sidebar.file_uploader("Выписка из банка (CSV)", type=['csv'])
    telegram_file = st.sidebar.file_uploader("Telegram канал (JSON)", type=['json'])
    st.sidebar.warning("Загрузите оба файла для анализа")

# Кнопка запуска
if st.button("🚀 Рассчитать скоринг", type="primary"):
    with st.spinner("Анализируем цифровой след и финансовые потоки..."):
        # Запуск анализа
        bank_analysis = scoring.analyze_bank_statement(bank_file)
        telegram_analysis = scoring.analyze_telegram(telegram_file)
        final_result = scoring.calculate_final_score(bank_analysis, telegram_analysis)

        # --- ВИЗУАЛИЗАЦИЯ ---

        # 1. Главный спидометр
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🎯 Итоговая оценка")
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=final_result['final_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Благонадежность (0-100)", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 40], 'color': "#ffcccc"},
                        {'range': [40, 70], 'color': "#ffffcc"},
                        {'range': [70, 100], 'color': "#ccffcc"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 60
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
            st.info(final_result['recommendation'])

        with col2:
            st.subheader("📈 Структура скоринга")
            st.metric("Базовый скоринг (Банк)", f"{final_result['base_score']} баллов")
            st.metric("Корректировка (Telegram AI)",
                      f"{'+' if final_result['telegram_adjustment'] >= 0 else ''}{final_result['telegram_adjustment']} баллов")

            st.divider()
            st.subheader("🏦 Анализ выписки")
            st.write(bank_analysis['explanation'])
            st.metric("Средний доход", f"{bank_analysis['metrics']['avg_income']:,.0f} ₽")
            st.metric("Доля расходов", f"{bank_analysis['metrics']['spending_ratio'] * 100:.0f}%")

        # 2. Детальный разбор Telegram
        st.divider()
        st.subheader("🧠 AI-анализ Telegram-канала")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("#### ✅ Позитивные сигналы")
            for signal in telegram_analysis['positive_signals']:
                st.success(f"✓ {signal}")

        with col4:
            st.markdown("#### ⚠️ Факторы риска")
            for signal in telegram_analysis['negative_signals']:
                st.warning(f"⚠ {signal}")

                # 3. Психологический портрет
                st.divider()
                st.subheader("👤 Психологический портрет заемщика")
                profile = telegram_analysis['psychological_profile']

                p1, p2, p3 = st.columns(3)
                with p1:
                    st.progress(profile['work_stability'] / 10)
                    st.caption(f"Стабильность работы: {profile['work_stability']}/10")
                with p2:
                    st.progress(profile['financial_literacy'] / 10)
                    st.caption(f"Фин. грамотность: {profile['financial_literacy']}/10")
                with p3:
                    st.progress(profile['responsibility'] / 10)
                    st.caption(f"Ответственность: {profile['responsibility']}/10")

                # 4. Кнопка экспорта (Вау-эффект)
                st.divider()
                st.subheader(" Отчет для кредитного комитета")

                report_text = f"""
        ОТЧЕТ ОБ АЛЬТЕРНАТИВНОМ СКОРИНГЕ
        ================================
        Дата анализа: 03.09.2026

        1. ФИНАНСОВЫЙ СКОРИНГ: {final_result['base_score']}/100
           {bank_analysis['explanation']}

        2. AI-АНАЛИЗ ЦИФРОВОГО СЛЕДА:
           Корректировка: {final_result['telegram_adjustment']} баллов
           Позитив: {', '.join(telegram_analysis['positive_signals'])}
           Риски: {', '.join(telegram_analysis['negative_signals'])}

        3. ИТОГОВАЯ ОЦЕНКА: {final_result['final_score']}/100
           РЕШЕНИЕ: {final_result['recommendation']}
                """

                st.download_button(
                    label="⬇️ Скачать отчет для банка",
                    data=report_text,
                    file_name="scoring_report.txt",
                    mime="text/plain"
                )

            else:
                st.info("👆 Настройте параметры слева и нажмите кнопку для запуска AI-анализа")