from odoo import fields, models


class ExpenseApprovalRole(models.Model):
    _name = "autoinfo.expense.approval.role"
    _description = "Expense Approval Role"
    _order = "name, id"

    name = fields.Char(required=True)
    code = fields.Selection(
        [
            ("manager_review", "Manager Review"),
            ("accounting_review", "Accounting Review"),
            ("final_approval", "Final Approval"),
        ],
        required=True,
    )
    group_id = fields.Many2one("res.groups", required=True, ondelete="restrict")
    company_id = fields.Many2one("res.company")
