# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from num2words import num2words
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.misc import formatLang, format_date, get_lang

from collections import defaultdict

class AccountMove(models.Model):
    _inherit = 'account.move'

    description = fields.Text(string="Description")
    billing_from = fields.Date(string="Billing from",required=False)
    billing_to = fields.Date(string="Billing to",required=False)
    days_in_month = fields.Integer(string="Days in a period",compute="_fetch_period_days")
    kind_attention = fields.Many2one('res.partner',string="Kind attention")
    po_date = fields.Date(string="PO Date")
    po_no = fields.Char(string="PO No.")
    text_amount = fields.Char(string="Amount in words", required=False, compute="number_to_word" )
    commission_percent = fields.Float(string="Commission %")
    inv_billing_type = fields.Selection([
        ('mid_month', '21/22 days'),
        ('full_month', '30/31 days')], 'Invoice Billing Type',related="partner_id.inv_billing_type")

    price_extras = fields.Monetary(string='Extra', store=True, readonly=True,
        currency_field='currency_id')


    @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
    def _compute_invoice_taxes_by_group(self):
        for move in self:

            # Not working on something else than invoices.
            if not move.is_invoice(include_receipts=True):
                move.amount_by_group = []
                continue

            lang_env = move.with_context(lang=move.partner_id.lang).env
            balance_multiplicator = -1 if move.is_inbound() else 1

            tax_lines = move.line_ids.filtered('tax_line_id')
            base_lines = move.line_ids.filtered('tax_ids')

            tax_group_mapping = defaultdict(lambda: {
                'base_lines': set(),
                'base_amount': 0.0,
                'tax_amount': 0.0,
                'base_laptop_charges':0.0,
                'base_travel_expense':0.0,
            })

            # Compute base amounts.
            for base_line in base_lines:

                base_amount = balance_multiplicator * (base_line.amount_currency if base_line.currency_id else base_line.balance)

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():

                    if base_line.tax_line_id.tax_group_id == tax.tax_group_id:
                        continue

                    tax_group_vals = tax_group_mapping[tax.tax_group_id]
                    if base_line not in tax_group_vals['base_lines']:
                        tax_group_vals['base_amount'] += base_amount
                        tax_group_vals['base_lines'].add(base_line)
                        tax_group_vals['base_laptop_charges'] = base_line.laptop_charges
                        tax_group_vals['base_travel_expense'] = base_line.travel_expense

            # Compute tax amounts.
            for tax_line in tax_lines:
                tax_amount = balance_multiplicator * (tax_line.amount_currency if tax_line.currency_id else tax_line.balance)
                tax_group_vals = tax_group_mapping[tax_line.tax_line_id.tax_group_id]
                tax_group_vals['tax_amount'] += tax_amount

            tax_groups = sorted(tax_group_mapping.keys(), key=lambda x: x.sequence)
            amount_by_group = []
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]
                # below code is added to get tax percent in report
                tax_percent = 0
                if tax_group_vals['base_amount'] >= 1:
                    tax_percent = round((tax_group_vals['tax_amount']/(tax_group_vals['base_amount']))*100 )
                amount_by_group.append((
                    tax_group.name,
                    tax_group_vals['tax_amount'],
                    tax_group_vals['base_amount'],
                    formatLang(lang_env, tax_group_vals['tax_amount'], currency_obj=move.currency_id),
                    formatLang(lang_env, tax_group_vals['base_amount'], currency_obj=move.currency_id),
                    len(tax_group_mapping),
                    tax_group.id,
                    tax_percent
                ))
            move.amount_by_group = amount_by_group

    

    @api.constrains('billing_from','billing_to')
    def check_billing_period(self):
        for line in self:
            if line.billing_to < line.billing_from:
                raise UserError(_('Billing to Period should be greater than billing from '))
    @api.depends('billing_from','billing_to')
    def _fetch_period_days(self):
        for line in self:
            if line.billing_from and line.billing_to:
                start_date = datetime.strptime(str(line.billing_from),"%Y-%m-%d")
                end_date = datetime.strptime(str(line.billing_to),"%Y-%m-%d")
                line.days_in_month = abs((end_date - start_date).days)+1
            else:
                line.days_in_month = 1

    @api.onchange('partner_id')
    def _fetch_commission(self):
        for line in self:
            if line.partner_id.commission_percent:
                line.commission_percent = line.partner_id.commission_percent

    @api.depends('amount_total')
    def number_to_word(self):
        number = round(self.amount_total)

        def get_word(n):
            words={ 0:"", 1:"One", 2:"Two", 3:"Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Eleven", 12:"Twelve", 13:"Thirteen", 14:"Fourteen", 15:"Fifteen", 16:"Sixteen", 17:"Seventeen", 18:"Eighteen", 19:"Nineteen", 20:"Twenty", 30:"Thirty", 40:"Forty", 50:"Fifty", 60:"Sixty", 70:"Seventy", 80:"Eighty", 90:"Ninty" }
            if n<=20:
                return words[n]
            else:
                ones=n%10
                tens=n-ones
                return words[tens]+" "+words[ones]
                
        def get_all_word(n):
            d=[100,10,100,100]
            v=["","Hundred And","Thousand","lakh"]
            w=[]
            for i,x in zip(d,v):
                t=get_word(n%i)
                if t!="":
                    t+=" "+x
                w.append(t.rstrip(" "))
                n=n//i
            w.reverse()
            w=' '.join(w).strip()
            if w.endswith("And"):
                w=w[:-3]
            return w

        arr=str(number).split(".")
        number=int(arr[0])
        crore=number//10000000
        number=number%10000000
        word=""
        if crore>0:
            word+=get_all_word(crore)
            word+=" crore "
        word+=get_all_word(number).strip()+" Rupees"
        if len(arr)>1:
             if len(arr[1])==1:
                arr[1]+="0"
             word+=" and "+get_all_word(int(arr[1]))+" paisa"
        self.text_amount = word

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    employee_id = fields.Many2one('hr.employee',string="Employee",domain="[('client_work_address','=',partner_id)]")
    billing_rate = fields.Float(string="Billing Rate",digits=(16, 2),compute="_fetch_billing_rate",store=True)
    worked_days = fields.Float(string="Worked Days")
    leaves_taken = fields.Float(string="Leaves Taken")
    billed_days = fields.Float(string="Billed Days")
    commission_percent = fields.Float(string="Commission %",related='move_id.commission_percent')
    laptop_charges = fields.Float(string="Laptop Charges")
    travel_expense = fields.Float(string="Travel Expense")

    
    unit_price = fields.Float(string='Unit Price', digits='Product Price',compute="_fetch_unit_price",store=True)

    markup_value = fields.Float(string="Markup Value",compute="compute_final_price_value")
    price_unit = fields.Float(string='Unit Price', digits='Product Price',compute="compute_final_price_value",store=True)

    # Fields for accord 
    total_hours_worked = fields.Float(string="Hours worked in Saturday/Sunday")
    total_amount = fields.Float(string="Total amount to be paid")
    no_of_weekends = fields.Float(string="Saturday/Sundays worked")
    charges = fields.Float(string="Charges per day")
    remarks = fields.Text(string="Remarks")

    @api.depends('move_id.partner_id','unit_price')
    def compute_final_price_value(self):
        for line in self:
            if line.move_id.partner_id.enable_markup_value:
                if line.move_id.partner_id.markup_value:
                    line.markup_value = (line.unit_price * line.move_id.partner_id.markup_value)/100
                    line.price_unit = line.markup_value + line.unit_price + line.laptop_charges + line.travel_expense
            else:
                line.price_unit = line.unit_price + line.laptop_charges + line.travel_expense
                line.markup_value = False

    @api.depends('commission_percent','employee_id')
    def _fetch_billing_rate(self):
        actual_ctc = 0
        for line in self:
            # actual_ctc = line.employee_id.salary_proposed + line.employee_id.annual_variable_pay
            actual_ctc = line.employee_id.salary_proposed
            line.billing_rate = ((actual_ctc + ( (actual_ctc)* line.commission_percent/100))/12)
            # line.billing_rate = ((line.employee_id.salary_proposed/12))

    @api.depends('worked_days','leaves_taken','billed_days','move_id.inv_billing_type','total_amount')
    def _fetch_unit_price(self):
        unit_price = 0
        for line in self:
            if line.worked_days and line.billed_days:
                unit_price = (line.billing_rate*line.worked_days)/line.billed_days
                if line.total_hours_worked and line.total_amount:
                    line.unit_price = unit_price + line.total_amount
                else:
                    line.unit_price = unit_price
            else:
                line.unit_price = 0

    @api.onchange('employee_id')
    def _fetch_attendance_details(self):
        for line in self:
            att_track_id = self.env['attendance.tracking'].search([('emp_id','=',line.employee_id.id),('billing_from','>=',line.move_id.billing_from),('billing_to','<=',line.move_id.billing_to)])
            if att_track_id:
                for att in att_track_id:
                    line.update({
                        'worked_days':att.worked_days,
                        'leaves_taken':att.leaves_taken,
                        'billed_days':att.billed_days,
                        'laptop_charges':line.employee_id.laptop_charges,
                        'travel_expense':line.employee_id.travel_expense,
                        'total_hours_worked':att.total_hours_worked,
                        'total_amount':att.total_amount,
                        'no_of_weekends':att.no_of_weekends,
                        'charges':att.charges,
                        })
            else:
                line.update({
                        'worked_days':False,
                        'leaves_taken':False,
                        'billed_days':False,
                        'laptop_charges':False,
                        'travel_expense':False,
                        'total_hours_worked':False,
                        'total_amount':False,
                        'no_of_weekends':False,
                        'charges':False,
                        })

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.move_type,
        )

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = (quantity * line_discount_price_unit)

        # Compute 'price_total'.
        if taxes:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res


