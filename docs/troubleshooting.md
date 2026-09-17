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
2. เอกสารต้องอยู่ที่ `submit`, `approve` หรือ `post`
3. ถ้าเอกสารเป็น `draft` ปุ่มนี้จะไม่แสดง
4. ถ้าเอกสารอยู่ที่ `post` ปุ่มยังแสดงได้ แต่จะยืนยัน reset ไม่ผ่านเมื่อมี `account_move_id`

## ปัญหา: กดยืนยัน Reset to Draft แล้วระบบไม่ให้ผ่าน

ให้เช็กตามนี้:

1. ต้องกรอกเหตุผลใน wizard ห้ามปล่อยว่าง
2. ถ้าเอกสารเป็น `draft` อยู่แล้ว ระบบจะไม่ยอม reset ซ้ำ
3. ถ้าเอกสารอยู่ใน state ที่ระบบไม่รองรับ ระบบจะไม่ยอมให้ทำต่อ
4. ถ้าเอกสารอยู่ที่ `post` ให้เช็กว่าไม่มี `account_move_id` ผูกอยู่
5. ตรวจว่า user อยู่ในกลุ่ม `Expense Manager`
6. เปิด `Chatter` เพื่อดู log reset ล่าสุดว่าระบบแจ้งเหตุผลอะไร

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

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon - Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
