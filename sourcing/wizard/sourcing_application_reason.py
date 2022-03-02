# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SourcingApplicationReason(models.TransientModel):
	_name = 'sourcing.application.reason'
	_description = 'Sourcing Application'

	expected_joining_date = fields.Date(string="Expected Joining Date")
	official_np_lwd = fields.Date(string="Official NP/ LWD")
	comments = fields.Text(string="Official NP/ LWD Comments")
	change_reason = fields.Text(string="Reason for change")
	sourcing_id = fields.Many2one('hr.sourcing')

	def action_create_application(self):
		self.sourcing_id.create_sourcing_application()
		return self.sourcing_id.write({'expected_joining_date': self.expected_joining_date,'official_np_lwd':self.official_np_lwd,
			'official_np_lwd_comments':self.comments,'change_reason':self.change_reason})
