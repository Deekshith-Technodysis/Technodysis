# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
	_inherit = 'res.company'

	ceo_id = fields.Many2one('hr.employee',string="CEO")
	hsn_no = fields.Char(string="HSN/SAC")
	pan_no = fields.Char(string="PAN")
	company_seal = fields.Image('Seal', copy=False, attachment=True, max_width=256, max_height=256)
	company_seal_sign = fields.Image('Seal & Sign', copy=False, attachment=True, max_width=256, max_height=256)
	lut_no = fields.Char(string="LUT No.")