# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime

import base64


class Category(models.Model):
	_inherit = 'hr.applicant.category'

	name = fields.Char("Category Name", required=True)