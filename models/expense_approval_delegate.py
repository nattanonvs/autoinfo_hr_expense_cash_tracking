from odoo import api, fields, models


class ExpenseApprovalDelegate(models.Model):
    _name = "autoinfo.expense.approval.delegate"
    _description = "Expense Approval Delegate"
    _order = "date_start desc, id desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    approver_user_id = fields.Many2one("res.users", required=True, ondelete="restrict")
    delegate_user_id = fields.Many2one("res.users", required=True, ondelete="restrict")
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    active = fields.Boolean(default=True)

    @api.model
    def find_active_delegate(self, employee, approver_user, on_date):
        if not employee or not approver_user:
            return self.env["res.users"]

        domain = [
            ("employee_id", "=", employee.id),
            ("approver_user_id", "=", approver_user.id),
            ("active", "=", True),
            ("date_start", "<=", on_date),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", on_date),
        ]
        return self.search(domain, limit=1).delegate_user_id
