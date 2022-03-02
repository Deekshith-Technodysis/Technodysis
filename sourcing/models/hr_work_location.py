# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrWorkLocations(models.Model):
    _name = 'hr.work.location'

    name = fields.Char(string='Location')

class HrWorkOtherLocations(models.Model):
    _name = 'hr.work.other.location'

    name = fields.Char(string='Name')