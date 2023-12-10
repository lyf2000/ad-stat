import logging

from ad_stat.choices import NotieLogTypes
from ad_stat.models.company import Company
from ad_stat.models.company_payment import PaymentInvoice
from ad_stat.services.noties.click_ru.base_notifier import (
    CoreClickRuNotifierMessageBuilderService,
)
from ad_stat.services.noties.flow.log.deliver import NotieDeliverLogFlow
from common.services.base import BaseTgNotifierService
from common.services.tg_bot import TgMessageItem

logger = logging.getLogger(__name__)


class PendingPaymentInvoiceNotifierMessageBuilderService(CoreClickRuNotifierMessageBuilderService):
    def __init__(self, company: Company):
        self.company = company

    def get_head_msg(self) -> TgMessageItem:
        msg = TgMessageItem(
            msg=(
                f"Здравствуйте, {self.tag_user(self.company.payment_setting.tag_tg_user())}"
                " Напоминаем о необходимости оплатить счет."
                f" {self.tag_company_tg_responsible(self.company)}"
            )
        )

        if not (pending_payment := PaymentInvoice.objects.company_pending(self.company)):
            logger.warn(f"No pending payment was found for company {self.company}")
        else:
            self.attach_file(msg, pending_payment.file.file.read(), "Счет.pdf")

        return msg


class PendingPaymentInvoiceNotifierService(BaseTgNotifierService):
    STAT_TYPE = NotieLogTypes.PAYMENT_INVOICE_PENDING

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    def send_notie(self) -> None:
        with NotieDeliverLogFlow(company=self.company, type=self.STAT_TYPE) as deliver:
            msg = PendingPaymentInvoiceNotifierMessageBuilderService(company=self.company).compose_msg(separated=True)

            logger.info(f"{type(self).__name__}: sending to {self.company.id}")
            result = self.message_sender(chat_ids=self.company.get_telegram_ids(), msgs=msg).send_msg_chats()
            deliver(result)
