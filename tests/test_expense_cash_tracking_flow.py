from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


@tagged("expense_cash_tracking_flow", "-at_install", "post_install")
class TestExpenseCashTrackingFlow(TransactionCase):
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
            "Expense Cash Employee User",
            "expense_cash_employee",
            "hr_expense.group_hr_expense_user",
        )
        cls.manager_user = cls._create_user(
            "Expense Cash Manager User",
            "expense_cash_manager",
            "hr_expense.group_hr_expense_user",
            "hr_expense.group_hr_expense_team_approver",
        )
        cls.delegate_user = cls._create_user(
            "Expense Cash Delegate User",
            "expense_cash_delegate",
            "hr_expense.group_hr_expense_user",
            "hr_expense.group_hr_expense_team_approver",
        )
        cls.accounting_user = cls._create_user(
            "Expense Cash Accounting User",
            "expense_cash_accounting",
            "autoinfo_hr_expense_cash_tracking.group_expense_cash_accounting_reviewer",
        )
        cls.finance_cash_user = cls._create_user(
            "Expense Cash Finance User",
            "expense_cash_finance",
            "autoinfo_hr_expense_cash_tracking.group_expense_cash_reimbursement_manager",
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Expense Cash Tracking Employee",
                "company_id": cls.env.company.id,
                "user_id": cls.employee_user.id,
                "expense_manager_id": cls.manager_user.id,
            }
        )
        cls.expense_product = cls.env["product.product"].create(
            {
                "name": "Expense Cash Tracking Product",
                "type": "service",
                "can_be_expensed": True,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Expense Cash Tracking Analytic",
                "company_id": cls.env.company.id,
            }
        )
        cls.env.user.groups_id |= cls.env.ref("hr_expense.group_hr_expense_user")
        cls.sheet = cls.env["hr.expense.sheet"].create(
            {
                "name": "Expense Cash Tracking Resolver Sheet",
                "company_id": cls.env.company.id,
                "employee_id": cls.employee.id,
            }
        )
        cls.sheet_model = cls.env["ir.model"].search(
            [("model", "=", "hr.expense.sheet")],
            limit=1,
        )
        cls.env["tier.definition"].create(
            {
                "name": "Expense Cash Tracking Manager Review",
                "model_id": cls.sheet_model.id,
                "review_type": "individual",
                "reviewer_id": cls.manager_user.id,
                "definition_domain": "[('employee_id', '=', %s)]" % cls.employee.id,
                "approve_sequence": True,
                "sequence": 10,
            }
        )

    def _create_expense(self, payment_mode="own_account", analytic_account=True, **overrides):
        values = {
            "name": "Expense Cash Tracking Line",
            "employee_id": self.employee.id,
            "product_id": self.expense_product.id,
            "date": "2026-07-01",
            "unit_amount": 100.0,
            "quantity": 1.0,
            "payment_mode": payment_mode,
        }
        if analytic_account:
            values["analytic_account_id"] = self.analytic_account.id
        values.update(overrides)
        return self.env["hr.expense"].create(values)

    def _make_sheet(self, expense, **overrides):
        values = {
            "name": "Expense Cash Tracking Sheet",
            "company_id": self.env.company.id,
            "employee_id": self.employee.id,
            "expense_line_ids": [(6, 0, expense.ids)],
        }
        values.update(overrides)
        return self.env["hr.expense.sheet"].create(values)

    def test_submit_requires_analytic_account(self):
        expense = self._create_expense(payment_mode="own_account", analytic_account=False)
        sheet = self._make_sheet(expense)

        with self.assertRaises(UserError):
            sheet.action_submit_sheet()

    def test_cash_tracking_defaults_for_own_account_sheet(self):
        expense = self._create_expense(payment_mode="own_account")
        sheet = self._make_sheet(expense)

        self.assertEqual(sheet.cash_tracking_state, "not_applicable")

    def test_delegate_resolves_active_reviewer(self):
        self.env["autoinfo.expense.approval.delegate"].create(
            {
                "employee_id": self.employee.id,
                "approver_user_id": self.manager_user.id,
                "delegate_user_id": self.delegate_user.id,
                "date_start": fields.Date.today(),
            }
        )

        self.assertEqual(
            self.sheet._get_cash_tracking_primary_reviewer(),
            self.delegate_user,
        )

    def test_role_model_maps_accounting_reviewer_group(self):
        role = self.env["autoinfo.expense.approval.role"].create(
            {
                "name": "Accounting Review",
                "code": "accounting_review",
                "group_id": self.env.ref(
                    "autoinfo_hr_expense_cash_tracking.group_expense_cash_accounting_reviewer"
                ).id,
            }
        )

        self.assertEqual(role.code, "accounting_review")

    def test_validation_gate_blocks_until_tier_review_is_completed(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)

        sheet.request_validation()

        with self.assertRaises(UserError):
            sheet._check_cash_tracking_validation_gate()

        self.assertTrue(sheet.review_ids)
        self.assertFalse(sheet.validated)

    def test_return_for_resubmission_records_reason_and_tier(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)

        wizard = self.env["expense.return.reason.wizard"].create(
            {
                "sheet_id": sheet.id,
                "reason": "Receipt amount mismatch",
                "returned_tier": "accounting_review",
            }
        )

        wizard.action_confirm()
        sheet.invalidate_cache()

        self.assertEqual(sheet.state, "draft")
        self.assertTrue(sheet.returned_for_resubmission)
        self.assertEqual(sheet.return_reason, "Receipt amount mismatch")
        self.assertEqual(sheet.returned_tier, "accounting_review")
        self.assertEqual(sheet.returned_by, self.env.user)
        self.assertTrue(sheet.returned_on)

    def test_request_cash_tracking_validation_resets_return_cycle(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)
        wizard = self.env["expense.return.reason.wizard"].create(
            {
                "sheet_id": sheet.id,
                "reason": "Missing attachment",
                "returned_tier": "manager_review",
            }
        )

        wizard.action_confirm()
        sheet.invalidate_cache()
        sheet.action_request_cash_tracking_validation()
        sheet.invalidate_cache()

        self.assertFalse(sheet.returned_for_resubmission)
        self.assertFalse(sheet.return_reason)
        self.assertFalse(sheet.returned_tier)
        self.assertTrue(sheet.review_ids)

    def test_return_wizard_action_contains_sheet_context(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)

        action = sheet.action_open_return_reason_wizard("accounting_review")

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "expense.return.reason.wizard")
        self.assertEqual(action["target"], "new")
        self.assertEqual(
            action["context"]["default_sheet_id"],
            sheet.id,
        )
        self.assertEqual(
            action["context"]["default_returned_tier"],
            "accounting_review",
        )

    def test_summary_xlsx_wizard_action_exists(self):
        action = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.action_expense_cash_summary_xlsx_wizard"
        )

        self.assertEqual(action.type, "ir.actions.act_window")
        self.assertEqual(action.res_model, "expense.cash.summary.xlsx.wizard")
        self.assertEqual(action.target, "new")

    def test_accounting_user_can_create_summary_xlsx_wizard(self):
        wizard = self.env["expense.cash.summary.xlsx.wizard"].with_user(
            self.accounting_user
        ).create(
            {
                "company_id": self.env.company.id,
                "date_from": fields.Date.today(),
                "date_to": fields.Date.today(),
            }
        )

        self.assertTrue(wizard)

    def test_sheet_form_view_contains_cash_tracking_buttons(self):
        view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_hr_expense_sheet_form_cash_tracking"
        )

        self.assertIn('name="action_request_cash_tracking_validation"', view.arch_db)
        self.assertIn('name="action_open_return_reason_wizard"', view.arch_db)
        self.assertIn('name="action_mark_cash_reimbursed"', view.arch_db)
        self.assertIn('name="cash_tracking_state"', view.arch_db)

    def test_mark_cash_reimbursed_sets_audit_fields_and_posts_notification(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)

        sheet.with_user(self.finance_cash_user).action_mark_cash_reimbursed()
        sheet.invalidate_cache()

        self.assertEqual(sheet.cash_tracking_state, "cash_reimbursed")
        self.assertEqual(sheet.cash_paid_by, self.finance_cash_user)
        self.assertTrue(
            any(
                "Cash reimbursement has been completed." in body
                for body in sheet.message_ids.mapped("body")
            )
        )

    def test_return_wizard_posts_notification_message(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)
        wizard = self.env["expense.return.reason.wizard"].create(
            {
                "sheet_id": sheet.id,
                "reason": "Missing receipt",
                "returned_tier": "manager_review",
            }
        )

        wizard.action_confirm()
        sheet.invalidate_cache()

        self.assertTrue(
            any(
                "Please correct it and request validation again." in body
                for body in sheet.message_ids.mapped("body")
            )
        )
