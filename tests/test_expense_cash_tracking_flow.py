import ast

from lxml import etree

from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import AccessError, UserError
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
        cls.internal_user = cls._create_user(
            "Expense Cash Internal User",
            "expense_cash_internal",
        )
        cls.manager_user = cls._create_user(
            "Expense Cash Manager User",
            "expense_cash_manager",
            "hr_expense.group_hr_expense_manager",
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
        cls.expense_journal = cls.env["account.journal"].create(
            {
                "name": "Expense Cash Tracking Journal",
                "code": "ECTJ",
                "type": "general",
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

    def _assert_user_cannot_reset_sheet_to_draft(self, user):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")

        with self.assertRaises(UserError):
            sheet.with_user(user).action_reset_to_draft_by_manager(
                "No permission for this reset"
            )

    def _create_reset_wizard(self, sheet, reason="Reset for correction", user=None):
        wizard_model = self.env["expense.reset.to.draft.reason.wizard"]
        if user:
            wizard_model = wizard_model.with_user(user)
        return wizard_model.create(
            {
                "sheet_id": sheet.id,
                "reason": reason,
            }
        )

    def _assert_reset_audit_message(self, sheet, expected_parts):
        matching_bodies = [
            body
            for body in sheet.message_ids.mapped("body")
            if "reset to draft by manager" in body.lower()
        ]
        self.assertTrue(matching_bodies)
        self.assertTrue(
            any(
                all(expected_part.lower() in body.lower() for expected_part in expected_parts)
                for body in matching_bodies
            )
        )

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
        sheet = self._make_sheet(expense, state="submit")

        wizard = self.env["expense.return.reason.wizard"].with_user(
            self.manager_user
        ).create(
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
        self.assertEqual(sheet.returned_by, self.manager_user)
        self.assertTrue(sheet.returned_on)

    def test_request_cash_tracking_validation_resets_return_cycle(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")
        wizard = self.env["expense.return.reason.wizard"].with_user(
            self.manager_user
        ).create(
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

    def test_reset_wizard_action_contains_sheet_context(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="approve")

        action = sheet.action_open_reset_to_draft_reason_wizard()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(
            action["res_model"],
            "expense.reset.to.draft.reason.wizard",
        )
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_sheet_id"], sheet.id)

    def test_reset_wizard_open_rejects_user_without_manager_access(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")

        with self.assertRaises(UserError):
            sheet.with_user(self.employee_user).action_open_reset_to_draft_reason_wizard()

    def test_reset_wizard_open_allows_posted_sheet_with_account_move(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="post",
            journal_id=self.expense_journal.id,
        )
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": fields.Date.today(),
                "journal_id": self.expense_journal.id,
                "ref": "Expense Reset Open Guard",
            }
        )
        sheet.write({"account_move_id": move.id})

        action = sheet.with_user(self.manager_user).action_open_reset_to_draft_reason_wizard()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "expense.reset.to.draft.reason.wizard")
        self.assertEqual(action["context"]["default_sheet_id"], sheet.id)

    def test_reset_wizard_acl_blocks_direct_create_for_non_manager(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")

        with self.assertRaises(AccessError):
            self.env["expense.reset.to.draft.reason.wizard"].with_user(
                self.employee_user
            ).create(
                {
                    "sheet_id": sheet.id,
                    "reason": "Trying to bypass manager access",
                }
            )

    def test_reset_wizard_rejects_blank_reason(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")
        wizard = self._create_reset_wizard(
            sheet,
            reason="   ",
            user=self.manager_user,
        )

        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_manager_can_reset_cash_reimbursed_sheet_to_draft(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="approve",
            cash_tracking_state="cash_reimbursed",
        )
        sheet.write(
            {
                "cash_paid_date": fields.Date.today(),
                "cash_paid_by": self.finance_cash_user.id,
                "cash_reference": "PC-POST-001",
                "cash_note": "Already reimbursed",
            }
        )

        wizard = self._create_reset_wizard(
            sheet,
            reason="Need to fix reimbursed amount",
            user=self.manager_user,
        )
        action = wizard.action_confirm()
        sheet.invalidate_cache()

        self.assertEqual(action, {"type": "ir.actions.act_window_close"})
        self.assertEqual(sheet.state, "draft")
        self.assertEqual(sheet.cash_tracking_state, "not_applicable")
        self.assertFalse(sheet.cash_paid_date)
        self.assertFalse(sheet.cash_paid_by)
        self.assertFalse(sheet.cash_reference)
        self.assertFalse(sheet.cash_note)

    def test_manager_reset_to_draft_clears_previous_tier_reviews(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense)

        sheet.request_validation()
        sheet.invalidate_cache()
        self.assertTrue(sheet.review_ids)
        sheet.review_ids.write({"status": "approved"})
        sheet.invalidate_cache()
        self.assertTrue(sheet.validated)
        sheet.write({"state": "submit"})

        sheet.with_user(self.manager_user).action_reset_to_draft_by_manager(
            "Restart the approval cycle"
        )
        sheet.invalidate_cache()

        self.assertEqual(sheet.state, "draft")
        self.assertFalse(sheet.review_ids)

        sheet.action_request_cash_tracking_validation()
        sheet.invalidate_cache()

        self.assertTrue(sheet.review_ids)

    def test_manager_can_reset_posted_sheet_without_account_move(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="post",
            journal_id=self.expense_journal.id,
        )

        wizard = self._create_reset_wizard(
            sheet,
            reason="Posting happened too early",
            user=self.manager_user,
        )
        wizard.action_confirm()
        sheet.invalidate_cache()

        self.assertEqual(sheet.state, "draft")
        self.assertFalse(sheet.account_move_id)

    def test_posted_reset_clears_accounting_and_reimbursement_audit_fields(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="post",
            journal_id=self.expense_journal.id,
            cash_tracking_state="cash_reimbursed",
        )
        sheet.write(
            {
                "approval_date": fields.Date.today(),
                "accounting_date": fields.Date.today(),
                "cash_paid_date": fields.Date.today(),
                "cash_paid_by": self.finance_cash_user.id,
                "cash_reference": "PC-POST-RESET-001",
                "cash_note": "Posted and reimbursed already",
            }
        )

        wizard = self._create_reset_wizard(
            sheet,
            reason="Posted sheet needs a full restart",
            user=self.manager_user,
        )
        wizard.action_confirm()
        sheet.invalidate_cache()

        self.assertEqual(sheet.state, "draft")
        self.assertFalse(sheet.approval_date)
        self.assertFalse(sheet.accounting_date)
        self.assertEqual(sheet.cash_tracking_state, "not_applicable")
        self.assertFalse(sheet.cash_paid_date)
        self.assertFalse(sheet.cash_paid_by)
        self.assertFalse(sheet.cash_reference)
        self.assertFalse(sheet.cash_note)
        self._assert_reset_audit_message(
            sheet,
            [
                "post",
                "Posted sheet needs a full restart",
                "cash reimbursement data cleared",
            ],
        )

    def test_regular_user_cannot_reset_sheet_to_draft(self):
        self._assert_user_cannot_reset_sheet_to_draft(self.employee_user)

    def test_delegate_user_cannot_reset_sheet_to_draft(self):
        self._assert_user_cannot_reset_sheet_to_draft(self.delegate_user)

    def test_accounting_user_cannot_reset_sheet_to_draft(self):
        self._assert_user_cannot_reset_sheet_to_draft(self.accounting_user)

    def test_finance_cash_user_cannot_reset_sheet_to_draft(self):
        self._assert_user_cannot_reset_sheet_to_draft(self.finance_cash_user)

    def test_posted_sheet_with_account_move_cannot_be_reset_to_draft(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="post",
            journal_id=self.expense_journal.id,
        )
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": fields.Date.today(),
                "journal_id": self.expense_journal.id,
                "ref": "Expense Reset Guard",
            }
        )
        sheet.write({"account_move_id": move.id})

        wizard = self._create_reset_wizard(
            sheet,
            reason="Trying to reopen a posted sheet",
            user=self.manager_user,
        )

        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_reset_to_draft_audit_message_includes_reason_and_previous_state(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="approve",
            cash_tracking_state="cash_reimbursed",
        )

        wizard = self._create_reset_wizard(
            sheet,
            reason="Manager requested full correction",
            user=self.manager_user,
        )
        wizard.action_confirm()
        sheet.invalidate_cache()

        self._assert_reset_audit_message(
            sheet,
            [
                "approve",
                "Manager requested full correction",
                "cash reimbursement data cleared",
            ],
        )

    def test_draft_sheet_cannot_be_reset_to_draft(self):
        expense = self._create_expense()
        sheet = self._make_sheet(
            expense,
            state="draft",
            returned_for_resubmission=True,
            return_reason="Returned for correction",
            returned_tier="manager_review",
        )

        with self.assertRaises(UserError):
            sheet.with_user(self.manager_user).action_reset_to_draft_by_manager(
                "Already in draft"
            )

    def test_return_wizard_action_contains_sheet_context(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")

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

    def test_return_wizard_open_rejects_user_without_reviewer_access(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")

        with self.assertRaises(UserError):
            sheet.with_user(self.internal_user).action_open_return_reason_wizard()

    def test_return_wizard_acl_blocks_direct_create_for_non_reviewer(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")

        with self.assertRaises(AccessError):
            self.env["expense.return.reason.wizard"].with_user(
                self.internal_user
            ).create(
                {
                    "sheet_id": sheet.id,
                    "reason": "Trying to return without reviewer access",
                    "returned_tier": "manager_review",
                }
            )

    def test_accounting_user_can_open_return_wizard(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="approve")

        action = sheet.with_user(self.accounting_user).action_open_return_reason_wizard()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "expense.return.reason.wizard")

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

    def test_sheet_form_limits_return_button_to_reviewer_groups(self):
        view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_hr_expense_sheet_form_cash_tracking"
        )
        arch = view.get_combined_arch()
        root = etree.fromstring(arch.encode())
        buttons = root.xpath(".//button[@name='action_open_return_reason_wizard']")

        self.assertEqual(len(buttons), 1)
        self.assertEqual(
            buttons[0].get("groups"),
            "hr_expense.group_hr_expense_team_approver,hr_expense.group_hr_expense_manager,autoinfo_hr_expense_cash_tracking.group_expense_cash_accounting_reviewer",
        )

    def test_sheet_form_view_contains_reset_to_draft_button_for_manager(self):
        view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_hr_expense_sheet_form_cash_tracking"
        )
        arch = view.get_combined_arch()
        root = etree.fromstring(arch.encode())
        buttons = root.xpath(
            ".//button[@name='action_open_reset_to_draft_reason_wizard']"
        )

        self.assertEqual(len(buttons), 1)
        self.assertEqual(
            buttons[0].get("groups"),
            "hr_expense.group_hr_expense_manager",
        )
        self.assertEqual(buttons[0].get("string"), "Reset to Draft")
        attrs = ast.literal_eval(buttons[0].get("attrs") or "{}")
        invisible_attrs = attrs.get("invisible", [])
        state_conditions = [
            condition
            for condition in invisible_attrs
            if isinstance(condition, (list, tuple))
            and len(condition) == 3
            and condition[0] == "state"
        ]
        self.assertTrue(state_conditions)
        self.assertIn(
            ("state", "not in", ["submit", "approve", "post"]),
            state_conditions,
        )

    def test_mark_cash_reimbursed_sets_audit_fields_and_posts_notification(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="approve")

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

    def test_mark_cash_reimbursed_rejects_draft_sheet(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="draft")

        with self.assertRaises(UserError):
            sheet.with_user(self.finance_cash_user).action_mark_cash_reimbursed()

    def test_mark_cash_reimbursed_rejects_company_paid_sheet(self):
        expense = self._create_expense(payment_mode="company_account")
        sheet = self._make_sheet(expense, state="approve")

        with self.assertRaises(UserError):
            sheet.with_user(self.finance_cash_user).action_mark_cash_reimbursed()

    def test_sheet_form_limits_mark_cash_reimbursed_button_to_ready_sheets(self):
        view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_hr_expense_sheet_form_cash_tracking"
        )
        arch = view.get_combined_arch()
        root = etree.fromstring(arch.encode())
        buttons = root.xpath(".//button[@name='action_mark_cash_reimbursed']")

        self.assertEqual(len(buttons), 1)
        attrs = ast.literal_eval(buttons[0].get("attrs") or "{}")
        invisible_attrs = attrs.get("invisible", [])
        self.assertIn(("state", "not in", ["approve", "post", "done"]), invisible_attrs)
        self.assertIn(("payment_mode", "!=", "own_account"), invisible_attrs)

    def test_return_wizard_posts_notification_message(self):
        expense = self._create_expense()
        sheet = self._make_sheet(expense, state="submit")
        wizard = self.env["expense.return.reason.wizard"].with_user(
            self.manager_user
        ).create(
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
