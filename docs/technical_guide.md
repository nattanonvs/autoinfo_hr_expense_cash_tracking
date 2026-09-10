# คู่มือทางเทคนิค

## การติดตั้งและอัปเกรด

1. วางโฟลเดอร์โมดูลไว้ที่ `/var/odoo/custom15_autoinfo/autoinfo_hr_expense_cash_tracking`
2. ตรวจว่า dependency ติดตั้งครบ
3. สำรองฐานข้อมูล
4. อัปเกรดโมดูลด้วย `--stop-after-init`
5. เปิด service และทดสอบฟอร์ม `Expense`, `Expense Sheet`, และเมนู `Expense Categories`

ตัวอย่างคำสั่ง:

```bash
sudo systemctl stop odoo15
cd /var/odoo/odoo15
./odoo-bin -c /etc/odoo.conf -d <database_name> -u autoinfo_hr_expense_cash_tracking --stop-after-init
sudo systemctl start odoo15
```

## สถาปัตยกรรมโดยย่อ

โมดูลนี้ขยาย `hr.expense` และ `hr.expense.sheet` เพื่อรองรับงานคืนเงินสด, validation หลายขั้น, Excel export และ UX แบบง่ายขึ้นสำหรับพนักงานทั่วไป

รอบปัจจุบันเพิ่ม `Expense Category` เป็นชั้นกลางระหว่างพนักงานกับ `product_id` ของบัญชี โดยไม่แก้ Odoo core

## โครงสร้างหลักของโมดูล

- `models/hr_expense.py`
  เพิ่ม `expense_category_id`, auto-map ไป `product_id`, และบังคับ `Analytic Account`
- `models/expense_category.py`
  เก็บ master data ของ `Expense Category` และ mapping ไป `product.product`
- `models/hr_expense_sheet.py`
  ตรวจ analytic account, ตรวจ category mapping ตอน submit, เก็บสถานะคืนเงินสด และจัดการ return cycle
- `models/expense_approval_delegate.py`
  ใช้ resolve ผู้แทนอนุมัติ
- `models/expense_approval_role.py`
  เก็บ role ของผู้อนุมัติ
- `views/hr_expense_views.xml`
  แทรก `expense_category_id` ก่อน `product_id` และจำกัดการเห็น `product_id` ตาม group
- `views/expense_category_views.xml`
  เพิ่ม tree/form/action/menu สำหรับตั้งค่า `Expense Category`
- `wizard/expense_return_reason_wizard.py`
  ใช้ตีกลับเอกสารพร้อมเหตุผล
- `wizard/expense_cash_summary_xlsx_wizard.py`
  ใช้เลือกช่วงวันที่ก่อน export Excel
- `reports/expense_cash_detail_xlsx.py`
  ทำ Excel แบบใบเดี่ยว
- `reports/expense_cash_summary_xlsx.py`
  ทำ Excel แบบหลายใบ

## Data Model

### `autoinfo.expense.category`

ฟิลด์หลัก:

- `name`
- `code`
- `product_id`
- `company_id`
- `active`
- `note`

พฤติกรรม:

- `product_id` เป็นฟิลด์บังคับ
- ใช้เป็น source of truth สำหรับ mapping ไป `hr.expense.product_id`
- จำกัดสิทธิ์การจัดการไว้ที่ `hr_expense.group_hr_expense_manager`

### `hr.expense`

ฟิลด์และ logic ที่เพิ่ม:

- `expense_category_id`
- `_onchange_expense_category_id()`
- `create()` override เพื่อเติม `product_id` อัตโนมัติถ้าส่ง `expense_category_id`
- `_check_expense_category_mapping()` เพื่อ block รายการที่เลือกหมวดแต่ไม่มี `product`
- `_check_cash_tracking_analytic_account()` เพื่อบังคับ `Analytic Account`

### `hr.expense.sheet`

logic ที่เกี่ยวข้อง:

- `_check_all_lines_have_analytic_account()`
- `_check_all_lines_have_valid_expense_category_mapping()`
- `action_submit_sheet()` เรียก validation ของ analytic account และ category mapping ก่อนส่ง
- `action_request_cash_tracking_validation()` reset รอบเอกสารถูกตีกลับ
- `action_mark_cash_reimbursed()` บันทึกสถานะคืนเงินสดและ audit fields

## พฤติกรรมของฟอร์มตามสิทธิ์

### พนักงานทั่วไป

- เห็น `expense_category_id`
- ไม่เห็น `product_id` ใน rendered form
- ยังต้องกรอก `analytic_account_id`

### Accounting Reviewer และ Expense Manager

- เห็นทั้ง `expense_category_id` และ `product_id`
- ใช้ตรวจว่าหมวดค่าใช้จ่าย map ไป product ที่ถูกต้อง

## Validation ที่สำคัญ

1. ถ้าไม่มี `Analytic Account` บน expense line ใด line หนึ่ง จะ submit sheet ไม่ได้
2. ถ้าเลือก `Expense Category` แล้วไม่มี `product_id` หรือ `product_id` ไม่ตรงกับ mapping จะ submit sheet ไม่ได้
3. ถ้า Tier Validation ยังไม่ครบ จะ approve/post ต่อไม่ได้

## Security และเมนู

- `Expense Categories` อยู่ใต้ `Expenses > Configuration`
- ACL ของ `autoinfo.expense.category` เปิดให้เฉพาะ `hr_expense.group_hr_expense_manager`
- ฝั่ง employee ใช้การ render view ตาม group เพื่อซ่อน `product_id`

## Dependency

- `hr_expense`
- `mail`
- `analytic`
- `report_xlsx`
- `base_tier_validation`
- `dtr_expense_tier_validation`

## การทดสอบที่มีในโมดูล

- `tests/test_expense_employee_ux.py`
  ครอบคลุม category mapping, visibility ตาม group, config action และ regression เชื่อม UX ใหม่กับ cash tracking default
- `tests/test_expense_cash_tracking_flow.py`
  ครอบคลุม analytic account gate, validation gate, return flow, reimbursement และ wizard actions
- `tests/test_expense_cash_tracking_security.py`
  ครอบคลุม visibility ของ sheet ตามกลุ่มสิทธิ์
- `tests/test_expense_cash_tracking_xlsx.py`
  ครอบคลุม detail/summary XLSX actions

## การถอนการติดตั้ง

1. เข้า Apps ใน Odoo
2. ค้นหา `AUTO-INFO : HR Expense Cash Tracking`
3. กด `Uninstall`
4. ตรวจว่าเมนู `Expense Categories` และ view ที่เกี่ยวข้องถูกลบออก

ถ้าถอนผ่านคำสั่ง ให้ทำในฐานทดสอบก่อนเสมอ

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon - Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
