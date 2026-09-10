from lxml import etree

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("expense_employee_ux", "-at_install", "post_install")
class TestExpenseEmployeeUx(TransactionCase):
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
        cls.manager_user = cls._create_user(
            "Expense Employee UX Manager",
            "expense_employee_ux_manager",
            "hr_expense.group_hr_expense_manager",
        )
        cls.accounting_user = cls._create_user(
            "Expense Employee UX Accounting",
            "expense_employee_ux_accounting",
            "hr_expense.group_hr_expense_user",
            "autoinfo_hr_expense_cash_tracking.group_expense_cash_accounting_reviewer",
        )
        cls.employee_user = cls._create_user(
            "Expense Employee UX User",
            "expense_employee_ux_user",
            "hr_expense.group_hr_expense_user",
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Expense Employee UX Employee",
                "company_id": cls.env.company.id,
                "user_id": cls.employee_user.id,
            }
        )
        cls.expense_product = cls.env["product.product"].create(
            {
                "name": "Expense Employee UX Product",
                "type": "service",
                "can_be_expensed": True,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Expense Employee UX Analytic",
                "company_id": cls.env.company.id,
            }
        )

    def _create_category(self, product=None):
        return self.env["autoinfo.expense.category"].create(
            {
                "name": "Office Supplies",
                "code": "office_supplies",
                "product_id": (product or self.expense_product).id,
                "company_id": self.env.company.id,
            }
        )

    def _get_cash_tracking_view_arch_root(self):
        view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_hr_expense_form_cash_tracking"
        )
        return etree.fromstring(view.arch_db.encode())

    def _get_rendered_form_nodes(self, user):
        arch = self.env["hr.expense"].with_user(user).fields_view_get(view_type="form")["arch"]
        root = etree.fromstring(arch.encode())
        category_node = root.xpath(".//field[@name='expense_category_id']")[0]
        product_node = category_node.xpath("./following-sibling::field[@name='product_id'][1]")[0]
        return category_node, product_node

    def test_expense_category_sets_product_on_create(self):
        category = self._create_category()
        expense = self.env["hr.expense"].create(
            {
                "name": "Taxi",
                "employee_id": self.employee.id,
                "expense_category_id": category.id,
                "date": "2026-07-03",
                "unit_amount": 250.0,
                "quantity": 1.0,
                "payment_mode": "own_account",
                "analytic_account_id": self.analytic_account.id,
            }
        )

        self.assertEqual(expense.product_id, self.expense_product)

    def test_expense_category_sets_product_onchange(self):
        category = self._create_category()
        expense = self.env["hr.expense"].new(
            {
                "name": "Taxi",
                "employee_id": self.employee.id,
                "expense_category_id": category.id,
                "unit_amount": 250.0,
                "quantity": 1.0,
            }
        )

        expense._onchange_expense_category_id()

        self.assertEqual(expense.product_id, self.expense_product)

    def test_check_expense_category_mapping_blocks_missing_product(self):
        category = self._create_category()
        expense = self.env["hr.expense"].new(
            {
                "name": "Taxi",
                "employee_id": self.employee.id,
                "expense_category_id": category.id,
                "unit_amount": 250.0,
                "quantity": 1.0,
            }
        )

        with self.assertRaises(UserError):
            expense._check_expense_category_mapping()

    def test_expense_category_maps_to_product(self):
        category = self.env["autoinfo.expense.category"].create(
            {
                "name": "Office Supplies",
                "code": "office_supplies",
                "product_id": self.expense_product.id,
                "company_id": self.env.company.id,
            }
        )
        expense = self.env["hr.expense"].create(
            {
                "name": "UX Expense",
                "employee_id": self.employee.id,
                "expense_category_id": category.id,
                "date": "2026-07-03",
                "unit_amount": 100.0,
                "quantity": 1.0,
                "payment_mode": "own_account",
                "analytic_account_id": self.analytic_account.id,
            }
        )

        self.assertEqual(expense.product_id, self.expense_product)

    def test_expense_category_flow_keeps_cash_tracking_default_for_own_account(self):
        category = self._create_category()
        expense = self.env["hr.expense"].create(
            {
                "name": "Taxi",
                "employee_id": self.employee.id,
                "expense_category_id": category.id,
                "date": "2026-07-03",
                "unit_amount": 250.0,
                "quantity": 1.0,
                "payment_mode": "own_account",
                "analytic_account_id": self.analytic_account.id,
            }
        )
        sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense Employee UX Sheet Default",
                "company_id": self.env.company.id,
                "employee_id": self.employee.id,
                "expense_line_ids": [(6, 0, expense.ids)],
            }
        )

        self.assertEqual(expense.product_id, self.expense_product)
        self.assertEqual(sheet.cash_tracking_state, "not_applicable")

    def test_sheet_submit_blocks_when_category_mapping_is_invalid(self):
        category = self._create_category()
        stale_product = self.env["product.product"].create(
            {
                "name": "Expense Employee UX Stale Product",
                "type": "service",
                "can_be_expensed": True,
            }
        )
        expense = self.env["hr.expense"].create(
            {
                "name": "Taxi",
                "employee_id": self.employee.id,
                "expense_category_id": category.id,
                "product_id": stale_product.id,
                "date": "2026-07-03",
                "unit_amount": 250.0,
                "quantity": 1.0,
                "payment_mode": "own_account",
                "analytic_account_id": self.analytic_account.id,
            }
        )
        sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense Employee UX Sheet",
                "company_id": self.env.company.id,
                "employee_id": self.employee.id,
                "expense_line_ids": [(6, 0, expense.ids)],
            }
        )

        with self.assertRaises(UserError):
            sheet.action_submit_sheet()

    def test_expense_category_config_action_exists(self):
        action = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.action_expense_category"
        )

        self.assertEqual(action.type, "ir.actions.act_window")
        self.assertEqual(action.res_model, "autoinfo.expense.category")
        self.assertEqual(action.view_mode, "tree,form")

    def test_expense_category_config_views_exist(self):
        tree_view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_expense_category_tree"
        )
        form_view = self.env.ref(
            "autoinfo_hr_expense_cash_tracking.view_expense_category_form"
        )

        self.assertEqual(tree_view.model, "autoinfo.expense.category")
        self.assertIn('<field name="product_id"/>', tree_view.arch_db)
        self.assertEqual(form_view.model, "autoinfo.expense.category")
        self.assertIn('<field name="note"/>', form_view.arch_db)

    def test_expense_category_access_is_limited_to_managers(self):
        manager_model = self.env["autoinfo.expense.category"].with_user(self.manager_user)
        employee_model = self.env["autoinfo.expense.category"].with_user(
            self.employee_user
        )

        self.assertTrue(manager_model.check_access_rights("read", raise_exception=False))
        self.assertTrue(
            manager_model.check_access_rights("create", raise_exception=False)
        )
        self.assertFalse(
            employee_model.check_access_rights("read", raise_exception=False)
        )
        self.assertFalse(
            employee_model.check_access_rights("create", raise_exception=False)
        )

        manager_category = manager_model.create(
            {
                "name": "Manager Only Category",
                "code": "manager_only_category",
                "product_id": self.expense_product.id,
                "company_id": self.env.company.id,
            }
        )
        self.assertTrue(manager_category)

        with self.assertRaises(AccessError):
            employee_model.create(
                {
                    "name": "Employee Forbidden Category",
                    "code": "employee_forbidden_category",
                    "product_id": self.expense_product.id,
                    "company_id": self.env.company.id,
                }
            )

    def test_expense_form_contains_expense_category_field(self):
        view_root = self._get_cash_tracking_view_arch_root()
        expense_category_nodes = view_root.xpath(".//field[@name='expense_category_id']")

        self.assertTrue(expense_category_nodes)

    def test_employee_form_hides_product_field_from_general_users(self):
        category_node, product_node = self._get_rendered_form_nodes(self.employee_user)

        self.assertEqual(category_node.get("name"), "expense_category_id")
        self.assertEqual(product_node.get("name"), "product_id")
        self.assertEqual(product_node.get("invisible"), "1")

    def test_accounting_reviewer_form_keeps_product_field_visible(self):
        category_node, product_node = self._get_rendered_form_nodes(self.accounting_user)

        self.assertEqual(category_node.get("name"), "expense_category_id")
        self.assertEqual(product_node.get("name"), "product_id")
        self.assertNotEqual(product_node.get("invisible"), "1")

    def test_manager_form_keeps_product_field_visible(self):
        category_node, product_node = self._get_rendered_form_nodes(self.manager_user)

        self.assertEqual(category_node.get("name"), "expense_category_id")
        self.assertEqual(product_node.get("name"), "product_id")
        self.assertNotEqual(product_node.get("invisible"), "1")
