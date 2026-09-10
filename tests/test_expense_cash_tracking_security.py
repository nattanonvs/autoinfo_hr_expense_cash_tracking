from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("expense_cash_tracking_security", "-at_install", "post_install")
class TestExpenseCashTrackingSecurity(TransactionCase):
    @classmethod
    def _create_user(cls, name, login, *group_xmlids):
        group_ids = [cls.env.ref("base.group_user").id]
        group_ids.extend(cls.env.ref(xmlid).id for xmlid in group_xmlids)
        return cls.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": name,
                "login": login,
                "email": "%s@example.com" % login,
                "password": "test-password",
                "groups_id": [(6, 0, group_ids)],
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_user = cls._create_user(
            "Expense Cash Employee",
            "expense_cash_security_employee",
        )
        cls.other_employee_user = cls._create_user(
            "Expense Cash Other Employee",
            "expense_cash_security_other_employee",
        )
        cls.accounting_user = cls._create_user(
            "Expense Cash Accounting",
            "expense_cash_security_accounting",
            "autoinfo_hr_expense_cash_tracking.group_expense_cash_accounting_reviewer",
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Expense Cash Security Employee",
                "company_id": cls.env.company.id,
                "user_id": cls.employee_user.id,
            }
        )
        cls.other_employee = cls.env["hr.employee"].create(
            {
                "name": "Expense Cash Security Other Employee",
                "company_id": cls.env.company.id,
                "user_id": cls.other_employee_user.id,
            }
        )
        cls.sheet_model = cls.env["hr.expense.sheet"]
        cls.sheet = cls.sheet_model.create(
            {
                "name": "Expense Cash Security Own Sheet",
                "company_id": cls.env.company.id,
                "employee_id": cls.employee.id,
            }
        )
        cls.other_sheet = cls.sheet_model.create(
            {
                "name": "Expense Cash Security Other Sheet",
                "company_id": cls.env.company.id,
                "employee_id": cls.other_employee.id,
            }
        )

    def test_accounting_group_sees_all_sheets(self):
        visible = self.sheet_model.with_user(self.accounting_user).search([])

        self.assertIn(self.sheet, visible)
        self.assertIn(self.other_sheet, visible)

    def test_executive_group_sees_all_sheets(self):
        executive_user = self._create_user(
            "Expense Cash Executive",
            "expense_cash_security_executive",
            "autoinfo_hr_expense_cash_tracking.group_expense_cash_executive_viewer",
        )

        visible = self.sheet_model.with_user(executive_user).search([])

        self.assertIn(self.sheet, visible)
        self.assertIn(self.other_sheet, visible)
