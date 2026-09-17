# วิธีแก้ปัญหา

## ปัญหา: ส่ง Expense Sheet ไม่ได้

ให้เช็กตามนี้:

1. เปิดทุกบรรทัดของค่าใช้จ่าย
2. ดูว่ามี `Analytic Account` ครบหรือไม่
3. ดูว่าเอกสารยังค้างอนุมัติใน `Tier Validation` หรือไม่

## ปัญหา: ฝ่ายการเงินกดคืนเงินไม่ได้

ให้เช็กตามนี้:

1. ผู้ใช้ต้องอยู่ในกลุ่ม `group_expense_cash_reimbursement_manager`
2. เปิดเอกสารจากหน้า `Expense Sheet`
3. ตรวจว่าเอกสารผ่านขั้นอนุมัติที่ต้องผ่านแล้ว

## ปัญหา: ไม่เห็นข้อความตีกลับ

ให้เช็กตามนี้:

1. เปิดเอกสารที่ถูกตีกลับ
2. เลื่อนดู `Chatter`
3. ดูว่ามีเหตุผลการตีกลับในฟอร์มหรือไม่
4. ดูว่า `returned_for_resubmission` ถูกเปิดแล้วหรือไม่

## ปัญหา: ไม่เห็นปุ่ม Reset to Draft

ให้เช็กตามนี้:

1. ผู้ใช้ต้องอยู่ในกลุ่ม `Expense Manager`
2. เอกสารต้องอยู่ที่ `submit`, `approve`, `post` หรือ `done` ที่ยัง `not_paid`
3. ถ้าเอกสารเป็น `draft` ปุ่มนี้จะไม่แสดง
4. ถ้าเอกสารอยู่ที่ `post` ปุ่มยังแสดงได้ แต่จะยืนยัน reset ไม่ผ่านเมื่อมี `account_move_id`
5. ถ้าเอกสารอยู่ที่ `done` ให้เช็ก `payment_state` ว่ายังเป็น `not_paid`

## ปัญหา: กดยืนยัน Reset to Draft แล้วระบบไม่ให้ผ่าน

ให้เช็กตามนี้:

1. ต้องกรอกเหตุผลใน wizard ห้ามปล่อยว่าง
2. ถ้าเอกสารเป็น `draft` อยู่แล้ว ระบบจะไม่ยอม reset ซ้ำ
3. ถ้าเอกสารอยู่ใน state ที่ระบบไม่รองรับ ระบบจะไม่ยอมให้ทำต่อ
4. ถ้าเอกสารอยู่ที่ `post` ให้เช็กว่าไม่มี `account_move_id` ผูกอยู่
5. ถ้าเอกสารอยู่ที่ `done` ให้เช็กว่า `payment_state` ยังเป็น `not_paid`
6. ตรวจว่า user อยู่ในกลุ่ม `Expense Manager`
7. เปิด `Chatter` เพื่อดู log reset ล่าสุดว่าระบบแจ้งเหตุผลอะไร

## ปัญหา: export Excel ไม่ได้

ให้เช็กตามนี้:

1. โมดูล `report_xlsx` ต้องติดตั้งแล้ว
2. ถ้าเป็นแบบใบเดี่ยว ให้เช็กว่าเปิด Expense Sheet ถูกใบ
3. ถ้าเป็นแบบหลายใบ ให้เช็กช่วงวันที่ใน wizard
4. ถ้าไม่มีข้อมูลในช่วงวันที่ ระบบอาจได้ไฟล์ว่าง

## ปัญหา: เปิดเมนู config ไม่ได้

ให้เช็กตามนี้:

1. ผู้ใช้ต้องมีสิทธิ์ที่เกี่ยวข้อง
2. โมดูลต้องติดตั้งครบ
3. ถ้ายังไม่เห็นเมนู ให้รีเฟรชหน้า Odoo

## แนวทางกู้คืนเบื้องต้น

1. สำรองฐานข้อมูลก่อนทุกครั้ง
2. หยุด Odoo service
3. รันอัปเกรดโมดูลใหม่อีกครั้งด้วย `--stop-after-init`
4. เปิด service
5. ทดสอบเมนูและปุ่มหลักใหม่

## ปัญหา: port 8069 ถูกใช้งานอยู่แล้ว

ให้เช็กตามนี้:

1. ถ้าเจอ `OSError: [Errno 98] Address already in use` แปลว่ามี process ใช้ port `8069` อยู่
2. หยุด service ก่อนรันอัปเดตด้วย `sudo systemctl stop odoo`
3. ถ้าหยุด service ไม่ได้ ให้รันชั่วคราวด้วย `--http-port=8070`
4. หลังอัปเดตเสร็จค่อย `sudo systemctl start odoo`

## ปัญหา: ขาด Python package ตอนเริ่ม Odoo

ให้เช็กตามนี้:

1. ยืนยัน Python ที่ใช้รันจริงด้วย `head -n 1 /var/odoo/odoo15/odoo-bin`
2. แนะนำติดตั้งทั้งชุดก่อนด้วย `python3 -m pip install -r /var/odoo/odoo15/requirements.txt`
3. ถ้าขาดเฉพาะตัว ให้ติดตั้ง `PyPDF2 Pillow reportlab Babel passlib pdfminer.six`
4. ถ้าจะตรวจทีละตัว ให้ใช้ `python3 -c "import PyPDF2, PIL, reportlab, babel, passlib"`

## ปัญหา: `actual_due_date` ไม่มีใน `account.move`

ให้เช็กตามนี้:

1. field นี้มาจากโมดูล `dtr_billing`
2. โมดูลที่อ้าง field นี้ต้องมี `dtr_billing` อยู่ใน `depends`
3. โมดูลที่พบจริงในรอบนี้คือ `dtr_customer_invoices`, `dtr_customer_invoices_with_sales`, `dtr_payment_invoice`, `dtr_vendor_bills_with_purchase`
4. ถ้าต้องแก้ทีเดียว ใช้คำสั่ง Python อัตโนมัติชุดเดียว:

```bash
python3 - <<'PY'
from pathlib import Path

targets = [
    Path('/var/odoo/odoo15_mods/dtr_customer_invoices/__manifest__.py'),
    Path('/var/odoo/odoo15_mods_accounting/dtr_customer_invoices_with_sales/__manifest__.py'),
    Path('/var/odoo/odoo15_mods_accounting/dtr_payment_invoice/__manifest__.py'),
    Path('/var/odoo/odoo15_mods_accounting/dtr_vendor_bills_with_purchase/__manifest__.py'),
]

for path in targets:
    text = path.read_text(encoding='utf-8')
    if "'dtr_billing'" in text:
        print(f'SKIP {path}')
        continue
    marker = "'depends': ["
    pos = text.find(marker)
    if pos == -1:
        print(f'NO_DEPENDS {path}')
        continue
    insert_at = text.find('[', pos) + 1
    text = text[:insert_at] + "'dtr_billing', " + text[insert_at:]
    path.write_text(text, encoding='utf-8')
    print(f'UPDATED {path}')
PY
```

## ปัญหา: `is_customer_and_supplier` ไม่มีใน `res.partner`

ให้เช็กตามนี้:

1. field นี้มาจาก `dtr_partner_master`
2. view และ domain ฝั่งบัญชีจะใช้งานผ่าน `dtr_taxation`
3. ให้รันอัปเดตสองโมดูลนี้คู่กัน

```bash
sudo systemctl stop odoo
cd /var/odoo
python3 /var/odoo/odoo15/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo_golive \
  -u dtr_partner_master,dtr_taxation \
  --stop-after-init
sudo systemctl start odoo
```

## ปัญหา: โมดูลค้างสถานะ `to upgrade`

ให้เช็กตามนี้:

1. อ่านรายชื่อด้วย `sudo -u postgres psql -At -d odoo_golive -c "select string_agg(name, ',') from ir_module_module where state='to upgrade';"`
2. ถ้ารายชื่อยาวมาก ให้แบ่งอัปเดตเป็น batch ตามกลุ่ม accounting, cash, sales, autoinfo
3. หลังอัปเดตแล้วตรวจซ้ำด้วย `select name, state from ir_module_module where state='to upgrade'`

## ปัญหา: มีการยิงเข้า DB เก่า

ให้เช็กตามนี้:

1. ถ้า log มี `FROMGOLIVE_15MAR2026 does not exist` แปลว่ามี client หรือ integration ใช้ชื่อฐานเก่า
2. ปรับ config ฝั่ง client, API, mobile app, webhook หรือ scheduled job ให้ชี้ `odoo_golive`
3. ปัญหานี้ไม่ใช่สาเหตุที่ทำให้รอบอัปเดตโมดูลล้ม แต่ควรแก้เพื่อให้ log สะอาด

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon - Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.

