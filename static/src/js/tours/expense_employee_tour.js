odoo.define('autoinfo_hr_expense_cash_tracking.expense_employee_tour', function (require) {
"use strict";

const {_t} = require('web.core');
const {Markup} = require('web.utils');
const tour = require('web_tour.tour');

tour.register('autoinfo_expense_employee_tour', {
    url: "/web",
    rainbowManMessage: _t("เยี่ยมมาก! คุณส่งเบิกค่าใช้จ่ายได้แล้ว รอหัวหน้าแผนกอนุมัติได้เลย"),
    sequence: 60,
}, [tour.stepUtils.showAppsMenuItem(), {
    trigger: '.o_app[data-menu-xmlid="hr_expense.menu_hr_expense_root"]',
    content: Markup(_t("<b>เริ่มเบิกค่าใช้จ่าย</b> ได้ที่แอป Expenses")),
    position: 'right',
    edition: 'community',
}, {
    trigger: '.o_app[data-menu-xmlid="hr_expense.menu_hr_expense_root"]',
    content: Markup(_t("<b>เริ่มเบิกค่าใช้จ่าย</b> ได้ที่แอป Expenses")),
    position: 'bottom',
    edition: 'enterprise',
}, {
    trigger: '.o_list_button_add, .o-kanban-button-new',
    extra_trigger: '.o_breadcrumb',
    content: Markup(_t("กด <b>Create</b> เพื่อสร้างรายการค่าใช้จ่ายใหม่ (1 ใบเสร็จ = 1 รายการ)")),
    position: 'bottom',
}, {
    trigger: '.o_expense_form .o_field_widget[name="name"]',
    content: Markup(_t("ใส่ <b>คำอธิบาย</b> ค่าใช้จ่าย เช่น ค่าแท็กซี่ไปพบลูกค้า")),
    position: 'bottom',
}, {
    trigger: '.o_expense_form .o_field_widget[name="expense_category_id"] input',
    content: Markup(_t("เลือก <b>Expense Category</b> ให้ตรงประเภทค่าใช้จ่าย ระบบจะผูกบัญชีให้อัตโนมัติ")),
    position: 'right',
}, {
    trigger: '.o_expense_form .o_field_widget[name="total_amount"] input, .o_expense_form input.o_field_widget[name="total_amount"]',
    content: Markup(_t("ระบุ <b>จำนวนเงินรวม</b> ตามใบเสร็จ (รวม VAT)")),
    position: 'right',
}, {
    trigger: '.o_expense_form .o_field_widget[name="date"] input',
    content: Markup(_t("ระบุ <b>วันที่</b> ตามใบเสร็จ")),
    position: 'right',
}, {
    trigger: '.o_expense_form .o_field_widget[name="analytic_account_id"] input',
    content: Markup(_t("เลือก <b>Analytic Account</b> (บังคับ) เช่น แผนก / โครงการที่ใช้จ่าย")),
    position: 'right',
}, {
    trigger: '.o_expense_form .o_field_widget[name="payment_mode"]',
    content: Markup(_t("<b>Paid By</b>: เลือก <i>Employee (to reimburse)</i> หากจ่ายด้วยเงินตัวเองและต้องการเบิกคืน")),
    position: 'left',
}, {
    trigger: '.o_form_button_save',
    extra_trigger: '.o_expense_form',
    content: Markup(_t("กด <b>Save</b> เพื่อบันทึกรายการ")),
    position: 'bottom',
}, {
    trigger: '.o_attach_document',
    extra_trigger: '.o_expense_form .o_form_readonly, .o_expense_form.o_form_readonly',
    content: Markup(_t("กด <b>Attach Receipt</b> เพื่อแนบรูป/ไฟล์ใบเสร็จ (จำเป็นสำหรับการตรวจสอบ)")),
    position: 'bottom',
}, {
    trigger: '.o_expense_submit',
    extra_trigger: '.o_expense_form',
    content: Markup(_t("กด <b>Create Report</b> เพื่อรวมรายการเข้ารายงานเบิก (เพิ่มหลายรายการในรายงานเดียวได้)")),
    position: 'bottom',
}, {
    trigger: '.o_expense_sheet .o_field_widget[name="name"]',
    content: Markup(_t("ตั้ง <b>ชื่อรายงานเบิก</b> เช่น เบิกค่าเดินทาง ต.ค. 2026")),
    position: 'bottom',
}, {
    trigger: '.o_expense_sheet .o_field_widget[name="department_head_user_id"]',
    content: Markup(_t("ตรวจสอบ <b>Department Head</b> ผู้อนุมัติ ระบบเลือกหัวหน้าแผนกให้อัตโนมัติ เปลี่ยนได้หากไม่ถูกต้อง")),
    position: 'right',
}, {
    trigger: '.o_expense_sheet .o_field_widget[name="reimbursement_method"]',
    content: Markup(_t("เลือก <b>Reimbursement Method</b> วิธีรับเงินคืน")),
    position: 'left',
}, {
    trigger: '.o_form_button_save',
    extra_trigger: '.o_expense_sheet',
    content: Markup(_t("กด <b>Save</b> เพื่อบันทึกรายงานเบิก")),
    position: 'bottom',
}, {
    trigger: 'button[name="action_request_cash_tracking_validation"]',
    extra_trigger: '.o_expense_sheet.o_form_readonly, .o_expense_sheet .o_form_readonly',
    content: Markup(_t("กด <b>Request Validation</b> เพื่อส่งให้หัวหน้าแผนกอนุมัติ<br/>หากถูก <i>Return</i> กลับมา ให้ดูเหตุผลในส่วน Cash Reimbursement แก้ไข แล้วกดปุ่มนี้อีกครั้ง")),
    position: 'bottom',
}, {
    trigger: '.o_expense_sheet .o_statusbar_status',
    content: Markup(_t("ติดตาม <b>สถานะ</b> รายงานได้ที่นี่ และดูรายงานทั้งหมดได้ที่เมนู <b>My Reports</b>")),
    position: 'bottom',
}]);

});
