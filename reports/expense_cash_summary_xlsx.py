from odoo import models


class ExpenseCashSummaryXlsx(models.AbstractModel):
    _name = "report.autoinfo_hr_expense_cash_tracking.expense_cash_summary_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Expense Cash Summary XLSX"
    _table = "ai_exp_cash_sum_xlsx"

    def generate_xlsx_report(self, workbook, data, wizard):
        worksheet = workbook.add_worksheet("Expense Summary")
        header_format = workbook.add_format({"bold": True, "bg_color": "#D9EAD3"})
        amount_format = workbook.add_format({"num_format": "#,##0.00"})

        headers = [
            "Document No.",
            "Employee",
            "Department",
            "Current Tier",
            "Tier Validation State",
            "Cash Tracking State",
            "Cash Paid Date",
            "Cash Paid By",
            "Cash Reference",
            "Total Amount",
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        worksheet.set_column("A:A", 22)
        worksheet.set_column("B:B", 24)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:F", 22)
        worksheet.set_column("G:I", 18)
        worksheet.set_column("J:J", 14)

        row = 1
        sheets = self.env["hr.expense.sheet"].browse(data.get("sheet_ids", []))
        for sheet in sheets:
            worksheet.write(row, 0, sheet.name or "")
            worksheet.write(row, 1, sheet.employee_id.name or "")
            worksheet.write(row, 2, sheet.department_id.name or "")
            worksheet.write(row, 3, getattr(sheet, "current_tier_role", False) or "")
            worksheet.write(row, 4, "validated" if sheet.validated else "pending")
            worksheet.write(row, 5, sheet.cash_tracking_state or "")
            worksheet.write(row, 6, str(sheet.cash_paid_date or ""))
            worksheet.write(row, 7, sheet.cash_paid_by.name or "")
            worksheet.write(row, 8, sheet.cash_reference or "")
            worksheet.write_number(row, 9, sheet.total_amount or 0.0, amount_format)
            row += 1