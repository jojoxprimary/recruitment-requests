# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class SubmitRecruitingProcess(models.TransientModel):
    _name = 'submit.recruiting.process'
    _description = 'Submit Recruiting Process'
    recruitment_id = fields.Many2one(
        'hr.recruitment.request',
        default=lambda self: self._default_recruitment(),
        required=True
    )
    responsible_manager = fields.Many2many('res.users','recruitment_manager_rel', 'recruitment_id', 'user_id', string='Manager', required=True)

    def _default_recruitment(self):
        return self.env['hr.recruitment.request'].browse(self.env.context.get(
            'active_id'))

    @api.onchange('recruitment_id')
    def get_manager_name_list(self):
        manager_dict = {}
        manager = self.env.ref('hr_recruitment.group_hr_recruitment_manager').users
        manager_dict['domain'] = {'responsible_manager': [('id', 'in', manager.ids)]}
        return manager_dict

    def send_email(self):
        submit_template = self.env.ref('recruitment_requests.submit_request_email_template')
        if submit_template:
            for manager in self.responsible_manager:
                submit_template.sudo().write({'email_to': manager.login})
                self.env['mail.template'].sudo().browse(submit_template.id).send_mail(self.recruitment_id.id,force_send=True)
        submit_user_template = self.env.ref('recruitment_requests.submit_request_user_email_template')
        if submit_user_template:
            submit_user_template.sudo().write({'email_to': self.recruitment_id.user_id.login})
            self.env['mail.template'].sudo().browse(submit_user_template.id).send_mail(self.recruitment_id.id,force_send=True)
        return self.recruitment_id.write({
            'state': 'confirmed',
        })
