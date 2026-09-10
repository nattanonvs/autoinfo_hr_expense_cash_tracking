from odoo import fields, models


class ExpenseCashSummaryXlsxWizard(models.TransientModel):
    _name = "expense.cash.summary.xlsx.wizard"
    _description = "Expense Cash Summary XLSX Wizard"

    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    def action_export_xlsx(self):
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id),
            ("accounting_date", ">=", self.date_from),
            ("accounting_date", "<=", self.date_to),
        ]
        sheet_ids = self.env["hr.expense.sheet"].search(domain).ids
        return self.env.ref(
            "autoinfo_hr_expense_cash_tracking.action_expense_cash_summary_xlsx"
        ).report_action(self, data={"sheet_ids": sheet_ids}, config=False)