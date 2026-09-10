# คู่มือการใช้งาน

## 1. โมดูลนี้คืออะไร

โมดูลนี้ช่วยจัดการงานเบิกค่าใช้จ่ายที่พนักงานสำรองจ่ายเอง แล้วรวมเป็น `Expense Sheet` เพื่อส่งตรวจ อนุมัติ ตีกลับ แก้ไข ส่งใหม่ และปิดงานคืนเงินสด

รอบปัจจุบันเพิ่ม `Expense Category` เพื่อให้พนักงานทั่วไปเลือกหมวดค่าใช้จ่ายที่เข้าใจง่าย แทนการเลือก `product` เชิงบัญชีด้วยตนเอง

## 2. ฟีเจอร์ที่ใช้งานได้จริง

- พนักงานเลือก `Expense Category` แล้วระบบเติม `product` ให้อัตโนมัติ
- ผู้ใช้พนักงานทั่วไปไม่เห็น `product_id` ในฟอร์ม `Expense`
- Accounting Reviewer และ Expense Manager ยังเห็น `product_id` จริง
- ทุกบรรทัดต้องมี `Analytic Account` ก่อนส่งขออนุมัติ
- ถ้า `Expense Category` map ไม่ครบ หรือ `product` ไม่ตรงกับหมวด ระบบจะ block ตอน submit
- `Expense Sheet` รองรับรอบการตีกลับและขออนุมัติใหม่
- ฝ่ายการเงินปิดสถานะคืนเงินสดได้
- ส่งออก Excel แบบรายใบและแบบสรุปช่วงวันที่ได้

## 3. ก่อนเริ่มใช้ ต้องเตรียมอะไร

1. ติดตั้งโมดูล `autoinfo_hr_expense_cash_tracking` แล้ว
2. ตั้งค่า `Tier Definition` สำหรับ `Expense Sheet`
3. มี `Analytic Account` ให้พนักงานเลือก
4. ผู้จัดการสร้าง `Expense Category` และผูก `product` ให้ครบ
5. กำหนดสิทธิ์ผู้ใช้ให้ถูกกลุ่ม

## 4. วิธีตั้งค่า Expense Category

### ผู้จัดการ Expense

1. ไปที่ `Expenses > Configuration > Expense Categories`
2. กดสร้างรายการใหม่
3. กรอก `Name` และ `Code`
4. เลือก `Product` ที่บัญชีต้องการให้ใช้จริง
5. ระบุ `Company` ถ้าต้องการแยกตามบริษัท
6. บันทึกข้อมูล

หมายเหตุ:

- หมวดค่าใช้จ่ายหนึ่งรายการผูกกับ `product` หลักได้หนึ่งตัว
- ถ้าไม่มีการตั้งค่า `product` ที่ถูกต้อง การส่งเอกสารจะไม่ผ่าน

## 5. วิธีใช้งานสำหรับพนักงาน

### สร้าง Expense

1. ไปที่เมนู `Expenses`
2. กดสร้างรายการค่าใช้จ่าย
3. กรอกชื่อรายการ วันที่ จำนวนเงิน และรายละเอียด
4. เลือก `Expense Category`
5. ใส่ `Analytic Account`
6. แนบหลักฐานถ้ามีกระบวนการภายในกำหนด
7. บันทึกรายการ

สิ่งที่พนักงานจะเห็นในฟอร์ม:

- เห็น `Expense Category`
- ไม่ต้องเลือก `product` เอง
- ยังต้องกรอก `Analytic Account` ตามกฎเดิม

### รวมเป็น Expense Sheet และส่งขออนุมัติ

1. เลือกรายการ `Expense` ที่ต้องการรวม
2. สร้าง `Expense Sheet`
3. ตรวจสอบข้อมูลรวม
4. กดส่งขออนุมัติ

ระบบจะ block หาก:

- มีบรรทัดใดไม่มี `Analytic Account`
- มีการเลือก `Expense Category` แต่ `product` ไม่ตรง mapping

## 6. วิธีใช้งานสำหรับผู้ตรวจและฝ่ายบัญชี

### ผู้ตรวจหรือผู้อนุมัติ

1. เปิด `Expense Sheet`
2. ตรวจข้อมูลตามรอบอนุมัติ
3. ถ้าข้อมูลครบ ให้ดำเนินการอนุมัติตามขั้น
4. ถ้าข้อมูลไม่ถูกต้อง ให้กดตีกลับและระบุเหตุผล

### Accounting Reviewer

1. เปิด `Expense` หรือ `Expense Sheet`
2. ตรวจว่า `Expense Category` ตรงกับ `product` จริง
3. ตรวจข้อมูลบัญชีและเอกสารประกอบ
4. อนุมัติหรือส่งกลับตามผลการตรวจ

## 7. การแก้ไขเอกสารหลังถูกตีกลับ

1. เปิด `Expense Sheet` ที่ถูกตีกลับ
2. อ่านเหตุผลจากฟอร์มหรือแชตเตอร์
3. แก้ไข `Expense`, หลักฐาน หรือ `Analytic Account`
4. ส่งขออนุมัติใหม่ด้วยปุ่มของโมดูล

## 8. การปิดงานคืนเงินสด

### ฝ่ายการเงิน

1. เปิด `Expense Sheet` ที่ผ่านกระบวนการอนุมัติแล้ว
2. จ่ายเงินคืนให้พนักงาน
3. กด `Mark Cash Reimbursed`
4. ตรวจวันที่ ผู้จ่าย และข้อความในแชตเตอร์

## 9. สิ่งที่ต้องระวัง

- อย่าลบหรือเปลี่ยน `product` ของ `Expense Category` โดยไม่ประเมินผลกระทบ
- ถ้าไม่ใส่ `Analytic Account` จะส่งเอกสารไม่ได้
- ถ้าเอกสารถูกตีกลับ ต้องแก้ไขแล้วส่งใหม่
- ผู้ใช้ทั่วไปจะไม่เห็น `Expense Category` configuration

## 10. ถ้ามีปัญหา

1. ถ้าส่งเอกสารไม่ได้ ให้เช็ก `Analytic Account` ก่อน
2. ถ้า submit ไม่ผ่าน ให้เช็กว่า `Expense Category` ถูกผูก `product` แล้วหรือไม่
3. ถ้าฝ่ายบัญชีเห็น `product` ไม่ตรงหมวด ให้แก้ mapping หรือแก้รายการก่อนส่งใหม่
4. ถ้าไม่เห็นไฟล์ Excel ให้เช็กว่า `report_xlsx` ติดตั้งแล้ว

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon - Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
