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

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
