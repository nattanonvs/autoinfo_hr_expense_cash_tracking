from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("expense_cash_tracking_xlsx", "-at_install", "post_install")
class TestExpenseCashTrackingXlsx(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Expense Cash XLSX Employee User",
                    "login": "expense_cash_xlsx_employee",
                    "email": "expense_cash_xlsx_employee@example.com",
                    "password": "test-password",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                cls.env.ref("base.group_user").id,
                                cls.env.ref("hr_expense.group_hr_expense_user").id,
                            ],
                        )
                    ],
                }
            )
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Expense Cash XLSX Employee",
                "company_id": cls.env.company.id,
                "user_id": cls.employee_user.id,
            }
        )
        cls.expense_product = cls.env["product.product"].create(
            {
                "name": "Expense Cash XLSX Product",
                "type": "service",
                "can_be_expensed": True,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Expense Cash XLSX Analytic",
                "company_id": cls.env.company.id,
            }
        )
        cls.expense = cls.env["hr.expense"].create(
            {
                "name": "Expense Cash XLSX Line",
                "employee_id": cls.employee.id,
                "product_id": cls.expense_product.id,
                "date": "2026-07-01",
                "unit_amount": 150.0,
                "quantity": 1.0,
                "payment_mode": "own_account",
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.sheet = cls.env["hr.expense.sheet"].create(
            {
                "name": "Expense Cash XLSX Sheet",
                "company_id": cls.env.company.id,
                "accounting_date": "2026-07-01",
                "employee_id": cls.employee.id,
                "expense_line_ids": [(6, 0, cls.expense.ids)],
            }
        )

    def test_detail_xlsx_returns_xlsx_binary(self):
        action = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.action_expense_cash_detail_xlsx"
        )

        content, file_type = action._render_xlsx(self.sheet.ids, data={})

        self.assertEqual(file_type, "xlsx")
        self.assertTrue(content.startswith(b"PK"))

    def test_summary_wizard_returns_report_action(self):
        wizard = self.env["expense.cash.summary.xlsx.wizard"].create(
            {
                "company_id": self.env.company.id,
                "date_from": "2026-07-01",
                "date_to": "2026-07-01",
            }
        )

        action = wizard.action_export_xlsx()

        self.assertEqual(action["type"], "ir.actions.report")

    def test_summary_xlsx_returns_xlsx_binary(self):
        action = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.action_expense_cash_summary_xlsx"
        )

        content, file_type = action._render_xlsx([], data={"sheet_ids": self.sheet.ids})

        self.assertEqual(file_type, "xlsx")
        self.assertTrue(content.startswith(b"PK"))
