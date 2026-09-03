class TelegramLLMAnalyzer:
    """Имитация LLM-анализатора для Telegram-каналов"""

    def __init__(self):
        # Ключевые слова для анализа
        self.work_keywords = ['проект', 'заказ', 'дедлайн', 'клиент', 'работа', 'задача', 'код', 'разработка']
        self.finance_keywords = ['оплата', 'деньги', 'руб', '₽', 'перевод', 'зарплата', 'доход']
        self.negative_keywords = ['нет денег', 'долг', 'кредит', 'займ', 'не отдам', 'кинули']

    def analyze_channel(self, posts_data):
        """Анализирует канал и возвращает психологический портрет"""

        posts = posts_data.get('posts', [])
        all_text = ' '.join([p['text'] for p in posts]).lower()

        # Считаем упоминания
        work_mentions = sum(1 for kw in self.work_keywords if kw in all_text)
        finance_mentions = sum(1 for kw in self.finance_keywords if kw in all_text)
        negative_mentions = sum(1 for kw in self.negative_keywords if kw in all_text)

        # Оцениваем метрики от 0 до 10
        work_stability = min(work_mentions * 2, 10)
        financial_literacy = min(finance_mentions * 2, 10)
        responsibility = max(10 - (negative_mentions * 4), 0)

        # Формируем сигналы
        positive_signals = []
        negative_signals = []

        if work_mentions >= 3:
            positive_signals.append("Часто упоминает работу и проекты — стабильная занятость")
        if 'дедлайн' in all_text or 'срок' in all_text:
            positive_signals.append("Следит за сроками и дедлайнами — высокая ответственность")
        if finance_mentions >= 2:
            positive_signals.append("Открыто обсуждает финансы и оплаты — финансовая грамотность")

        if negative_mentions > 0:
            negative_signals.append("Упоминает долги или финансовые проблемы")
        if work_mentions == 0:
            negative_signals.append("Нет упоминаний работы или проектов")

        if not positive_signals:
            positive_signals.append["Проявляет базовую социальную активность"]
        if not negative_signals:
            negative_signals.append("Критических рисков не выявлено")

        # Корректировка общего скоринга (от -10 до +20 баллов)
        score_adjustment = (work_stability + financial_literacy + responsibility) - 15
        score_adjustment = max(-10, min(score_adjustment, 20))

        return {
            "psychological_profile": {
                "work_stability": work_stability,
                "financial_literacy": financial_literacy,
                "responsibility": responsibility
            },
            "positive_signals": positive_signals,
            "negative_signals": negative_signals,
            "score_adjustment": score_adjustment
        }


# Создаем глобальный экземпляр для импорта
llm_analyzer = TelegramLLMAnalyzer()