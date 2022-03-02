# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    applicant_id = fields.Many2one('hr.applicant',required=False, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')
    display_skill = fields.Boolean(string="Display skill in Workorder")
    n_skill = fields.Char(string="N-1 Skill")


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')
    applicant_id = fields.Many2one('hr.applicant', required=False, ondelete='cascade')

    latest_experience = fields.Boolean(string="This is the latest Experience")
    latest_experience_check = fields.Boolean(string="Check for Latest Experience")

    # latest_qualification = fields.Boolean(string="This is the Highest Qualification")
    # latest_qualification_check = fields.Boolean(string="Check for Highest Qualification")

    @api.onchange('line_type_id')
    def display_latest_experience_bool(self):
    	for line in self:
    		if line.line_type_id.name == "Experience":
    			line.latest_experience_check = True
    		else:
    			line.latest_experience_check = False

    # @api.onchange('line_type_id')
    # def display_latest_education_bool(self):
    #     for line in self:
    #         if line.line_type_id.name == "Education":
    #             line.latest_qualification_check = True
    #         else:
    #             line.latest_qualification_check = False