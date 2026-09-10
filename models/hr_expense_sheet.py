from odoo import _, fields, models
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    reimbursement_method = fields.Selection(
        [("petty_cash", "Petty Cash"), ("bank_transfer", "Bank Transfer")],
        default="petty_cash",
        tracking=True,
    )
    cash_tracking_state = fields.Selection(
        [
            ("not_applicable", "Not Applicable"),
            ("waiting_cash_reimbursement", "Waiting Cash Reimbursement"),
            ("cash_reimbursed", "Cash Reimbursed"),
        ],
        default="not_applicable",
        tracking=True,
    )
    cash_paid_date = fields.Date(tracking=True)
    cash_paid_by = fields.Many2one("res.users", tracking=True)
    cash_reference = fields.Char(tracking=True)
    cash_note = fields.Text()
    returned_for_resubmission = fields.Boolean(tracking=True, copy=False)
    return_reason = fields.Text(tracking=True, copy=False)
    returned_by = fields.Many2one("res.users", tracking=True, copy=False)
    returned_on = fields.Datetime(tracking=True, copy=False)
    returned_tier = fields.Selection(
        [
            ("manager_review", "Manager Review"),
            ("accounting_review", "Accounting Review"),
            ("final_approval", "Final Approval"),
        ],
        tracking=True,
        copy=False,
    )

    def _check_all_lines_have_analytic_account(self):
        self.mapped("expense_line_ids")._check_cash_tracking_analytic_account()

    def _check_all_lines_have_valid_expense_category_mapping(self):
        expense_lines = self.mapped("expense_line_ids")
        expense_lines._check_expense_category_mapping()
        invalid_mapping_lines = expense_lines.filtered(
            lambda expense: expense.expense_category_id
            and expense.product_id != expense.expense_category_id.product_id
        )
        if invalid_mapping_lines:
            raise UserError(
                _(
                    "Every expense line must keep the product mapped from its Expense Category before this report can be submitted."
                )
            )

    def write(self, vals):
        tracked_fields = {"returned_for_resubmission", "return_reason", "returned_tier"}
        notify_on_return = bool(tracked_fields.intersection(vals))
        previous_state_by_id = {}
        if notify_on_return:
            previous_state_by_id = {
                sheet.id: (
                    sheet.returned_for_resubmission,
                    sheet.return_reason,
                    sheet.returned_tier,
                )
                for sheet in self
            }

        result = super().write(vals)

        if notify_on_return:
            returned_sheets = self.filtered(
                lambda sheet: sheet.returned_for_resubmission
                and (
                    not previous_state_by_id[sheet.id][0]
                    or previous_state_by_id[sheet.id][1] != sheet.return_reason
                    or previous_state_by_id[sheet.id][2] != sheet.returned_tier
                )
            )
            returned_sheets._notify_cash_tracking_returned()

        return result

    def action_submit_sheet(self):
        self._check_all_lines_have_analytic_account()
        self._check_all_lines_have_valid_expense_category_mapping()
        return super().action_submit_sheet()

    def _get_cash_tracking_primary_reviewer(self):
        self.ensure_one()
        base_user = (
            self.employee_id.expense_manager_id
            or self.employee_id.parent_id.user_id
            or self.employee_id.department_id.manager_id.user_id
        )
        if not base_user:
            return self.env["res.users"]

        delegate_user = self.env[
            "autoinfo.expense.approval.delegate"
        ].find_active_delegate(
            self.employee_id,
            base_user,
            fields.Date.context_today(self),
        )
        return delegate_user or base_user

    def _check_cash_tracking_validation_gate(self):
        blocked_sheets = self.filtered(
            lambda sheet: sheet.need_validation
            or (sheet.review_ids and not sheet.validated)
        )
        if blocked_sheets:
            raise UserError(
                _(
                    "This expense report must complete Tier Validation before approval or posting."
                )
            )

    def approve_expense_sheets(self):
        self._check_cash_tracking_validation_gate()
        return super().approve_expense_sheets()

    def action_sheet_move_create(self):
        self._check_cash_tracking_validation_gate()
        return super().action_sheet_move_create()

    def action_request_cash_tracking_validation(self):
        self.write(
            {
                "returned_for_resubmission": False,
                "return_reason": False,
                "returned_by": False,
                "returned_on": False,
                "returned_tier": False,
            }
        )
        return self.request_validation()

    def _get_cash_tracking_return_tier(self):
        self.ensure_one()
        if self.returned_tier:
            return self.returned_tier
        if self.validated:
            return "final_approval"
        if self.review_ids:
            return "accounting_review"
        return "manager_review"

    def action_open_return_reason_wizard(self, returned_tier=None):
        self.ensure_one()
        view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_expense_return_reason_wizard_form"
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Return Expense Sheet"),
            "res_model": "expense.return.reason.wizard",
            "view_mode": "form",
            "view_id": view.id,
            "target": "new",
            "context": {
                "default_sheet_id": self.id,
                "default_returned_tier": returned_tier
                or self._get_cash_tracking_return_tier(),
            },
        }

    def _notify_cash_tracking_returned(self):
        for sheet in self:
            tier_label = dict(self._fields["returned_tier"].selection).get(
                sheet.returned_tier,
                _("Review"),
            )
            body = _(
                "Expense Sheet %s was rejected at %s. Please correct it and request validation again."
            ) % (sheet.name or "", tier_label)
            if sheet.return_reason:
                body = "%s<br/>%s: %s" % (
                    body,
                    _("Reason"),
                    sheet.return_reason,
                )
            sheet.message_post(body=body)

    def action_mark_cash_reimbursed(self):
        self.ensure_one()
        if not self.user_has_groups(
            "autoinfo_hr_expense_cash_tracking.group_expense_cash_reimbursement_manager"
        ):
            raise UserError(
                _("Only authorized finance users can mark cash reimbursement.")
            )
        author_id = self.env.user.partner_id.id
        sudo_self = self.sudo()
        sudo_self.write(
            {
                "cash_tracking_state": "cash_reimbursed",
                "cash_paid_by": self.env.user.id,
                "cash_paid_date": fields.Date.context_today(self),
            }
        )
        sudo_self.message_post(
            body=_("Cash reimbursement has been completed."),
            author_id=author_id,
        )
        return True
