# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    sourcing_id = fields.Many2one('hr.sourcing',required=False, ondelete='cascade')



class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    sourcing_id = fields.Many2one('hr.sourcing',required=False, ondelete='cascade')
