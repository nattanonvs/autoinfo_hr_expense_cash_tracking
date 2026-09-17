from odoo import fields, models


class ExpenseResetToDraftReasonWizard(models.TransientModel):
    _name = "expense.reset.to.draft.reason.wizard"
    _description = "Expense Reset To Draft Reason Wizard"

    sheet_id = fields.Many2one("hr.expense.sheet", required=True, readonly=True)
    reason = fields.Text(required=True)

    def action_confirm(self):
        self.ensure_one()
        self.sheet_id.action_reset_to_draft_by_manager(self.reason)
        return {"type": "ir.actions.act_window_close"}
