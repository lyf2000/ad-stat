from common.choices import IntegerChoices


class CompanyTariffChoices(IntegerChoices):
    FREE = 0, "Free"
    STANDART = 1, "Standart"
    PREMIUM = 2, "Premium"


class WeekDayChoices(IntegerChoices):
    MONDAY = 0, "Понедельник"
    TUESDAY = 1, "Вторник"
    WEDNESDAY = 2, "Среда"
    THURSDAY = 3, "Четверг"
    FRIDAY = 4, "Пятница"
    SATURDAY = 5, "Суббота"
    SUNDAY = 6, "Воскресенье"

    @staticmethod
    def get_prev_weekday(val: int) -> int:
        return (val + 6) % 7


class NotieLogStatuses(IntegerChoices):
    NOT_SENT = 0, "Не отправлено"
    SENT = 1, "Отправлено"
    FAILED = 2, "Ошибка"
    EMPTY_MSG = 3, "Пустое сообщение"


class NotieLogTypes(IntegerChoices):
    DAILY_CLICK_STATS_NOTIE = 1, "Отчет по статистике за вчерашний день"
    WEEKLY_YA_DIRECT_ADS_NOTIE = 2, "Отчет по рекламе за предыдущую неделю"
    MONTHLY_CLICK_STATS_NOTIE = 3, "Отчет по статистике за предыдущий месяц"
    PAYMENT_INVOICE_FIRST_STEP = 4, "Создан счет на оплату"
    PAYMENT_INVOICE_PENDING = 5, "Напоминание о необходимости оплатить выставленный счет"
    BALANCE = 6, "Рассылка баланса"
    SEARCH_URL_BOUNCE_TOP = 7, "Топ запросов с большим коэффициентом отказов по URL"
    SEARCH_BOUNCE_TOP = 15, "Топ запросов с большим коэффициентом отказов по запросам"
    SEARCH_VISITS_TOP = 13, "Отчет топ запросов с большим коэффициентом визитов по поиску"
    SEARCH_AD_COST = 14, "Отчет по поисковым запросам с контекстной рекламы"
    SCREEN_BOUNCE_TOP = 8, "Отчет топ запросов с большим коэффициентом отказов по экранам"
    DEVICE_BOUNCE_TOP = 9, "Отчет топ запросов с большим коэффициентом отказов по устройствам"
    DEVICE_CATEGORy_BOUNCE_TOP = 10, "Отчет топ запросов с большим коэффициентом отказов по типам устройств"
    DEVICE_URL = 11, "Отчет топ запросов с большим коэффициентом отказов по типам устройств"
    WEEKLY_YA_DIRECT_AIMS_CONVERSIONS_NOTIE = 12, "Отчет по целям и конверсиям за предыдущую неделю"


class PaymentInvoiceState:
    NOT_PAYED = 0
    PAYED = 1
    RESET_TO_NEW_INVOICE = 2
    CANCELED = 3

    RESETS = (RESET_TO_NEW_INVOICE,)
    READY_FOR_FIRST_STEP = (PAYED, CANCELED)
    PENDING = (NOT_PAYED,)
