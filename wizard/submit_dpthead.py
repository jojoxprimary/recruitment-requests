# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class SubmitDptHeadProcess(models.TransientModel):
    _name = 'submit.dpthead.process'
    _description = 'Submit Department Head Process'
    recruitment_id = fields.Many2one(
            'hr.recruitment.request',
            default=lambda self: self._default_recruitment(),
            required=True
        )

    responsible_dpthead = fields.Many2many('res.users','recruitment_dpthead_rel', 'recruitment_id', 'user_id', string='Manager', required=True)

    def _default_recruitment(self):
        return self.env['hr.recruitment.request'].browse(self.env.context.get(
            'active_id'))

    @api.onchange('recruitment_id')
    def get_manager_name_list(self):
        manager_dict = {}
        # NOTE JOJO: Update groups here to include users outside hr_recruitment module
        manager = self.env.ref('hr_recruitment.group_hr_recruitment_manager').users
        manager_dict['domain'] = {'responsible_manager': [('id', 'in', manager.ids)]}
        return manager_dict
    
    def submit_dpthead(self):

        selected_dpthead = self.responsible_dpthead[0] if self.responsible_dpthead else False
        # NOTE JOJO: Temporary remove emailing
        # submit_template = self.env.ref('recruitment_requests.submit_request_email_template')
        # if submit_template:
        #     for manager in self.responsible_manager:
        #         submit_template.sudo().write({'email_to': manager.login})
        #         self.env['mail.template'].sudo().browse(submit_template.id).send_mail(self.recruitment_id.id,force_send=True)
        # submit_user_template = self.env.ref('recruitment_requests.submit_request_user_email_template')
        # if submit_user_template:
        #     submit_user_template.sudo().write({'email_to': self.recruitment_id.user_id.login})
        #     self.env['mail.template'].sudo().browse(submit_user_template.id).send_mail(self.recruitment_id.id,force_send=True)
        return self.recruitment_id.write({
            'state': 'dpthead_approval',
            'dpthead_id_approver': selected_dpthead.id if selected_dpthead else False,
            'dpthead_approval_date': fields.Datetime.now(),
        })
