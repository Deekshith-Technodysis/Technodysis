# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrJobType(models.Model):
    _name = 'hr.job.type'

    name = fields.Char(string='Name')

    enable_bill_rate = fields.Boolean(string="Enable Bill Rate",default=False)