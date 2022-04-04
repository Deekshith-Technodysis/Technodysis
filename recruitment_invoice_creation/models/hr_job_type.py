# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrJobType(models.Model):
    _inherit = 'hr.job.type'

    enable_direct_invoice_creation = fields.Boolean(string="Enable Direct Invoicing",default=False)