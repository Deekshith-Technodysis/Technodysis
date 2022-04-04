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