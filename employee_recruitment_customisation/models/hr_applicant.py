# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
import uuid
import base64
from werkzeug.urls import url_encode

class ExperienceLevel(models.Model):
    _name = 'hr.applicant.exp.level'

    name = fields.Char(string="Level")
    notes = fields.Text(string="Notes")

class NoticePeriod(models.Model):
    _name = 'hr.applicant.notice.period'

    name = fields.Char(string="Notice Period")
    notes = fields.Text(string="Notes")

class JobApplication(models.Model):
    _inherit = 'hr.applicant'

    @api.model
    def default_get(self,fields):
        defaults = super(JobApplication, self).default_get(fields)
        if 'access_id' in fields and not defaults.get('access_id'):
            defaults['access_id'] = uuid.uuid4().hex

        return defaults


    access_id = fields.Char('Security Token', copy=False)
    sequence = fields.Char(string="Application No", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    created_date = fields.Date(string="Date of Record Creation",required=True, readonly=True, index=True, copy=False,default=datetime.today())
    resume_no = fields.Char(string="Resume No", copy=False)

    jc_exp_level = fields.Many2one('hr.applicant.exp.level',string="JC Exp. level")


    structure_id = fields.Many2one('hr.contract',string="Contract",track_visibility='onchange')
    salary_lines = fields.One2many('salary.line','salary_id')
    basic_salary = fields.Float(string="Basic Salary",digits=(16, 2))

    # Manual entry fields
    annual_fixed_pay = fields.Float(string="Annual Fixed Pay")
    annual_variable_pay = fields.Float(string="Annual Variable Pay",digits=(16, 2))
    # not using below field
    annual_perf_bonus = fields.Float(string="Annual Performance Bonus",digits=(16, 2))
    pt_deduction = fields.Float(string="Monthly Employee PT Deduction",digits=(16, 2))

    
    #Recruitment HR details
    recruitment_hr_id = fields.Many2one('hr.employee',string="Recruiter")
    recruitment_hr_manager_id = fields.Many2one('hr.employee',string="Lead Recruiter")
    onboarding_hr_id = fields.Many2one('hr.employee',string="Onboarding HR")
    onboarding_hr_manager_id = fields.Many2one('hr.employee',string="Onboarding HR Manager")
    sourcing_manager_id = fields.Many2one('hr.employee',string="Sourcing Manager")
    hr_head_id = fields.Many2one('hr.employee',string="HR Head")
    module_lead_id = fields.Many2one('hr.employee',string="Module Lead")

    # Onboarding Details
    onboarding_date = fields.Date(string="Onboarding Date",copy=False)
    expected_joining_date = fields.Date(string="Expected Joining Date",copy=False)
    joining_date = fields.Date(string="Joining Date",copy=False)
    induction_date = fields.Date(string="Induction Date",copy=False)
    initial_discussion = fields.Date(string="Initial Discussion",copy=False)
    selection_date = fields.Date(string="Date of Selection",copy=False)
    doc_requirement = fields.Date(string="DNH Triggered date",copy=False)
    workorder_approval = fields.Date(string="WO Approval",readonly=False,copy=False)
    workorder_id = fields.Many2one('res.partner.workorder',string="Workorder Ref",readonly=True)
    dnh_submission = fields.Date(string="DNH/WO submission",copy=False)
    offer_letter_release = fields.Date(string="Annexure release",copy=False)
    offer_letter_acceptance = fields.Date(string="Annexure acceptance",copy=False)
    embarck_trigger_date = fields.Date(string="Embarck BGV Trigger",copy=False)
    ogt_clearance = fields.Date(string="OGT Clearance",copy=False)
    offline_nda_date_lou = fields.Date(string="Offline NDA and LOU",copy=False)
    offline_nda_date = fields.Date(string="Offline NDA date",copy=False)
    online_nda_date = fields.Date(string="Online NDA",copy=False)
    onboarding_remarks = fields.Text(string="Remarks",copy=False)
    employment_type = fields.Selection([
        ('contract', 'Contract'),
        ('fte', 'FTE'),
        ('trainee', 'Trainee'),
        ('intern', 'Intern')], 'Employment Type')

    # Applicant address
    relocation_needed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Relocation Needed ?',default="no")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    current_location = fields.Char(string="Current Location")
    preferred_location = fields.Char(string="Preferred Location")

    # Standard field used to rename
    user_id = fields.Many2one(
        'res.users', "Assigned To", compute='_compute_user',
        tracking=True, store=True, readonly=False)
    categ_ids = fields.Many2many('hr.applicant.category', string="Category Selection")

    
    # Recruiter
    hr = fields.Many2one('hr.employee',string="HR")

    # Field to set the visibility on screen based on stages
    stage_count_id = fields.Integer(string="Stage Sequence",related="stage_id.sequence")

    # Client details
    client_id = fields.Many2one('res.partner',string="Client Name")
    

    # Skill
    applicant_skill_ids = fields.One2many('hr.employee.skill', 'applicant_id', string="Skills")
    applicant_resume_line_ids = fields.One2many('hr.resume.line', 'applicant_id', string="Resumé lines")


    # Applicant Experience
    total_exp_year = fields.Integer(string="Total Experience(Years)")
    total_exp_month = fields.Integer(string="Total Experience")
    relevant_exp_year = fields.Integer(string="Relevant Experience(Years)")
    relevant_exp_month = fields.Integer(string="Relevant Experience")

    certificate = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Highest Education', default='other', groups="hr.group_hr_user", tracking=True)
    study_field = fields.Many2one('hr.recruitment.degree',"Field of Study", groups="hr.group_hr_user", tracking=True,required=True)
    type_id = fields.Many2one('hr.recruitment.degree',"Degree", groups="hr.group_hr_user", tracking=True,related="study_field")
    study_school = fields.Char("School", groups="hr.group_hr_user", tracking=True)

    # Work details
    currently_employed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Currently Employed ?',default="no")
    nature_of_role = fields.Selection([
        ('contract', 'Contract'),
        ('permanent', 'Permanent')], 'Nature of Role')
    employer_name = fields.Char(string="Name of the Employer")
    notice_period_id = fields.Many2one('hr.applicant.notice.period',string="Notice Period")
    last_working_day = fields.Date(string="Last Working Day")
    other_offers = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),('pipeline','Pipeline')], 'Other Offers ?',default="no")
    salary_hike = fields.Date(string="Date of Last Salary Hike")
    hike_percent = fields.Float(string="Percentage of Hike")
    last_salary = fields.Float(string="Latest Monthly Salary (Rs)",compute="update_last_monthly_salary")
    last_variable_payout = fields.Float(string="Variable Payout (Rs)")
    overall_ctc = fields.Float(string="Current CTC (Rs)")
    remarks = fields.Text(string="Remarks")
    # new fields added
    current_or_last_company = fields.Char(string="Current/Last Company",required=True)
    sourcing_date = fields.Date(string="Sourcing Date",required=True)

    # Business Information
    lead_contact_id = fields.Many2one('res.partner',string="Spoc Contact Name")
    lead_contact_email = fields.Char(string="Email",related="lead_contact_id.email")
    lead_contact_number = fields.Char(string="Contact Number",related="lead_contact_id.mobile")
    talent_contact_id = fields.Many2one('res.partner',string="TA Contact Name")
    talent_contact_email = fields.Char(string="Email",related="talent_contact_id.email")
    talent_contact_number = fields.Char(string="Contact Number",related="talent_contact_id.mobile")
    job_code = fields.Char(string="Job Code")
    contact_account = fields.Char(string="Account")
    business_unit = fields.Char(string="Business Unit")

    # TAF Status
    is_taf_status = fields.Boolean(string='Enable TAF Status', default=False,
        help="Check if the TAF Status has to be enabled",related="client_id.is_taf_status",store=True)
    taf_status = fields.Selection([
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('not_initiated', 'Not Initiated'),
        ('not_applicable', 'Not Applicable')], 'TAF Status')

    # Fields to employee master
    alternate_phone = fields.Char(string="Alternate No",copy=False)

    # Passport details
    passport_id = fields.Char(string="Passport No",copy=False)
    passport_name = fields.Char(string="Name in the passport",copy=False)
    passport_issue_date = fields.Date(string="Issue Date",copy=False)
    passport_expiry_date = fields.Date(string="Expiry Date",copy=False)
    passport_issue_country = fields.Many2one('res.country',string="Issuing Country",copy=False)
    identification_id = fields.Char(string='Adhaar No.', groups="hr.group_hr_user",copy=False)
    pan_no = fields.Char(string="PAN No",copy=False)

    # Nationality
    # nationality_id = fields.Many2one('res.country',string="Nationality")

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('transender', 'Transgender'),
        ('dont_disclose','Dont want to disclose')
    ], groups="hr.group_hr_user")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced'),
        ('dont_disclose','Dont want to disclose')
    ], string='Marital Status', groups="hr.group_hr_user", default='single')
    birthday = fields.Date('Date of Birth', groups="hr.group_hr_user", tracking=True)
    father_name = fields.Char(string="Father's Name")


    # Booleans to check for the flow
    salary_updated = fields.Boolean(string="Salary computation done",copy=False)
    offer_letter_type = fields.Selection([
        ('client', 'Client Employee'),
        ('internal', 'Internal Employee')
    ], string='Offer letter Type',required=True, groups="hr.group_hr_user")


    # Onboarding Status
    dnh_status = fields.Selection([
        ('submitted', 'Submitted'),
        ('pending', 'Pending for Submission'),('cleared','Cleared'),
        ('failed','Failed'),('in_progress','In Progress'),
        ('not_applicable','Not Applicable')], 'DNH Status',required=True,copy=False)
    bgv_status = fields.Selection([
        ('triggered', 'Triggered'),
        ('pending', 'Pending to Trigger'),
        ('not_applicable','Not Applicable')], 'Embark Status',copy=False)
    ogt_status = fields.Selection([
        ('cleared', 'Cleared'),
        ('in_progress','In Progress'),
        ('not_cleared', 'Not cleared'),
        ('not_applicable','Not Applicable')], 'OGT Status',copy=False)
    offline_nda_status = fields.Selection([
        ('submitted', 'Submitted'),
        ('pending','Pending for Submission'),
        ('not_initiated', 'Not Initiated'),
        ('not_applicable','Not Applicable')], 'Offline NDA and LOU Status',copy=False)
    online_nda_status = fields.Selection([
        ('submitted', 'Submitted'),
        ('pending','Pending for Submission'),
        ('not_initiated', 'Not Initiated'),
        ('not_applicable','Not Applicable')], 'Online NDA Status',copy=False)
    jc_status = fields.Selection([
        ('available', 'JC Available'),
        ('not_available','JC Not Available'),
        ('not_applicable','Not Applicable')], 'JC Status',copy=False,required=True)
    wo_status = fields.Selection([
        ('approved', 'Approved'),
        ('in_progress','Approval in Progress'),
        ('not_initiated', 'Not Initiated'),
        ('not_applicable','FTE-Not Applicable'),('non_wipro','Non Wipro-Not Applicable')], 'WO Status',copy=False)
    offer_status = fields.Selection([
        ('offered', 'Offered'),
        ('in_progress','Offer in Progress'),
        ('accepted', 'Offer Accepted'),
        ('declined', 'Offer Declined'),
        ('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Offer Status',copy=False,required=True)
    joining_status = fields.Selection([
        ('joined', 'Joined'),
        ('pending','Pending Joiner'),
        ('dropped', 'Dropped Out'),('op_dropped', 'Opportunity Dropped Out'),
        ('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Joining Status',copy=False,required=True)
    employee_status = fields.Selection([
        ('active', 'Active'),
        ('resigned','Resigned'),
        ('terminated', 'Terminated'),('inactive', 'Not Active'),
        ('bgv_issue', 'BGV Issue'),('perf_issue', 'Performance Issue'),('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Employee Status',copy=False)

    joining_bonus_delivered_by = fields.Selection([('client','Client End'),('technodysis','Technodysis End')],string="Joining Bonus Delivered By")
    joining_bonus_amount = fields.Float(string="Joining Bonus Amount")
    add_bonus_for_salary = fields.Boolean(string="Add to Salary annexure",default=False)

    hourly_salary_bool = fields.Boolean(string="Hourly salary calculation",default=False)

    amount_per_hour = fields.Float(string="Amount per hour")
    no_of_hours = fields.Float(string="Number of hours")
    total_amount = fields.Float(string="Total Amount",store=True,compute="fetch_total_amount")
    offer_letter_sent = fields.Boolean(string="Offer Letter sent",default=False)

    @api.depends('amount_per_hour','no_of_hours','hourly_salary_bool')
    def fetch_total_amount(self):
        for line in self:
            if line.hourly_salary_bool == True:
                line.total_amount = line.amount_per_hour * line.no_of_hours
            else:
                line.total_amount = 0

    salary_proposed = fields.Float(string="Salary Proposed",compute="salary_proposed_cal")
    salary_expected = fields.Float(string="Expected Salary while Souring")


    # def action_application_send(self):
    #   if self.offer_letter_type == 'internal':
    #       raise ValidationError(_("Template not designed for Internal Company"))
    #   else:
    #       template_id = self.env.ref('employee_recruitment_customisation.mail_template_application').id

    #       template=self.env['mail.template'].browse(template_id)
    #   if template:
    #       email_values = {'email_to': self.email_from,
    #                      'email_from': self.hr.work_email,
    #                      }

    #       template.send_mail(self.id, email_values=email_values,force_send=True)
    # above function removed , since we are using the existing offer letter send option

    @api.onchange('annual_fixed_pay','annual_variable_pay')
    def salary_proposed_cal(self):
        for line in self:
            if line.annual_fixed_pay or line.annual_variable_pay:
                line.salary_proposed = line.annual_fixed_pay + line.annual_variable_pay
            else:
                line.salary_proposed = False

    @api.onchange('joining_date')
    def update_onboarding_date(self):
        for line in self:
            if line.joining_date:
                line.onboarding_date = line.joining_date
                line.induction_date = line.joining_date
            else:
                line.onboarding_date = False
                line.induction_date = False
    
    @api.depends('overall_ctc')
    def update_last_monthly_salary(self):
        for line in self:
            if line.overall_ctc:
                line.last_salary = line.overall_ctc / 12
            else:
                line.last_salary = 0


    @api.constrains('joining_status')
    def _check_joining_status(self):
        for line in self:
            if not line.dnh_status:
                raise ValidationError("Kindly Update DNH Status")
            if not line.wo_status:
                raise ValidationError("Kindly Update WO Status")
            if not line.jc_status:
                raise ValidationError("Kindly Update JC Status")
            if not line.offer_status:
                raise ValidationError("Kindly Update Offer Status")
            if not line.bgv_status:
                raise ValidationError("Kindly Update Embark Status")

    @api.constrains('joining_date')
    def _check_joining_date(self):
        for line in self:
            if not line.dnh_status:
                raise ValidationError("Kindly Update DNH Status")
            if not line.wo_status:
                raise ValidationError("Kindly Update WO Status")
            if not line.jc_status:
                raise ValidationError("Kindly Update JC Status")
            if not line.offer_status:
                raise ValidationError("Kindly Update Offer Status")
            if not line.joining_status:
                raise ValidationError("Kindly Update Joining Status")
            if not line.bgv_status:
                raise ValidationError("Kindly Update Embark Status")


    

    def name_get(self):
        result = []
        for application in self:
            name = application.sequence + ' ' + application.name
            result.append((application.id, name))
        return result


    @api.onchange('annual_fixed_pay','annual_variable_pay','pt_deduction')
    def enable_salary_computation(self):
        if not self.annual_fixed_pay or not self.annual_variable_pay or not self.pt_deduction:
            self.salary_updated = False


    def offer_accepted(self):
        stage_id = self.env['hr.recruitment.stage'].search([('sequence','=',4)])
        if stage_id:
            date = fields.Date.today()
            self.update({'stage_id':stage_id,'offer_letter_acceptance':date})

    def revise_offer(self):
        stage_id = self.env['hr.recruitment.stage'].search([('sequence','=',1)])
        if stage_id:
            self.update({'stage_id':stage_id,
                'salary_updated':False,'offer_letter_release':False,'offer_letter_sent':False,'offer_letter_acceptance':False})

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.applicant') or _('New')
        result = super(JobApplication, self).create(vals)
        return result

    @api.onchange('user_id')
    def onchange_recruiter(self):
        for line in self:
            emp_id = self.env['hr.employee'].search([('user_id','=',line.user_id.id)])
            if emp_id:
                line.hr = emp_id.id


    def print_offer_letter(self):
        if self.offer_letter_type == 'internal':
            raise ValidationError(_("Template not designed for Internal Company"))
        else:
            template_id = self.env.ref('employee_recruitment_customisation.offer_letter_mail_template_id').id

            template=self.env['mail.template'].browse(template_id)
            report = self.env.ref('employee_recruitment_customisation.action_report_offer_doc', False)
            pdf_content, content_type = report.sudo()._render_qweb_pdf(self.id)
            attachment = self.env['ir.attachment'].sudo().create({
                'name': self.partner_name+ "- Offer Letter" ,
                'type': 'binary',
                'datas': base64.encodebytes(pdf_content),
                'res_model': self._name,
                'res_id': self.id
                })
        if template:
            email_values = {'email_to': self.email_from,
                           'email_from': self.hr.work_email,
                           'attachment_ids': attachment,
                           }

            template.send_mail(self.id, email_values=email_values,force_send=True)
            stage_id = self.env['hr.recruitment.stage'].search([('sequence','=',3)])
            if stage_id:
                date = fields.Date.today()
                self.update({'offer_letter_release':date,'offer_letter_sent':True})

    def print_salary_annexure(self):
        template_id = self.env.ref('employee_recruitment_customisation.salary_annexure_mail_template_id').id

        template=self.env['mail.template'].browse(template_id)
        report = self.env.ref('employee_recruitment_customisation.action_salary_annexure', False)
        pdf_content, content_type = report.sudo()._render_qweb_pdf(self.id)
        attachment = self.env['ir.attachment'].sudo().create({
            'name': self.partner_name+ "- Annexure 1" ,
            'type': 'binary',
            'datas': base64.encodebytes(pdf_content),
            'res_model': self._name,
            'res_id': self.id
            })
        if template:
            email_values = {'email_to': self.email_from,
                           'email_from': self.hr.work_email,
                           'attachment_ids': attachment,
                           }

            template.send_mail(self.id, email_values=email_values,force_send=True)
            stage_id = self.env['hr.recruitment.stage'].search([('sequence','=',3)])
            if stage_id:
                date = fields.Date.today()
                self.update({'stage_id':stage_id,'offer_letter_release':date})




    url = fields.Char('Simulation link', compute='_compute_url')

    @api.depends(lambda self: [key for key in self._fields.keys()])
    def _compute_url(self):
        for wizard in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/offerletter/%s?' % (wizard.id)
            params = {}
            for trigger in self._get_url_triggers():
                if wizard[trigger]:
                    params[trigger] = wizard[trigger].id if isinstance(wizard[trigger], models.BaseModel) else wizard[trigger]
            
            params['token'] = wizard.access_id
            if params:
                url = url + url_encode(params)
            wizard.url = url

    def _get_url_triggers(self):
        return ['id']


    #Fuction not used 
    def save_attachment(self):
        pdf = self.env.ref('employee_recruitment_customisation.action_report_offer_doc')._render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        # save pdf as attachment
        return self.env['ir.attachment'].create({
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })


    def confirm_salary(self):
        stage_id = self.env['hr.recruitment.stage'].search([('sequence','=',2)])
        if stage_id:
            for line in self:
                line.update({'stage_id':stage_id.id})

    def compute_salary(self):
        for line in self:
            basic_salary = hra_amount = esi = esi_cal = 0
            provident_fund = provident_fund_emp = gratuity = special_allowance = leave_travel_allowance =0
            if not line.annual_fixed_pay:
                raise ValidationError(_("Kindly update the Annual fixed salary for this candidate to generate the salary structure"))
            else:
                line.salary_lines.unlink()

                #GROSS Calculation
                # if line.gross_salary:
                #   gross_amount = line.gross_salary
                if line.annual_fixed_pay >= 350000:
                    basic_salary = round((line.annual_fixed_pay*40)/100)
                    line.basic_salary = basic_salary
                    hra_amount = round(basic_salary*50/100)
                    leave_travel_allowance = round(basic_salary*20/100)
                    provident_fund = 1950*12
                    gratuity = (basic_salary*4.81/100)
                    esi_cal = line.annual_fixed_pay + line.annual_variable_pay - (provident_fund+gratuity)
                    if esi_cal <= 252000:
                        esi = (line.annual_fixed_pay + line.annual_variable_pay - (provident_fund+gratuity))*3.25/100
                    else:
                        esi = 0
                    special_allowance = (line.annual_fixed_pay - (basic_salary + hra_amount + leave_travel_allowance) - (provident_fund + gratuity))
                else:
                    basic_salary = 180000
                    line.basic_salary = basic_salary
                    provident_fund = (basic_salary*13)/100
                    gratuity = (basic_salary*4.81/100)
                    esi_cal = line.annual_fixed_pay - (provident_fund+gratuity)
                    if esi_cal <= 252000:
                        esi = (line.annual_fixed_pay - (provident_fund+gratuity))*3.25/100
                    else:
                        esi = 0
                    special_allowance = line.annual_fixed_pay - basic_salary-provident_fund-gratuity-esi

    
                # Basic Calculation
                salary_lines_basic = self.env['salary.line'].create({
                    'name':'Basic',
                    'annual_salary':round(basic_salary),
                    'salary_id':self.id,
                    'salary_type':'statutory',
                    })
                #HRA Calculation
                if hra_amount > 0:
                    salary_lines_hra = self.env['salary.line'].create({
                        'name':'HRA',
                        'annual_salary':round(hra_amount),
                        'salary_id':self.id,
                        'salary_type':'statutory',
                        })
                # Leave Travel allowance
                if leave_travel_allowance > 0:
                    salary_lines_leave = self.env['salary.line'].create({
                        'name':'Leave Travel Allowance',
                        'annual_salary':round(leave_travel_allowance),
                        'salary_id':self.id,
                        'salary_type':'statutory',
                        })
                # Special allowance
                salary_lines_sa = self.env['salary.line'].create({
                    'name':'Special Allowance',
                    'annual_salary':round(special_allowance),
                    'salary_id':self.id,
                    'salary_type':'statutory',
                    })
                # PF
                # salary_lines_pf_emp = self.env['salary.line'].create({
                #     'name':'PF – Employee Contribution',
                #     'annual_salary':round(provident_fund_emp),
                #     'salary_id':self.id,
                #     'salary_type':'statutory',
                #     })
                salary_lines_pf = self.env['salary.line'].create({
                    'name':'PF – Employer Contribution',
                    'annual_salary':round(provident_fund),
                    'salary_id':self.id,
                    'salary_type':'deduction',
                    })
                salary_lines_pt = self.env['salary.line'].create({
                    'name':'Employee PT Deduction',
                    'annual_salary':round(line.pt_deduction*12),
                    'salary_id':self.id,
                    'salary_type':'deduction',
                    })
                # Gratuity
                salary_lines_gratuity = self.env['salary.line'].create({
                    'name':'Gratuity',
                    'annual_salary':round(gratuity),
                    'salary_id':self.id,
                    'salary_type':'deduction',
                    })
                # ESI
                salary_lines_esi = self.env['salary.line'].create({
                    'name':'ESI',
                    'annual_salary':round(esi),
                    'salary_id':self.id,
                    'salary_type':'deduction',
                    })
                
                
            self.update({'salary_updated':True})

    # ---rewritten the standard function----
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                            and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.department_id and applicant.department_id.company_id
                            and applicant.department_id.company_id.email or False,
                    'default_work_phone': applicant.department_id.company_id.phone,
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                    'default_current_street':applicant.street,
                    'default_current_street2':applicant.street2,
                    'default_current_city':applicant.city,
                    'default_current_state_id':applicant.state_id.id,
                    'default_current_zip':applicant.zip,
                    'default_current_country_id':applicant.country_id.id,
                    'default_total_exp_year':applicant.total_exp_year,
                    'default_total_exp_month':applicant.total_exp_month,
                    'default_relevant_exp_year':applicant.relevant_exp_year,
                    'default_relevant_exp_month':applicant.relevant_exp_month,
                    'default_salary_expected':applicant.salary_expected,
                    'default_passport_name':applicant.passport_name,
                    'default_passport_id':applicant.passport_id,
                    'default_passport_issue_date':applicant.passport_issue_date,
                    'default_passport_expiry_date':applicant.passport_expiry_date,
                    'default_passport_issue_country':applicant.passport_issue_country.id,
                    'default_identification_id':applicant.identification_id,
                    # 'default_country_id':applicant.nationality_id.id,
                    'default_gender':applicant.gender,
                    'default_marital':applicant.marital,
                    'default_alternate_phone':applicant.alternate_phone,
                    'default_pan_no':applicant.pan_no,
                    'default_resume_line_ids':[(6, 0, [resume.id for resume in applicant.applicant_resume_line_ids])],
                    'default_employee_skill_ids':[(6, 0, [skill.id for skill in applicant.applicant_skill_ids])],
                    'default_certificate': applicant.certificate,
                    'default_study_field': applicant.study_field.name,
                    'default_study_school': applicant.study_school,
                    'default_father_name':applicant.father_name,
                    'default_birthday':applicant.birthday,
                    'default_joining_date':applicant.joining_date,
                    # applicant.applicant_resume_line_ids 
                    # 'search_result': [(6, 0, [sr.id for sr in call.search_result])]
                    # 'default_private_email':applicant.email_from
                    }
                    
        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window

    def reset_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage = dict()
        for job_id in self.mapped('job_id'):
            default_stage[job_id.id] = self.env['hr.recruitment.stage'].search(
                ['|',
                    ('job_ids', '=', False),
                    ('job_ids', '=', job_id.id),
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).id
        for applicant in self:
            applicant.write(
                {'stage_id': applicant.job_id.id and default_stage[applicant.job_id.id],
                 'refuse_reason_id': False,'salary_updated':False,'offer_letter_release':False,'offer_letter_sent':False,'offer_letter_acceptance':False})


            

class Salaryline(models.Model):
    _name = 'salary.line'

    salary_id = fields.Many2one('hr.applicant')
    name = fields.Char(string="Name")
    salary = fields.Float(string="Amount",digits=(16, 2),compute="compute_monthly_salary")
    annual_salary = fields.Float(string="Annual Amount",digits=(16, 2))
    salary_type = fields.Selection([('statutory','Statutory Benefits'),('deduction','Deduction'),('extra','Extra'),('gross','Gross'),('net','Net')],string="Type")

    @api.depends('annual_salary')
    def compute_monthly_salary(self):
        for line in self:
            line.salary = round(line.annual_salary / 12)

