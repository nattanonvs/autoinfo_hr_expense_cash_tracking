from odoo import models


class ExpenseCashDetailXlsx(models.AbstractModel):
    _name = "report.autoinfo_hr_expense_cash_tracking.expense_cash_detail_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Expense Cash Detail XLSX"
    _table = "ai_exp_cash_detail_xlsx"

    def generate_xlsx_report(self, workbook, data, sheets):
        worksheet = workbook.add_worksheet("Expense Detail")
        header_format = workbook.add_format({"bold": True, "bg_color": "#D9EAD3"})
        amount_format = workbook.add_format({"num_format": "#,##0.00"})

        headers = [
            "Document No.",
            "Employee",
            "Department",
            "Expense Date",
            "Description",
            "Analytic Account",
            "Subtotal",
            "Tax",
            "Total",
            "Cash Tracking Status",
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        worksheet.set_column("A:A", 22)
        worksheet.set_column("B:B", 24)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 14)
        worksheet.set_column("E:E", 32)
        worksheet.set_column("F:F", 24)
        worksheet.set_column("G:I", 14)
        worksheet.set_column("J:J", 22)

        row = 1
        for sheet in sheets:
            for line in sheet.expense_line_ids:
                tax_amount = line.total_amount - line.untaxed_amount
                worksheet.write(row, 0, sheet.name or "")
                worksheet.write(row, 1, sheet.employee_id.name or "")
                worksheet.write(row, 2, sheet.department_id.name or "")
                worksheet.write(row, 3, str(line.date or ""))
                worksheet.write(row, 4, line.name or "")
                worksheet.write(row, 5, line.analytic_account_id.name or "")
                worksheet.write_number(row, 6, line.untaxed_amount or 0.0, amount_format)
                worksheet.write_number(row, 7, tax_amount or 0.0, amount_format)
                worksheet.write_number(row, 8, line.total_amount or 0.0, amount_format)
                worksheet.write(row, 9, sheet.cash_tracking_state or "")
                row += 1
