# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    request_id = fields.Many2one('hr.recruitment.request', string='Enrolment Request',
                                 domain=[('state', 'not in', ['draft', 'confirmed'])], required=True)


    @api.onchange('job_id')
    def get_recruitment_request(self):
        for rec in self:
            if rec.job_id:
                recruitment_object = self.env['hr.recruitment.request'].search(
                    [('job_id', '=', rec.job_id.id), ('state', 'not in', ['draft', 'confirmed'])])
                for recruitment in recruitment_object:
                        rec.request_id = recruitment.id
                if not recruitment_object:
                    rec.request_id = False
            else:
                rec.request_id = False
    def _get_employee_create_vals(self):
        employee_create = super()._get_employee_create_vals()
        employee_create.update({'request_id': self.request_id.id or False})
        return employee_create

class HrJob(models.Model):
    _inherit = 'hr.job'


