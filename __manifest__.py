# -*- coding: utf-8 -*-
{
    'name': 'Recruitment Request',
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'category': 'Employees',
    'description': "Request for new employee recruitment.This module allow department managers to request for new employee recruitment",
    'summary': 'Recruitment Request app, Recruitment Request Odoo Apps, SunCart Recruitment Request Odoo Apps, Recruitment Request Odoo Apps in India, Customer Experience Management Odoo Apps, Solicitud de Reclutamiento, Aplicación de solicitud de contratación, Aplicaciones Odoo de solicitud de contratación, Aplicaciones Odoo de solicitud de contratación SunCart, Aplicaciones Odoo de solicitud de contratación en India, Aplicaciones Odoo de gestión de la experiencia del cliente',
    # 'price': 49,
    'price':44,
    'sequence': 1,
    'currency': 'USD',
    'author': "SunArc Technologies",
    'website': 'https://www.suncartstore.com/odoo-apps/recruitment-request',
    'depends': ['base', 'hr_recruitment', 'mail'],
    'images': ['static/description/Banner.png'],
    'data': [
        'data/request_email.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/start_recruiting.xml',
        'wizard/submit_manager.xml',
        'wizard/submit_dpthead.xml',
        'views/request.xml',
        'views/employee.xml',
        'views/applicant.xml',
    ],
    'assets':{
    'web.assets_backend': [
    'recruitment_requests/static/css/req_page.css',
    ],
    },
    'installable': True,
    'active': False,
    'application': True
}
