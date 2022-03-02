# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, models
from odoo.exceptions import CacheMiss

_logger = logging.getLogger(__name__)


class WorkorderXlsx(models.AbstractModel):
	_name = "report.employee_recruitment_customisation.partner_wo_xlsx"
	_description = "Workorder XLSX Report"
	_inherit = "report.report_xlsx.abstract"

	def fetch_workorder_lines(self, lines, sheet, row, level,workbook):
		i, j = row, level
		j += 1
		date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
		floating_point = workbook.add_format({'num_format': '#,##0.00', 'border': 1})

		sheet.write(i, 0, lines.job_code or "")
		sheet.write(i, 1, lines.contact_account or "")
		sheet.write(i, 2, lines.business_unit or "")
		sheet.write(i, 3, lines.jc_exp_level.name or "")
		sheet.write(i, 4, str(lines.mark_up_percent)+' %' or "")
		sheet.write(i, 5, lines.vendor_id.name or "")
		sheet.write(i, 6, lines.candidate_name or "")
		sheet.write(i, 7, lines.resume_number or "")
		sheet.write(i, 8, lines.skill or "")
		sheet.write(i, 9, lines.study_field.name or "")
		sheet.write(i, 10, str(lines.total_exp_year) +'.'+ str(lines.total_exp_month)+' yrs'  or "")
		sheet.write(i, 11, lines.relocation_needed or "")
		sheet.write(i, 12, lines.currently_employed or "")
		sheet.write(i, 13, lines.employer_name or "")
		# sheet.write(i, 14, str(lines.hike_percent)+'% on '+ str(lines.salary_hike) or "")
		sheet.write(i, 14, " ")
		sheet.write(i, 15, lines.last_salary or "")
		sheet.write(i, 16, lines.salary_expected_monthly or "")
		sheet.write(i, 17, lines.current_hike_percent  or "")
		# sheet.write(i, 18, lines.monthly_wo_rate or "")
		sheet.write(i, 18, lines.monthly_work_bill_rate or "",floating_point)
		sheet.write(i, 19, lines.expected_joining_date or "",date_format)
		sheet.write(i, 20, lines.remarks or "")

		
		i += 1
		j -= 1
		return i

	def generate_xlsx_report(self, workbook, data, objects):
		workbook.set_properties(
			{"comments": "Created with Python and XlsxWriter from Odoo 13.0"}
		)

		sheet = workbook.add_worksheet(_("Workorder"))
		sheet.set_landscape()
		sheet.fit_to_pages(1, 0)
		sheet.set_zoom(80)
		sheet.set_column(0, 0, 20)
		sheet.set_column(0, 1, 30)
		sheet.set_column(0, 2, 20)
		sheet.set_column(0, 3, 30)
		sheet.set_column(0, 4, 30)
		sheet.set_column(0, 5, 20)
		sheet.set_column(0, 6, 20)
		sheet.set_column(0, 7, 30)
		sheet.set_column(0, 8, 30)
		sheet.set_column(0, 9, 20)
		sheet.set_column(0, 10, 20)
		sheet.set_column(0, 11, 30)
		sheet.set_column(0, 12, 30)
		sheet.set_column(0, 13, 35)
		sheet.set_column(0, 14, 20)
		sheet.set_column(0, 15, 30)
		sheet.set_column(0, 16, 40)
		sheet.set_column(0, 17, 20)
		sheet.set_column(0, 18, 20)
		sheet.set_column(0, 19, 30)
		sheet.set_column(0, 20, 30)
		# sheet.set_column(0, 21, 30)
		
		bold = workbook.add_format({"bold": True})
		right = workbook.add_format({"align": 'right',"bold": True})
		right_no_bold = workbook.add_format({"align": 'right'})
		left = workbook.add_format({"align": 'left'})
		center = workbook.add_format({"align": "center"})
		title_style = workbook.add_format(
			{"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
		)
		title_head_style = workbook.add_format(
			{"bold": True, "bg_color": "#ccccff", "bottom": 1,"align":"center",'font_size': 13}
		)
		head_style = workbook.add_format(
			{"bold": True, "align":"left",'font_size': 13}
		)
		sheet_title = [
			_("Job code"),
			_("Account"),
			_("BU/SL"),
			_("JC Exp. level"),
			_("Mark-up %"),
			_("Vendor name"),
			_("Candidate Name"),
			_("Resume number"),
			_("Skill"),
			_("Full Time Qualification"),
			_("Candidate Total Experience"),
			_("Relocation candidate  (Yes/No)"),
			_("Currently employed (Yes/No)"),
			_("Current Employer Name & (Contract/ Permanent)"),
			_("Last Hike Offered & when"),
			_("Last/ current Monthly drawn"),
			_("Expected Monthly CTC by Candidate"),
			_("Current % Hike offered"),
			# _("Monthly WO rate"),
			_("Monthly Billing rate"),
			_("Expected Joining Date"),
			_("Remarks"),
			
		]

		k = 1

		sheet.write_row(k, 0, sheet_title, title_style)
		k = k+1
		sheet.freeze_panes(k, 0)
		i = k - 1
		for o in objects:
			i += 1
			j = 0

			for lines in o.workorder_lines:
				i = self.fetch_workorder_lines(lines, sheet, i, j,workbook)
					

			