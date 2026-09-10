# AUTO-INFO : HR Expense Cash Tracking

## โมดูลนี้คืออะไร

โมดูลนี้ขยาย `hr_expense` บน Odoo 15 สำหรับงานเบิกค่าใช้จ่ายที่พนักงานสำรองจ่ายเองและต้องการติดตามการคืนเงินสดอย่างเป็นขั้นตอน

รอบปัจจุบันของโมดูลเพิ่มฟีเจอร์ `Expense Category` เพื่อให้พนักงานทั่วไปกรอกฟอร์ม `Expense` ได้ง่ายขึ้น โดยระบบจะ map ไปยัง `product_id` จริงของบัญชีให้อัตโนมัติ

โมดูลนี้ไม่สร้างเอกสาร `dtr_petty_cash` อัตโนมัติ

## ฟีเจอร์หลัก

- รวมหลาย `Expense` เป็น `Expense Sheet` เดียวเพื่อขอคืนเงินสด
- บังคับกรอก `Analytic Account` ก่อนส่งขออนุมัติ
- ใช้ `Tier Validation` กับรอบการตีกลับและส่งใหม่
- เพิ่ม `Expense Category` สำหรับพนักงาน และ map ไป `product` อัตโนมัติ
- ซ่อน `product_id` จากผู้ใช้พนักงานทั่วไป แต่ยังให้บัญชีและผู้จัดการเห็นข้อมูลจริง
- บล็อกการ submit ถ้า mapping ของ `Expense Category` ไม่ครบหรือมีการเปลี่ยน `product` ไม่ตรง mapping
- ส่งออก Excel ได้ทั้งแบบรายใบและสรุปหลายใบ

## ขอบเขตการทำงาน

- ทำงานต่อจาก `hr_expense`
- ใช้ร่วมกับ `dtr_expense_tier_validation`
- เหมาะกับงานที่พนักงานสำรองจ่ายแล้วขอคืนภายหลัง
- ให้ฝ่ายบัญชีหรือผู้จัดการดูแลตาราง `Expense Category`

## กลุ่มผู้ใช้หลัก

- พนักงานทั่วไป: เลือก `Expense Category`, กรอกจำนวนเงิน, วันที่, รายละเอียด และ `Analytic Account`
- ผู้จัดการ Expense: ตั้งค่า `Expense Category` และตรวจสอบเอกสาร
- Accounting Reviewer: เห็น `product_id` จริงเพื่อตรวจ mapping และข้อมูลบัญชี
- Finance Reimbursement Manager: ปิดงานคืนเงินสดและบันทึกข้อมูลการจ่าย

## Dependencies

โมดูลนี้ต้องใช้:

- `hr_expense`
- `mail`
- `analytic`
- `report_xlsx`
- `base_tier_validation`
- `dtr_expense_tier_validation`

## สรุปการติดตั้ง

1. วางโมดูลไว้ที่ `/var/odoo/custom15_autoinfo/autoinfo_hr_expense_cash_tracking`
2. สำรองฐานข้อมูลก่อนอัปเกรด
3. อัปเกรดโมดูลแบบ `--stop-after-init`
4. ตรวจสิทธิ์กลุ่มผู้ใช้และ `Tier Definition`
5. ให้ผู้จัดการสร้าง `Expense Category` อย่างน้อยตามหมวดใช้งานจริง

ตัวอย่างคำสั่ง:

```bash
sudo systemctl stop odoo15
cd /var/odoo/odoo15
./odoo-bin -c /etc/odoo.conf -d <database_name> -u autoinfo_hr_expense_cash_tracking --stop-after-init
sudo systemctl start odoo15
```

## การตั้งค่าหลังติดตั้ง

1. ไปที่ `Expenses > Configuration > Expense Categories`
2. สร้างหมวดค่าใช้จ่ายที่พนักงานเข้าใจง่าย
3. ผูกแต่ละหมวดเข้ากับ `product` จริงที่บัญชีต้องการใช้
4. ทดสอบสร้าง `Expense` โดยเลือกหมวดแทนการเลือก `product` เอง

## เอกสารประกอบ

- `docs/user_guide.md`: ขั้นตอนใช้งานของพนักงาน บัญชี และการเงิน
- `docs/technical_guide.md`: โครงสร้าง model, view, validation และ test coverage
- `docs/installation_guide.md`: ขั้นตอนติดตั้งและอัปเกรด
- `docs/troubleshooting.md`: แนวทางตรวจปัญหาที่พบบ่อย

## Ownership

- Module Type: EXTENDED
- Base Module Owner: Odoo S.A.
- Related Extension Owner Found: Dataroot Asia Co., Ltd.
- Current Delivery Owner: The Auto-Info Co., Ltd.

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon - Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.

## Changelog Summary

- `2026-09-10`
- เพิ่ม `Expense Category` และ simplified employee form ตามสถานะโค้ดจริง
- ปรับ README และคู่มือให้สะท้อนสิทธิ์การมองเห็นและ validation ปัจจุบัน
- ตรวจ full regression ของ `expense_employee_ux`, `expense_cash_tracking_flow`, `expense_cash_tracking_security`, และ `expense_cash_tracking_xlsx`
