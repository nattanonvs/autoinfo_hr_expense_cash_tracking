from odoo import fields, models


class ExpenseCategory(models.Model):
    _name = "autoinfo.expense.category"
    _description = "Expense Category"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    product_id = fields.Many2one(
        "product.product",
        required=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)
    note = fields.Text()
