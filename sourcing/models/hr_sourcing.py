# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError

class HrSourcing(models.Model):
    _name = 'hr.sourcing'
    _description = "Sourcing"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Subject / Application Name",required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    candidate_name = fields.Char(string="Applicant's Name",required=True)
    stage_id = fields.Selection([
        ('l0', 'L0 Discussion'),
        ('l1', 'L1 Discussion'),
        ('l2', 'L2 Discussion'),
        ('l3', 'L3 Discussion'),
        ('done','Done'),
        ('reject','Rejected')], 'Stages',default="l0")
    sourcing_date = fields.Date(string="Sourcing Date",required=True)
    sequence = fields.Char(string="Sequence")
    category_id = fields.Many2many('hr.applicant.category',string="Category",required=True)
    currently_employed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Currently Working ?',default="no")

    applicant_skill_ids = fields.One2many('hr.employee.skill', 'sourcing_id', string="Skills")
    applicant_resume_line_ids = fields.One2many('hr.resume.line', 'sourcing_id', string="Resumé lines")
    job_type_id = fields.Many2one('hr.job.type',string="Job Type",required=True)
    client_id = fields.Many2one('res.partner',string="Client",required=True)
    mobile = fields.Char(string="Candidate's Mobile No.",required=True)
    email = fields.Char(string="Candidate's mail id",required=True)

    total_exp_year = fields.Integer(string="Total Experience(Years)",required=True)
    total_exp_month = fields.Integer(string="Total Experience")
    relevant_exp_year = fields.Integer(string="Relevant Experience(Years)",required=True)
    relevant_exp_month = fields.Integer(string="Relevant Experience")
    hourly_salary_bool = fields.Boolean(string="Hourly salary calculation",default=False)

    amount_per_hour = fields.Float(string="Amount per hour")
    no_of_hours = fields.Float(string="Number of hours")
    total_amount = fields.Float(string="Total Amount",store=True,compute="fetch_total_amount")

    @api.depends('amount_per_hour','no_of_hours','hourly_salary_bool')
    def fetch_total_amount(self):
        for line in self:
            if line.hourly_salary_bool == True:
                line.total_amount = line.amount_per_hour * line.no_of_hours
            else:
                line.total_amount = 0



    
    notice_period_id = fields.Many2one('hr.applicant.notice.period',string="Notice Period",required=True)
    current_location = fields.Char(string="Current Location",required=True)
    preffered_location_id = fields.Many2many('hr.work.other.location','source_loc_other_id',string="Open to work in Other location")
    other_offers_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),('pipeline','Pipeline')], 'Other Offers')
    offer_price = fields.Float(string="Offer Price")
    joining_date = fields.Date(string="Tenative Joining Date")
    official_np_lwd = fields.Date(string="Official NP/ LWD")
    official_np_lwd_comments = fields.Text(string="Official NP/ LWD Comments")
    
    # Eduction and personal details
    degree_year_of_passing = fields.Char(string="Year of passing")
    university_name = fields.Char(string="University name")
    puc_passing_year = fields.Char(string="12 th Year of passing")
    puc_college_name = fields.Char(string="12th Name of the College")
    high_school_passing_year = fields.Char(string="10th Year of passing")
    school_name = fields.Char(string="Name of the school")
    work_gap_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], "Gap in work")
    education_gap_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],"Gap Education")
    father_name = fields.Char(string="Father name")
    aadhar_no = fields.Char(string="Aadhar #")
    dob = fields.Date(string="Date of birth")

    # address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")

    
    current_or_last_company = fields.Char(string="Current/Last Company",required=True)
    recruiter_id = fields.Many2one('hr.employee',string="Recruiter",required=True)
    lead_co_ordinator_id = fields.Many2one('hr.employee',string="Lead Recruiter",required=True)
    module_lead_id = fields.Many2one('hr.employee',string="Module Lead")
    ctc = fields.Float(string="CTC",required=True)
    ectc = fields.Float(string="ECTC",readonly=False)
    commission_percent = fields.Float("Commission Percent",required=True)
    training_bool = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], "Training")
    availability = fields.Datetime(string="Availability for Interview")
    change_reason = fields.Text(string="Reason for change",default="For career growth")
    selection_date = fields.Date(string="Date of selection")
    
    billing_rate = fields.Float(string="Billing Rate/Month",compute="compute_bill_rate")

    # Business Information
    lead_contact_id = fields.Many2one('res.partner',string="Spoc Contact Name")
    lead_contact_email = fields.Char(string="Spoc Email",related="lead_contact_id.email")
    lead_contact_number = fields.Char(string="Contact Number",related="lead_contact_id.mobile")
    talent_contact_id = fields.Many2one('res.partner',string="TA Contact Name")
    talent_contact_email = fields.Char(string="TA Email",related="talent_contact_id.email")
    talent_contact_number = fields.Char(string="Contact Number",related="talent_contact_id.mobile")
    jc_no = fields.Char(string="JC No.")
    contact_account = fields.Char(string="Account")
    business_unit = fields.Char(string="Business Unit",required=True)
    resume_no = fields.Char(string="Resume No", copy=False)

    l0_selected = fields.Date(string="L0 Selected",readonly=True)
    l1_selected = fields.Date(string="L1 Selected",readonly=True)
    l2_selected = fields.Date(string="L2 Selected",readonly=True)
    l3_selected = fields.Date(string="L3 Selected",readonly=True)

    enable_bill_rate = fields.Boolean(string="Enable Bill Rate",default=False,related="job_type_id.enable_bill_rate")

    application_status = fields.Selection(
            [('draft', 'Draft'),
             ('application_created', 'Application Created')], string='Application Status', readonly=True, copy=False, default='draft')

    sourcing_app_count = fields.Integer(string='Applications', compute='_application_count')

    # onboarding status
    joining_status = fields.Selection([
        ('joined', 'Joined'),
        ('pending','Pending Joiner'),
        ('dropped', 'Dropped Out'),('op_dropped', 'Opportunity Dropped Out'),
        ('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Joining Status',copy=False,required=True,default="not_applicable")
    jc_status = fields.Selection([
        ('available', 'JC Available'),
        ('not_available','JC Not Available'),
        ('not_applicable','Not Applicable')], 'JC Status',copy=False,required=True,default="not_applicable")
    offer_status = fields.Selection([
        ('offered', 'Offered'),
        ('in_progress','Offer in Progress'),
        ('accepted', 'Offer Accepted'),
        ('declined', 'Offer Declined'),
        ('aborted', 'Aborted'),
        ('not_applicable','Not Applicable')], 'Offer Status',copy=False,required=True,default="not_applicable")
    dnh_status = fields.Selection([
        ('submitted', 'Submitted'),
        ('pending', 'Pending for Submission'),('cleared','Cleared'),
        ('failed','Failed'),('in_progress','In Progress'),
        ('not_applicable','Not Applicable')], 'DNH Status',required=True,copy=False,default="not_applicable")
    wo_status = fields.Selection([
        ('approved', 'Approved'),
        ('in_progress','Approval in Progress'),
        ('not_initiated', 'Not Initiated'),
        ('not_applicable','FTE-Not Applicable')], 'WO Status',copy=False,default="not_applicable")
    bgv_status = fields.Selection([
        ('triggered', 'Triggered'),
        ('pending', 'Pending to Trigger'),
        ('not_applicable','Not Applicable')], 'BGV Status',copy=False,default="not_applicable")
    work_location_id = fields.Many2one('hr.work.location',string="Work Location")
    preferred_location = fields.Char(string="Preferred Location",required=True)
    expected_joining_date = fields.Date(string="Expected Joining Date",copy=False,required=True)
    study_field = fields.Many2one('hr.recruitment.degree',"Field of Study", tracking=True,required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('transender', 'Transgender'),
        ('dont_disclose','Dont want to disclose')
    ])
    alternate_phone = fields.Char(string="Alternate No",copy=False,default="0000000000")
    job_id = fields.Many2one('hr.job',string="Applied Job",required=True)
    department_id = fields.Many2one('hr.department',string="Department",required=True)
    offer_letter_type = fields.Selection([
        ('client', 'Client Employee'),
        ('internal', 'Internal Employee')
    ], string='Offer letter Type',required=True)

    # Interview Details
    l1_interview_date = fields.Datetime(string="Date and time of Interview")
    l1_interviewer_name = fields.Char(string="Panel / Spoc")
    l1_interviewer_email = fields.Char(string="Email")
    l1_interviewer_phone = fields.Char(string="Phone")
    l1_feedback = fields.Text(string="Feedback")
    l2_interview_date = fields.Datetime(string="Date and time of Interview")
    l2_interviewer_name = fields.Char(string="Panel / Spoc")
    l2_interviewer_email = fields.Char(string="Email")
    l2_interviewer_phone = fields.Char(string="Phone")
    l2_feedback = fields.Text(string="Feedback")
    l3_interview_date = fields.Datetime(string="Date and time of Interview")
    l3_interviewer_name = fields.Char(string="Panel / Spoc")
    l3_interviewer_email = fields.Char(string="Email")
    l3_interviewer_phone = fields.Char(string="Phone")
    l3_feedback = fields.Text(string="Feedback")

    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.")
    refuse_reason_id = fields.Many2one('hr.sourcing.refuse.reason', string='Refuse Reason', tracking=True)

    # 
    

    # @api.onchange('talent_contact_id')
    # def update_interviewer_details(self):
    #     for line in self:
    #         if line.talent_contact_id:
    #             line.l1_interviewer_name = line.talent_contact_id.id
    #             line.l2_interviewer_name = line.talent_contact_id.id
    #             line.l3_interviewer_name = line.talent_contact_id.id

    def archive_applicant(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Refuse Reason'),
            'res_model': 'sourcing.get.refuse.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sourcing_ids': self.ids, 'active_test': False},
            'views': [[False, 'form']]
        }

    def reset_sourcing(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        for applicant in self:
            applicant.write(
                {'stage_id': 'l0',
                 'refuse_reason_id': False})

    def toggle_active(self):
        res = super(HrSourcing, self).toggle_active()
        sourcing_active = self.filtered(lambda sourcing: sourcing.active)
        if sourcing_active:
            sourcing_active.reset_sourcing()
        sourcing_inactive = self.filtered(lambda sourcing: not sourcing.active)
        if sourcing_inactive:
            return sourcing_inactive.archive_applicant()
        return res

    def _application_count(self):
        for order in self:
            application_count = self.env['hr.applicant'].search([('origin_id', '=', order.id)])
            order.sourcing_app_count = len(application_count)

    def l0_select(self):
        for line in self:
            date = fields.Date.today()
            self.update({'stage_id':'l1','l0_selected':date})
    def l1_select(self):
        for line in self:
            date = fields.Date.today()
            self.update({'stage_id':'l2','l1_selected':date})

    def l2_select(self):
        for line in self:
            date = fields.Date.today()
            self.update({'stage_id':'l3','l2_selected':date})

    def l3_select(self):
        for line in self:
            date = fields.Date.today()
            self.update({'stage_id':'done','l3_selected':date})

    # def reject(self):
    #     for line in self:
    #         self.stage_id = 'reject'

    @api.onchange('sourcing_date')
    def updated_expected_joining_date(self):
        for line in self:
            if line.sourcing_date:
                line.expected_joining_date = line.sourcing_date + timedelta(days=20)


    def sourcing_done(self):
        for line in self:
            date = fields.Date.today()
            if self.stage_id == 'l0':
                self.update({'stage_id':'done','selection_date':date,'l0_selected':date})
            elif self.stage_id == 'l1':
                self.update({'stage_id':'done','selection_date':date,'l1_selected':date})
            else:
                self.update({'stage_id':'done','selection_date':date,'l2_selected':date})

    @api.depends('ectc','ctc','commission_percent','client_id')
    def compute_bill_rate(self):
        for line in self:
            line.billing_rate = (((line.ectc * line.commission_percent)/100)+line.ectc)/12

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.sourcing') or _('New')
        result = super(HrSourcing, self).create(vals)
        return result

    def name_get(self):
        result = []
        for application in self:
            name = str(application.sequence) + ' ' + str(application.name)
            result.append((application.id, name))
        return result

    def create_application(self):
        for line in self:
            if not line.applicant_resume_line_ids:
                raise ValidationError(_("Please update Experience of candidate"))
            if not line.applicant_skill_ids:
                raise ValidationError(_("Please update Skills of candidate"))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Application'),
            'res_model': 'sourcing.application.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sourcing_id': self.id},
            'views': [[False, 'form']]
        }

    def create_sourcing_application(self):
        application_count = self.env['hr.applicant']
        if not application_count:
            categ_ids = [x.id for x in list(self.category_id)]
            self.application_status = 'application_created'
            
            vals = {
                'origin_id': self.id,
                'name': self.name,
                'partner_name':self.candidate_name,
                'job_id':self.job_id.id,
                'client_id':self.client_id.id,
                'partner_mobile':self.mobile,
                'email_from':self.email,
                'birthday':self.dob,
                'categ_ids':[(6, 0, categ_ids)],
                'current_location':self.current_location,
                'street':self.street,
                'street2':self.street2,
                'zip':self.zip,
                'city':self.city,
                'country_id':self.country_id.id,
                'state_id':self.state_id.id,
                'notice_period_id':self.notice_period_id.id,
                'other_offers':self.other_offers_bool,
                'father_name':self.father_name,
                # skills need to be added
                'applicant_skill_ids':[(6, 0, [skill.id for skill in self.applicant_skill_ids])],
                'applicant_resume_line_ids':[(6, 0, [skill.id for skill in self.applicant_resume_line_ids])],
                'total_exp_year':self.total_exp_year,
                'total_exp_month':self.total_exp_month,
                'relevant_exp_year':self.relevant_exp_year,
                'relevant_exp_month':self.relevant_exp_month,
                'current_or_last_company':self.current_or_last_company,
                'recruitment_hr_id':self.recruiter_id.id,
                'recruitment_hr_manager_id':self.lead_co_ordinator_id.id,
                'selection_date':self.selection_date,
                'lead_contact_id':self.lead_contact_id.id,
                'lead_contact_email':self.lead_contact_email,
                'lead_contact_number':self.lead_contact_number,
                'talent_contact_id':self.talent_contact_id.id,
                'talent_contact_email':self.talent_contact_email,
                'talent_contact_number':self.talent_contact_number,
                'resume_no':self.resume_no,
                'salary_expected':self.ectc,
                'salary_proposed':self.ctc,
                'overall_ctc':self.ctc,
                'job_code':self.jc_no,
                'contact_account':self.contact_account,
                'business_unit':self.business_unit,
                'sourcing_date':self.sourcing_date,
                'joining_status':self.joining_status,
                'jc_status':self.jc_status,
                'offer_status':self.offer_status,
                'dnh_status':self.dnh_status,
                'wo_status':self.wo_status,
                'bgv_status':self.bgv_status,
                'work_location_id':self.work_location_id.id,
                'preferred_location':self.preferred_location,
                'expected_joining_date':self.expected_joining_date,
                'study_field':self.study_field.id,
                'gender':self.gender,
                'alternate_phone':self.alternate_phone,
                'department_id':self.department_id.id,
                'offer_letter_type':self.offer_letter_type,
                'currently_employed':self.currently_employed,
                'identification_id':self.aadhar_no,
                'employer_name':self.current_or_last_company,
                'module_lead_id':self.module_lead_id.id,
                'hourly_salary_bool':self.hourly_salary_bool,
                'amount_per_hour':self.amount_per_hour,
                'no_of_hours':self.no_of_hours,
                'total_amount':self.total_amount,
                'job_type_id':self.job_type_id.id

                # 'preffered_location_id'



            }
            app_obj = self.env['hr.applicant'].create(vals)
            if app_obj:
                attachemt_ids = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','hr.sourcing')])
                if attachemt_ids:
                    for line in attachemt_ids:
                        attachment = self.env['ir.attachment'].sudo().create({
                            'name': line.name ,
                            'type': 'binary',
                            'datas': line.datas,
                            'res_id':app_obj.id,
                            'res_model': 'hr.applicant',
                            })
            
        else:
            if self.application_status == 'application_created':
                raise UserError(_("Application already created, Please Check and Confirm your application"))
            else:
                raise UserError(_("Application already created, Please update the reasons and confirm the record"))


        # for line in self:
        #   application_data = {
        #   'default_name': line.name,
        #   }

        # dict_act_window = self.env['ir.actions.act_window']._for_xml_id('employee_recruitment_customisation.open_view_application_list')
        # dict_act_window['context'] = application_data
        # return dict_act_window

    

class HrWorkLocationsLine(models.Model):
    _name = 'hr.source.work.location.line'

    location_id = fields.Many2one('hr.work.location',string='Location')
    source_loc_id = fields.Many2one('hr.sourcing',required=False, ondelete='cascade')



class SourcingRefuseReason(models.Model):
    _name = "hr.sourcing.refuse.reason"
    _description = 'Refuse Reason of Sourcing'

    name = fields.Char('Description', required=True, translate=True)
    active = fields.Boolean('Active', default=True)