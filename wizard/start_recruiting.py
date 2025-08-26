# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class StartRecruitingProcess(models.TransientModel):
    _name = 'start.recruiting.process'
    _description = 'Start Recruiting Process'
    recruitment_id = fields.Many2one(
        'hr.recruitment.request',
        default=lambda self: self._default_recruitment(),
        required=True
    )

    recruitment_responsible = fields.Many2one('res.users', string='Recruitment Responsible')
    interviewer_ids = fields.Many2many('res.users', string='Interviewers', domain="[('share', '=', False)]", help="The Interviewers set on the job position can see all Applicants in it. They have access to the information, the attachments, the meeting management and they can refuse him. You don't need to have Recruitment rights to be set as an interviewer.")


    def _default_recruitment(self):
        return self.env['hr.recruitment.request'].browse(self.env.context.get(
            'active_id'))

    def action_start_recruit(self):
        approve_template = self.env.ref('recruitment_requests.approve_request_email_template')
        if self.recruitment_id.job_id:
            self.recruitment_id.job_id.write({
                'company_id': self.recruitment_responsible.company_id.id,
                'user_id': self.recruitment_responsible.id,
                'interviewer_ids':self.interviewer_ids,
                'no_of_recruitment': self.recruitment_id.expected_employees,
            })
            self.recruitment_id.write({
                'state': 'recruiting',
                'approver_id': self.env.user.id
            })
            if approve_template:
                approve_template.sudo().write({'email_to': self.recruitment_id.user_id.login})
                self.env['mail.template'].sudo().browse(approve_template.id).send_mail(self.recruitment_id.id,force_send=True)
            # return self.recruitment_id.job_id.set_recruit()
            data = ({'user_id': self.recruitment_responsible.id,
                     'no_of_recruitment': self.recruitment_id.expected_employees,
                     'interviewer_ids': self.interviewer_ids,
                     })
            return self.recruitment_id.job_id.update(data)
        else:
            new_job_id = self.env['hr.job'].create({'name': self.recruitment_id.job_tmp,
                                                    'company_id': self.recruitment_responsible.company_id.id,
                                                    'department_id': self.recruitment_id.department_id.id,
                                                    'user_id': self.recruitment_responsible.id,
                                                    'interviewer_ids': self.interviewer_ids,
                                                    'description': self.recruitment_id.description,
                                                    'no_of_recruitment': self.recruitment_id.expected_employees,
                                                    })
            if approve_template:
                approve_template.sudo().write({'email_to': self.recruitment_id.user_id.login})
                self.env['mail.template'].sudo().browse(approve_template.id).send_mail(self.recruitment_id.id,force_send=True)
            return self.recruitment_id.write({
                'job_id': new_job_id.id,
                'state': 'recruiting',
                'approver_id': self.env.user.id
            })
