# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import uuid
import base64
from werkzeug.urls import url_encode


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	is_module_lead = fields.Boolean(string="Is Module Lead ?")
	registration_number = fields.Char('Registration Number of the Employee', groups="hr.group_hr_user", copy=False)