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
    job_type_id = fields.Many2one('hr.job.type',string="Employment Type",required=True)
    enable_direct_invoice_creation = fields.Boolean(string="Enable Direct invoice creation",related="job_type_id.enable_direct_invoice_creation")

    fte_lumen_invoice = fields.Boolean(string="Check if this is a Lumen FTE Invoice")

    

    def unlink(self):
        for move in self:
            if move.posted_before and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted once."))
            if move.hr_employee_id:
                raise UserError(_("Since this invoice belogns to the employee who is onboarded to client, You cannot delete this entry"))
        self.line_ids.unlink()
        return super(AccountMove, self).unlink()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    pay_element = fields.Float(string="Pay Element")
    vendor_margin = fields.Float(string="Vendor Margin")


    @api.onchange('vendor_margin')
    def _fetch_unit_price_on_vendor_margin(self):
        unit_price = 0
        for line in self:
            if line.move_id.fte_lumen_invoice == True:
                unit_price = (line.pay_element * line.vendor_margin)/100
                line.unit_price = unit_price
