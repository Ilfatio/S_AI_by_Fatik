import pandas as pd
import json
import os
from llm_mock import llm_analyzer


class ScoringSystem:
    def __init__(self):
        # Определяем путь к папке data (на уровень выше src)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'data')

    def analyze_bank_statement(self, file_path):
        """Анализирует банковскую выписку (CSV)"""
        df = pd.read_csv(file_path)

        score = 50  # Базовый скоринг

        # 1. Средний доход
        incomes = df[df['type'] == 'income']['amount']
        avg_income = incomes.mean() if not incomes.empty else 0

        if avg_income > 30000:
            score += 15
            income_comment = "Стабильный высокий доход (>30к)"
        elif avg_income > 15000:
            score += 10
            income_comment = "Средний доход (>15к)"
        else:
            income_comment = "Низкий или нерегулярный доход"

        # 2. Регулярность поступлений
        income_count = len(incomes)
        if income_count >= 3:
            score += 20
            regularity_comment = "Регулярные поступления"
        else:
            regularity_comment = "Нерегулярные доходы"

        # 3. Доля расходов
        expenses = abs(df[df['type'] == 'expense']['amount'].sum())
        total_income = incomes.sum() if not incomes.empty else 1
        spending_ratio = expenses / total_income

        if spending_ratio < 0.6:
            score += 15
            spending_comment = "Разумные траты (<60% дохода)"
        else:
            spending_comment = "Высокая долговая/расходная нагрузка"

        return {
            "base_score": min(score, 100),
            "metrics": {
                "avg_income": avg_income,
                "income_count": income_count,
                "spending_ratio": round(spending_ratio, 2)
            },
            "explanation": f"{income_comment}, {regularity_comment}, {spending_comment}"
        }

    def analyze_telegram(self, file_path):
        """Анализирует Telegram-канал (JSON)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return llm_analyzer.analyze_channel(data)

    def calculate_final_score(self, bank_analysis, telegram_analysis):
        """Объединяет результаты"""
        base = bank_analysis['base_score']
        adjustment = telegram_analysis['score_adjustment']

        final_score = min(max(base + adjustment, 0), 100)

        if final_score >= 80:
            rec = "✅ Одобрить кредит. Надежный заемщик."
        elif final_score >= 60:
            rec = "⚠️ Одобрить с ограничениями. Требуется доп. проверка."
        elif final_score >= 40:
            rec = " Высокий риск. Предложить микрозайм или отказ."
        else:
            rec = "❌ Отклонить. Недостаточная платежеспособность."

        return {
            "final_score": final_score,
            "base_score": base,
            "telegram_adjustment": adjustment,
            "recommendation": rec
        }