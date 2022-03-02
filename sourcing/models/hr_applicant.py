# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import uuid
import base64
from werkzeug.urls import url_encode


class JobApplication(models.Model):
	_inherit = 'hr.applicant'

	origin_id = fields.Many2one('hr.sourcing',string="Source id")
	work_location_id = fields.Many2one('hr.work.location',string="Work Location")
