# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerBank(models.Model):
	_inherit = 'res.partner.bank'

	swift_code = fields.Char(string="Swift Code")