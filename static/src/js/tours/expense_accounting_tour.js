odoo.define('autoinfo_hr_expense_cash_tracking.expense_accounting_tour', function (require) {
"use strict";

const {_t} = require('web.core');
const {Markup} = require('web.utils');
const tour = require('web_tour.tour');

tour.register('autoinfo_expense_accounting_tour', {
    url: "/web",
    rainbowManMessage: _t("เยี่ยมมาก! คุณตรวจสอบ อนุมัติ และจ่ายเงินคืนรายงานเบิกได้ครบขั้นตอนแล้ว"),
    sequence: 61,
}, [tour.stepUtils.showAppsMenuItem(), {
    trigger: '.o_app[data-menu-xmlid="hr_expense.menu_hr_expense_root"]',
    content: Markup(_t("<b>ฝั่งบัญชี</b> เริ่มตรวจสอบรายงานเบิกได้ที่แอป Expenses")),
    position: 'right',
    edition: 'community',
}, {
    trigger: '.o_app[data-menu-xmlid="hr_expense.menu_hr_expense_root"]',
    content: Markup(_t("<b>ฝั่งบัญชี</b> เริ่มตรวจสอบรายงานเบิกได้ที่แอป Expenses")),
    position: 'bottom',
    edition: 'enterprise',
}, {
    trigger: '.o_menu_sections [data-menu-xmlid="hr_expense.menu_hr_expense_report"]',
    content: Markup(_t("เปิดเมนู <b>Expense Reports</b>")),
    position: 'bottom',
}, {
    trigger: '[data-menu-xmlid="hr_expense.menu_hr_expense_sheet_all"]',
    content: Markup(_t("เลือก <b>All Reports</b> เพื่อดูรายงานเบิกทั้งหมด<br/>" +
        "<i>Reports to Post</i> = อนุมัติแล้วรอลงบัญชี, <i>Reports to Pay</i> = ลงบัญชีแล้วรอจ่าย")),
    position: 'right',
}, {
    trigger: '.o_searchview_input',
    extra_trigger: '.o_list_view, .o_kanban_view',
    content: Markup(_t("ใช้ตัวกรอง <b>Needs my Review</b> เพื่อดูรายงานที่รอคุณตรวจ " +
        "หรือ <b>Validated</b> เพื่อดูรายงานที่ผ่าน tier validation แล้ว (เมนู Filters)")),
    position: 'bottom',
}, {
    trigger: '.o_data_row:first .o_data_cell:first, .o_kanban_record:first',
    content: Markup(_t("คลิกเปิด <b>รายงานเบิก</b> ที่ต้องการตรวจสอบ")),
    position: 'bottom',
}, {
    trigger: '.o_expense_sheet .o_field_widget[name="expense_line_ids"]',
    content: Markup(_t("<b>ตรวจรายการค่าใช้จ่าย</b>: ใบเสร็จแนบครบ, จำนวนเงินถูกต้อง, " +
        "Expense Category / Product และ <b>Analytic Account</b> ถูกต้อง")),
    position: 'top',
}, {
    trigger: '.o_expense_sheet .o_field_widget[name="cash_tracking_state"]',
    content: Markup(_t("ดูสถานะ <b>Cash Tracking</b> และ <b>Reimbursement Method</b> ที่พนักงานเลือก")),
    position: 'left',
}, {
    trigger: 'button[name="validate_tier"], button[name="approve_expense_sheets"]',
    extra_trigger: '.o_expense_sheet',
    content: Markup(_t("กด <b>Validate</b> เพื่อผ่านการตรวจสอบในขั้นของคุณ (ต้องผ่านทุก tier ก่อนจึงจะ Approve ได้)<br/>" +
        "หากพบปัญหา: กด <b>Reject</b> เพื่อปฏิเสธ หรือ <b>Return</b> พร้อมระบุเหตุผลให้พนักงานแก้ไขและส่งใหม่")),
    position: 'bottom',
}, {
    trigger: 'button[name="approve_expense_sheets"]',
    extra_trigger: '.o_expense_sheet',
    content: Markup(_t("เมื่อ validate ครบทุก tier แล้ว กด <b>Approve Report</b> เพื่ออนุมัติรายงาน")),
    position: 'bottom',
}, {
    trigger: 'button[name="action_sheet_move_create"]',
    extra_trigger: '.o_expense_sheet',
    content: Markup(_t("กด <b>Post Entries</b> เพื่อสร้างรายการบันทึกบัญชี (Journal Entry)")),
    position: 'bottom',
}, {
    trigger: '.o_expense_sheet .o_field_widget[name="cash_reference"]',
    content: Markup(_t("กรณีจ่ายเงินสด/เงินสดย่อย ระบุ <b>Cash Reference</b> (เลขที่ใบสำคัญจ่าย) " +
        "และ <b>Cash Note</b> เพื่อใช้อ้างอิงภายหลัง")),
    position: 'left',
}, {
    trigger: 'button[name="action_register_payment"], button[name="action_mark_cash_reimbursed"]',
    extra_trigger: '.o_expense_sheet',
    content: Markup(_t("จ่ายเงินคืนพนักงาน:<br/>" +
        "- โอน/เช็ค: กด <b>Register Payment</b><br/>" +
        "- เงินสด/เงินสดย่อย: กด <b>Mark Cash Reimbursed</b> ระบบจะบันทึกผู้จ่ายและวันที่จ่ายให้อัตโนมัติ")),
    position: 'bottom',
}, {
    trigger: '.o_expense_sheet .o_form_statusbar button:contains("Summary XLSX")',
    content: Markup(_t("กด <b>Summary XLSX</b> เพื่อดึงรายงานสรุปการเบิกจ่ายเงินสดเป็นไฟล์ Excel")),
    position: 'bottom',
}]);

});
