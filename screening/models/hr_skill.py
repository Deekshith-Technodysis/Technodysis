# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    screening_id = fields.Many2one('hr.screening',required=False, ondelete='cascade')



class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    screening_id = fields.Many2one('hr.screening',required=False, ondelete='cascade')
