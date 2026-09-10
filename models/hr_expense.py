from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    expense_category_id = fields.Many2one(
        "autoinfo.expense.category",
        string="Expense Category",
        ondelete="restrict",
    )
    analytic_account_required = fields.Boolean(
        compute="_compute_analytic_account_required",
        readonly=True,
    )

    @api.depends("company_id", "account_id")
    def _compute_analytic_account_required(self):
        for expense in self:
            expense.analytic_account_required = True

    @api.onchange("expense_category_id")
    def _onchange_expense_category_id(self):
        for expense in self:
            if expense.expense_category_id and expense.expense_category_id.product_id:
                expense.product_id = expense.expense_category_id.product_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            category_id = vals.get("expense_category_id")
            if category_id and not vals.get("product_id"):
                category = self.env["autoinfo.expense.category"].browse(category_id)
                if category.product_id:
                    vals["product_id"] = category.product_id.id
        return super().create(vals_list)

    def _check_expense_category_mapping(self):
        for expense in self:
            if expense.expense_category_id and not expense.product_id:
                raise UserError(
                    _(
                        "This expense category is not mapped to a product yet. Please contact Accounting."
                    )
                )

    def _check_cash_tracking_analytic_account(self):
        for expense in self:
            if not expense.analytic_account_id:
                raise UserError(
                    _(
                        "Every expense line must have an Analytic Account before this report can be submitted."
                    )
                )
