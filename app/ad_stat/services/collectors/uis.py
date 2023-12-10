from ad_stat.models.company import Company
from damri.collectors.uis.collector import _UISDataCollector
from damri.integrations.api.uis.models import CallReportItemModel


class CompanyUISDataCollector(_UISDataCollector):
    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    # TODO add filter in api
    def calls_report_prev_week(self) -> list[CallReportItemModel]:
        return [
            report
            for report in super().calls_report_prev_week()
            if report.virtual_phone_number in self.company.uis_setting.phone
        ]

    def calls_report_prev_month(self) -> list[CallReportItemModel]:
        return [
            report
            for report in super().calls_report_prev_month()
            if report.virtual_phone_number in self.company.uis_setting.phone
        ]
