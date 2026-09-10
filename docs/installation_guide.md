# คู่มือติดตั้ง

## ก่อนติดตั้ง

ให้เตรียมสิ่งนี้ก่อน:

1. Odoo 15
2. path ของโมดูลคือ `/var/odoo/custom15_autoinfo`
3. dependency ให้ครบ:
   - `hr_expense`
   - `mail`
   - `analytic`
   - `report_xlsx`
   - `base_tier_validation`
   - `dtr_expense_tier_validation`

## วิธีติดตั้งหรืออัปเดต

1. วางโฟลเดอร์โมดูลไว้ที่
   `/var/odoo/custom15_autoinfo/autoinfo_hr_expense_cash_tracking`
2. หยุด Odoo service
3. รันคำสั่งอัปเกรดแบบปลอดภัย
4. เปิด Odoo service

ตัวอย่างคำสั่ง:

```bash
sudo systemctl stop odoo15
cd /var/odoo/odoo15
./odoo-bin -c /etc/odoo.conf -d <database_name> -u autoinfo_hr_expense_cash_tracking --stop-after-init
sudo systemctl start odoo15
```

## หลังติดตั้ง

1. ตั้งกลุ่มสิทธิ์ของผู้ตรวจ
2. ตั้งกลุ่มสิทธิ์ของผู้จ่ายเงิน
3. ตรวจ `Tier Definition`
4. เปิดหน้า `Expense Sheet`
5. ดูว่ามีส่วน `Cash Reimbursement`
6. ลอง export `Detail XLSX`
7. ลอง export `Summary XLSX`
