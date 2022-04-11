# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import uuid
import base64
from werkzeug.urls import url_encode

class AccountMove(models.Model):
    _inherit = 'account.move'

    application_id = fields.Many2one('hr.applicant',string="Application Id")
    hr_employee_id = fields.Many2one('hr.employee',string="Employee Id")



    def unlink(self):
        for move in self:
            if move.posted_before and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted once."))
            if move.hr_employee_id:
                raise UserError(_("Since this invoice belogns to the employee who is onboarded to client, You cannot delete this entry"))
        self.line_ids.unlink()
        return super(AccountMove, self).unlink()