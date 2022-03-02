# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SourcingGetRefuseReason(models.TransientModel):
    _name = 'sourcing.get.refuse.reason'
    _description = 'Get Refuse Reason'

    refuse_reason_id = fields.Many2one('hr.sourcing.refuse.reason', 'Refuse Reason')
    sourcing_ids = fields.Many2many('hr.sourcing')

    def action_refuse_reason_apply(self):
        return self.sourcing_ids.write({'refuse_reason_id': self.refuse_reason_id.id, 'active': False})
