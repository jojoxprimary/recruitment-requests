# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    request_id = fields.Many2one('hr.recruitment.request', string='Enrolment Request')




