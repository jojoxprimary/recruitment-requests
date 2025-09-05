# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class HrRecruitmentRequest(models.Model):
    _name = 'hr.recruitment.request'
    _description = "Recruitment Request"
    _rec_name = 'name'

    def _domain_department_ids(self):
        department = False
        if self.env.user in self.env.ref('hr_recruitment.group_hr_recruitment_manager').users:
            department = self.env['hr.department'].search([]).ids
        else:
            department = []
            employee_department = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            if employee_department:
             department.append(employee_department.department_id.id)
            department_object = self.env['hr.department'].search([('manager_id.user_id', '=', self.env.user.id)])
            for dept_obj in department_object:
              department.append(dept_obj.id)
        return [('id', 'in', department)]

    rr_name = fields.Char('Recruitment Ref',readonly=True)
    name = fields.Text(string="Subject", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    department_id = fields.Many2one('hr.department', string="Department", required=True, domain=_domain_department_ids)
    #department_id = fields.Many2one('hr.department', string="Department", required=True, domain=lambda self: self.get_requested_employee_department())
    job_id = fields.Many2one('hr.job', string="Requested Position")
    job_tmp = fields.Char(string="Job Title")
    employees_count = fields.Integer(string="# of employees", compute='get_employees_count')
    expected_employees = fields.Integer(string="Expected Employees", required=True, default=1)
    date_expected = fields.Date(string="Date Expected", required=True, default=datetime.now().date())
    user_id = fields.Many2one('res.users', string="Requested By", readonly=True, default=lambda self: self.env.user)
    approver_id = fields.Many2one('res.users', string="Approved By", readonly=True)
    refused_by = fields.Many2one('res.users', string="Refused By", readonly=True)
    applicants_count = fields.Integer('# of Application', compute='get_applicants_count')
    reason = fields.Text(string="Reason", required=True)
    #reason = fields.Html(string="Reason", required=True)
    #description = fields.Text(string="Job Description", required=True)
    description = fields.Html(string="Job Description", required=True)
    #requirements = fields.Text(string="Job Requirement", required=True)
    requirements = fields.Html(string="Job Requirement", required=True)

    dpthead_id_approver = fields.Many2one('res.users', string='Department Head Approver', readonly=True)
    dpthead_approval_date = fields.Datetime(string='Department Head Approval Date', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'), 
        ('dpthead_approval', 'Department Head Approval'), 
        ('refused', 'Refused'), 
        ('confirmed', 'Waiting Approval'), 
        ('accepted', 'Approved'),
        ('recruiting', 'In recruitment'), 
        ('done', 'Done')], string='State', default='draft')
    applicant_ids = fields.One2many('hr.applicant', 'request_id', string='Applicant', readonly=True)

    employee_ids = fields.One2many('hr.employee', 'request_id', string="Recruited Employees", readonly=True)
    recruited_employees = fields.Integer('Recruited Percentage', compute='get_recruited_employees_percentage')
    existing_job = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Existing Job Position', required=True)
    # submit_manager = fields.Many2many('res.users','manager_user_rel','id','user_id', string='Manager')

    @api.onchange('existing_job')
    def update_job(self):
        for res in self:
            res.job_id = False
            res.job_tmp = False

    def get_recruited_employees_percentage(self):
        for percentage in self:
            percentage.recruited_employees = (percentage.employees_count / percentage.expected_employees) * 100

    def get_applicants_count(self):
        read_group_result = self.env['hr.applicant'].read_group([('request_id', 'in', self.ids)], ['request_id'],
                                                                ['request_id'])
        result = dict((data['request_id'][0], data['request_id_count']) for data in read_group_result)
        for job in self:
            job.applicants_count = result.get(job.id, 0)

    def get_employees_count(self):
        for employee in self:
            employee.employees_count = len(employee.employee_ids.ids)
            

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            seq = self.env['ir.sequence'].next_by_code('hr.recruitment.request') or '/'
            vals['rr_name'] = seq
        return super().create(vals_list)

    @api.onchange('department_id','existing_job')
    def get_requested_position(self):
        position = {}
        if self.department_id:
            job_object = self.env['hr.job'].search([('department_id', '=', self.department_id.id)])
            if job_object:
                position['domain'] = {'job_id': [('id', 'in', job_object.ids)]}
        else:
            position['domain'] = {'job_id': [('id', 'in', [])]}
        return position

    @api.onchange('department_id')
    def update_job_id(self):
        self.job_id = False

    @api.onchange('job_id', 'department_id')
    def get_job_description(self):
        if self.job_id:
            self.description = self.job_id.description
        else:
            self.description = False

    def action_submit_to_department_head(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'submit.dpthead.process',
            'target': 'new',
            'views': [(False, 'form')],
            'context': {
                'default_recruitment_id': self.id,
            }
        }
        
        # recommended
        #         {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'submit.dpthead.process',
        #     'target': 'new',
        #     'views': [(False, 'form')],
        #     'params': {
        #         'view_type': 'form'  # ← Moved here
        #     }
        # }

    def action_submit_recruiting(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'submit.recruiting.process',
            'target': 'new',
        }

# state = fields.Selection([
#         ('draft', 'Draft'), 
#         ('dpthead_approval', 'Department Head Approval'), 
#         ('refused', 'Refused'), 
#         ('confirmed', 'Waiting Approval'), 
#         ('accepted', 'Approved'),
#         ('recruiting', 'In recruitment'), 
#         ('done', 'Done')], string='State', default='draft')
        
        

    #@api.multi
    def action_accept(self):
        if not self.job_id:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'start.recruiting.process',
                'target': 'new',
            }
        else:

            open_request = self.search(
                [('job_id', '=', self.job_id.id), ('state', 'in', ['accepted', 'recruiting']), ('id', '!=', self.id)])
            if open_request and open_request.ids:
                display_name = []
                for open_req in open_request:
                    display_name.append(open_req.rr_name)
                raise ValidationError(
                    ("Recruitment request already in process.Kindly Complete or Cancel %s request.") % (
                        '\n'.join(display_name)))
            else:
                return self.write({'state': 'accepted'})


            # job_request_object = self.env['hr.job'].search([('id', '=', self.job_id.id)])
            # return self.write({'state': 'accepted'})
            # if job_request_object.state == 'open':
            #     return self.write({'state': 'accepted'})
            # else:
            ##     raise ValidationError("An existing request for this job position already in queue")
                # raise ValidationError("Job recruitment process in progress related to respective job position.First Complete that one then start a new hiring process.")

    def action_refuse(self):
        self.update({'refused_by': self.env.user.id})
        refuse_template = self.env.ref('recruitment_requests.refuse_request_email_template')
        if refuse_template:
            print("uuu")
            refuse_template.sudo().write({'email_to': self.user_id.login})
            self.env['mail.template'].sudo().browse(refuse_template.id).send_mail(self.id,
                                                                                       force_send=True)
        self.write({
            'state': 'refused'
        })

    def action_draft(self):
        self.write({
            'state': 'draft',
        })

    def action_done(self):
        self.write({
            'state': 'done',
        })
        self.job_id.update({'no_of_recruitment':
                                0})
