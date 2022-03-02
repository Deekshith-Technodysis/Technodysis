# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ReportTimesheet(models.AbstractModel):
	_name = 'report.employee_recruitment_customisation.report_offer_letter'



	@api.model
	def _get_report_values(self, docids, data=None):
		"""we are overwriting this function because we need to show values from other models in the report
		we pass the objects in the docargs dictionary"""
		if self.env.context.get('active_model') == 'hr.applicant':
			print("same model working")
		docs = self.env['hr.applicant'].browse(self.env.context.get('active_ids'))
		
		company_name = self.env['res.company'].search([('name', '=', docs.company_id.name)])
		
		return {
			'doc_ids': self.ids,
			'docs': docs,
			'company':company_name,
		}
	