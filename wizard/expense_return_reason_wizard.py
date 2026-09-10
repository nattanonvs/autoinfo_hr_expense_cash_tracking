from odoo import fields, models


class ExpenseReturnReasonWizard(models.TransientModel):
    _name = "expense.return.reason.wizard"
    _description = "Expense Return Reason Wizard"

    sheet_id = fields.Many2one("hr.expense.sheet", required=True)
    reason = fields.Text(required=True)
    returned_tier = fields.Selection(
        [
            ("manager_review", "Manager Review"),
            ("accounting_review", "Accounting Review"),
            ("final_approval", "Final Approval"),
        ],
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        self.sheet_id.write(
            {
                "state": "draft",
                "returned_for_resubmission": True,
                "return_reason": self.reason,
                "returned_by": self.env.user.id,
                "returned_on": fields.Datetime.now(),
                "returned_tier": self.returned_tier,
            }
        )
        return {"type": "ir.actions.act_window_close"}
