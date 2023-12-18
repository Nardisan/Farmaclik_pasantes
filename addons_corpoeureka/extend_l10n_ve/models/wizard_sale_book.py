# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import date

from time import gmtime, strftime
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ReportExtendReportShoopingBookExcel(models.AbstractModel):
    _name = 'report.extend_l10n_ve.report_sale_book_excel'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Libro de Ventas en Excel'

    def generate_xlsx_report(self, workbook, data, obj):
        # Obtenemos la data necesaria para generar el reporte
        excel_data = self._use_data_dict(docids=[],data=data)

        # Formatos
        format1 = workbook.add_format({'font_size': 22, 'bg_color': '#D3D3D3'})
        format2 = workbook.add_format({'font_size': 12, 'bold': True})
        format3 = workbook.add_format({'font_size': 10})
        format4 = workbook.add_format({'font_size': 22, })
        format5 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        format6 = workbook.add_format({'font_size': 22, 'bg_color': '#FFFFFF'})
        format7 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        format8 = workbook.add_format({'font_size': 10, 'bold': True})
        format24 = workbook.add_format({'font_size': 12})
        format7.set_align('center')
        
        format22 = workbook.add_format({'font_size': 12})
        format23 = workbook.add_format(
            {'font_size': 14, 'bold': True, 'bg_color': '#FFFFFF'})
        format66 = workbook.add_format(
            {'font_size': 14, 'bg_color': '#FFFFFF'})
        format66.set_align('center')
        format22.set_align('center')

        # Hojas del Excel
        report_name = "Libro de venta".upper()
        current_date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        current_date = str( datetime.now().strftime("%Y-%m-%d %H:%M %p") )
        vat = self.env.company.rif if self.env.company.rif else ''
        name_company = self.env.company.display_name if self.env.company.display_name else ''
        
        sheet = workbook.add_worksheet(report_name)
        date_range = 'Desde {} hasta {}'.format(data['form']['date_from'],data['form']['date_to'])
        
        sheet.merge_range('A1:B1', name_company, format66)
        sheet.merge_range('A2:B2', 'RIF: '+vat, format24)
        sheet.merge_range('A3:B3', report_name, format24)
        sheet.merge_range('A4:C4', 'Rango: '+date_range, format24)
        
        sheet.write('A8', _("Oper. Nro"), format2)
        sheet.set_column('A:A', 15)
        
        sheet.write('B8', _("Fecha de la Factura"), format2)
        sheet.set_column('B:B', 20)
        
        sheet.write('C8', _("RIF. No."), format2)
        sheet.set_column('C:C',20)
        
        sheet.write('D8', _("Nombre Apellido o Razón Social del Comprador"), format2)
        sheet.set_column('D:D',30)

        #sheet.write('E8', _("Serie"), format2)
        #sheet.set_column('E:E',20)

        sheet.write('E8', _("Nro Control"), format2)
        sheet.set_column('E:E',20)

        sheet.write('F8', _("Factura."), format2)
        sheet.set_column('F:F',20)

        sheet.write('G8', _("Núm. Planilla de Export"), format2)
        sheet.set_column('G:G',20)

        sheet.write('H8', _("Núm. de Expedte. Import"), format2)
        sheet.set_column('H:H',25)

        sheet.write('I8', _("Serie "), format2)
        sheet.set_column('I:I',28)

        sheet.write('J8', _("Número Nota Debito"), format2)
        sheet.set_column('J:J',20)

        sheet.write('K8', _("Número Nota Credito."), format2)
        sheet.set_column('K:K',20)

        sheet.write('L8', _("Tipo de Transacción"), format2)
        sheet.set_column('L:L',20)

        sheet.write('M8', _("Número de Factura Afectada"), format2)
        sheet.set_column('M:M',28)

        sheet.write('N8', _("Total Ventas Incluyendo el IVA"), format2)
        sheet.set_column('N:N',20)

        sheet.write('O8', _("Ventas Exentas o Exoneradas"), format2)
        sheet.set_column('O:O',20)

        sheet.merge_range('P7:S7','Contribuyente',format3)

        sheet.write('P8', _("Base Imponible"), format2)
        sheet.set_column('P:P',20)

        sheet.write('Q8', _("% Alicuota"), format2)
        sheet.set_column('Q:Q',20)

        sheet.write('R8', _("Impuesto IVA"), format2)
        sheet.set_column('R:R',25)

        sheet.write('S8', _("Ventas Exentas o Exoneradas"), format2)
        sheet.set_column('S:S',25)

        sheet.merge_range('T7:V7','No Contribuyente',format3)

        sheet.write('T8', _("Base Imponible"), format2)
        sheet.set_column('T:T',25)
        
        sheet.write('U8', _("% Alícuota"), format2)
        sheet.set_column('U:U',20)

        sheet.write('V8', _("Impuesto IVA"), format2)
        sheet.set_column('V:V',25)

        sheet.merge_range('W7:Y7','Retención de IVA',format3)

        sheet.write('W8', _("IVA Retenido (por el comprador)"), format2)
        sheet.set_column('W:W',25)

        sheet.write('X8', _("Comp. de Retención"), format2)
        sheet.set_column('X:X',25)

        sheet.write('Y8', _("Agente de Retención"), format2)
        sheet.set_column('Y:Y',25)


        row_initial = 8
        row_number = row_initial
        row_number_aux = 0
        col_number = 0
        count = 1
        data_format1 = workbook.add_format({'font_size': 10})
        data_format2 = workbook.add_format({'font_size': 10})

        R40 = 0
        R31 = 0
        R32 = 0
        R312 = 0
        R313 = 0
        R322 = 0
        R323 = 0
        R442 = 0
        R342 = 0
        R443 = 0                
        R343 = 0                
        R42 = 0               
        R34 = 0              
        R35 = 0             
        R36 = 0              
        untaxed = 0               
        acum_exento = 0               
        untaxed_deductible = 0
        untaxed_not_deductible = 0                
        tax = 0
        tax_deductible = 0
        tax_not_deductible = 0                
        retencion = 0   
        retention = 0               
        retention_three = 0             
        total = 0                
        iva_percibido = 0                
        iva_percibido_g = 0                
        retencion_g = 0               
        retencion_ga = 0               
        iva_percibido_ga = 0              
        retencion_r  = 0                
        iva_percibido_r = 0
        monto_impuesto_untaxed_exento = 0
        prorratas = 0                
        proc_prorrata = 0                
        acumret = 0
       
        if excel_data['fact']:  

            for fact in excel_data['fact'].sorted( lambda f: f.invoice_date ):
                # Calculos
                total += (-fact.amount_total if fact.move_type == 'out_refund' else fact.amount_total) if fact.currency_id.name == 'VEF' else  -fact.amount_ref if fact.move_type == 'out_refund' else fact.amount_ref
                
                domain = 'price_subtotal' if fact.currency_id.name == 'VEF' else 'price_subtotal_ref'

                suma_iva = 0
                suma_no_iva = 0
                exento = 0
                iva = 0
                base_imp =0
                for line in fact.invoice_line_ids:
                    if not len(line.tax_ids) or line.tax_ids[0].amount == 0 :
                        suma_iva +=1
                    else: 
                        suma_no_iva +=1
                        total_iva = sum(fact.invoice_line_ids.filtered(lambda line: len(line.tax_ids ) and line.tax_ids[0].amount != 0).mapped(domain)) 

                total_fact = (-fact.amount_total if fact.move_type == 'out_refund' else fact.amount_total) if fact.currency_id.name == 'VEF' else  -fact.amount_ref if fact.move_type == 'out_refund' else fact.amount_ref
                iva = ((round(fact.amount_total - fact.amount_untaxed,2) if fact.move_type == 'out_invoice' else round(-fact.amount_total + fact.amount_untaxed,2) ) if fact.currency_id.name == 'VEF' else round(fact.amount_ref - fact.amount_untaxed_ref,2) if fact.move_type == 'out_invoice' else round(-fact.amount_ref+fact.amount_untaxed_ref,2)) 

                if len(fact.invoice_line_ids) == suma_iva:
                    exento = total_fact
                elif len(fact.invoice_line_ids) == suma_no_iva:
                    total_iva = total_fact
                else:
                    exento = total_fact - total_iva - iva 

                base_imp = total_fact - exento - iva
                
                acum_exento += -exento if fact.move_type == 'out_refund' else exento

                if( len( fact.invoice_line_ids.filtered( lambda line: len( line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced') ) ) ) ):
                    R443 += -sum(fact.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain)) \
                        if fact.move_type == 'out_refund' \
                        else sum(fact.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain))                                  

                    R343 += -(sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain))) \
                        if fact.move_type == 'out_refund' \
                        else (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain)))

                    if fact.wh_id:
                        retencion_r += -( sum( fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain) ) ) * retention \
                            if fact.move_type == 'out_refund' \
                            else ( sum( fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain) ) ) * retention

                        iva_percibido_r += - (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain))-((sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain)))*retention)) \
                                if fact.move_type == 'out_refund' \
                                else (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain))-((sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'reduced'))).mapped(domain)))*retention))

                if( len( fact.invoice_line_ids.filtered( lambda line: len( line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional') ) ) ) ):
                    R442 += -sum(fact.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain)) \
                        if fact.move_type == 'out_refund' \
                        else sum(fact.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain))                                  

                    R342 += -(sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain))) \
                        if fact.move_type == 'out_refund' \
                        else (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain)))

                    if fact.wh_id:
                        retencion_ga += -( sum( fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain) ) ) * retention \
                            if fact.move_type == 'out_refund' \
                            else ( sum( fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain) ) ) * retention

                        iva_percibido_ga += - sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain)) * retention \
                            if fact.move_type == 'out_refund' \
                            else (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'additional'))).mapped(domain) *retention ))                                                

                
                if( len( fact.invoice_line_ids.filtered( lambda line: len( line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general') ) ) ) ):
                    R42 += -sum(fact.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain)) \
                        if fact.move_type == 'out_refund' \
                        else sum(fact.invoice_line_ids.filtered(lambda line: len(line.mapped('tax_ids').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain))                                  

                    R34 += -(sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain))) \
                        if fact.move_type == 'out_refund' \
                        else (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain)))

                    if fact.wh_id:
                        retencion_g += -( sum( fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain) ) ) * retention \
                            if fact.move_type == 'out_refund' \
                            else ( sum( fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain) ) ) * retention

                        iva_percibido_g += - sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain)) * retention \
                            if fact.move_type == 'out_refund' \
                            else (sum(fact.line_ids.filtered(lambda line: len(line.mapped('tax_line_id').filtered(lambda tax: tax.aliquot_type == 'general'))).mapped(domain))*retention)                                              
                                                                                                            
                untaxed += -exento if fact.move_type == 'out_refund' else exento
                R40 +=  -exento if fact.move_type == 'out_refund' else exento

                retencion += -fact.wh_id.total_tax_ret if fact.move_type == 'out_refund' else fact.wh_id.total_tax_ret
                tax += -fact.amount_tax if fact.move_type == 'out_refund' else fact.amount_tax
                iva_percibido += -(fact.amount_tax - fact.wh_id.total_tax_ret) if fact.move_type == 'out_refund' else (fact.amount_tax - fact.wh_id.total_tax_ret)

                if not fact.deductible:
                    tax_deductible += (fact.amount_total - fact.amount_untaxed if fact.move_type == 'out_invoice' else -fact.amount_total + fact.amount_untaxed ) if fact.currency_id.name == 'VEF' else fact.amount_ref - fact.amount_untaxed_ref if fact.move_type == 'out_invoice' else -fact.amount_ref+fact.amount_untaxed_ref 
                    untaxed_deductible += -sum(fact.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped(domain)) if fact.move_type == 'out_refund' else sum(fact.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped(domain))
                
                else:
                    tax_not_deductible += -fact.amount_tax if fact.move_type == 'out_refund' else fact.amount_tax
                    untaxed_not_deductible += -sum(fact.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped(domain)) if fact.move_type == 'out_refund' else sum(fact.invoice_line_ids.filtered(lambda whl: whl.tax_ids).mapped(domain))
                

                # Fin de los calculos
                
                
                sheet.write(row_number,col_number,count,format3) #
                sheet.set_column('A:A', 15)

                sheet.write(row_number,col_number + 1,fact.invoice_date.strftime('%d-%m-%Y'),format3)
                sheet.set_column('B:B', 20)
                
                sheet.write(row_number,col_number + 2,fact.partner_id.rif,format3)
                sheet.set_column('C:C', 20)

                sheet.write(row_number,col_number + 3,fact.partner_id.name,format3)
                sheet.set_column('D:D', 30)
                
                if fact.move_type=='out_invoice':
                    sheet.write(row_number,col_number + 4,fact.nro_control,format3)
                    sheet.set_column('E:E', 20)
                elif fact.move_type=='out_refund':
                    sheet.write(row_number,col_number + 4,fact.ref_credit,format3)
                    sheet.set_column('E:E', 20)
                
                if fact.move_type=='out_invoice':
                    sheet.write(row_number,col_number + 5,fact.name ,format3)
                    sheet.set_column('F:F', 20)
                else:
                    sheet.write(row_number,col_number + 5,'-',format3)
                    sheet.set_column('F:F', 20)
                
                sheet.write(row_number,col_number + 6,fact.num_import,format3)
                sheet.set_column('G:G', 20)

                sheet.write(row_number,col_number + 7,fact.num_export,format3)
                sheet.set_column('H:H', 20)

                sheet.write(row_number,col_number + 8,'-',format3)#SERIE
                sheet.set_column('I:I', 25)
                
                sheet.write(row_number,col_number + 9,' ',format3)
                sheet.set_column('J:J', 28)

                sheet.write(row_number,col_number + 10,fact.num_credit if fact.move_type == 'out_refund' else '-',format3)
                sheet.set_column('K:K', 20)      
                
                sheet.write(row_number,col_number + 11,fact.transaction_type,format3)
                sheet.set_column('L:L', 20)

                if fact.move_type == 'out_invoice':
                    sheet.write_number(row_number,col_number + 12, fact.reversed_entry_id.name,format3)
                    sheet.set_column('M:M', 25)

                sheet.write_number(row_number,col_number + 13, round(total_fact,2),format3)
                sheet.set_column('N:N', 28)
                
                sheet.write_number(row_number,col_number + 14, round(exento,2),format3)# ventas exoneradas
                sheet.set_column('O:O', 20)
                
                sheet.write_number(row_number,col_number + 15,round(base_imp,2),format3) #BASE IMPONIBLE
                sheet.set_column('P:P', 20)

                sheet.write_number(row_number,col_number + 16,sum(fact.invoice_line_ids.mapped('tax_ids.amount')),format3)
                sheet.set_column('Q:Q', 20)

                sheet.write_number(row_number,col_number + 17,iva,format3)
                sheet.set_column('R:R', 20)

                sheet.write_number(row_number,col_number + 18,0,format3)
                sheet.set_column('S:S', 25)

                sheet.write(row_number,col_number + 19, 0,format3)
                sheet.set_column('T:T',25)

                sheet.write(row_number,col_number + 20, 0,format3)
                sheet.set_column('U:U',25)

                sheet.write(row_number,col_number + 21, 0,format3)
                sheet.set_column('V:V',20)

                sheet.write(row_number,col_number + 22, 0,format3)
                sheet.set_column('W:W',25)

                sheet.write(row_number,col_number + 23, 0,format3)
                sheet.set_column('X:X',25)

                sheet.write(row_number,col_number + 24, 0,format3)
                sheet.set_column('Y:Y',25)

                row_number += 1
                count += 1

        # Totales en las columnas
        sheet.write(row_number,col_number + 12,'TOTAL',format8)
        sheet.write_number(row_number,col_number + 13,round(total,2),format8) #Total de la factura
        sheet.write_number(row_number,col_number + 14,round(acum_exento,2),format8) #Total exento
        sheet.write_number(row_number,col_number + 15,round(R42 + R31 + R312 + R313 + R442 + R443,2),format8) #Total de la base imponible
        sheet.write_number(row_number,col_number + 17,round(tax_deductible,2),format8) #Total Impuesto IVA deducible
        sheet.write_number(row_number,col_number + 18,round(untaxed_not_deductible,2),format8) #Total Base imponible no deducible
        sheet.write_number(row_number,col_number + 19,round(tax_not_deductible,2),format8) #Total impuesto no deducible
        sheet.write_number(row_number,col_number + 20,round(retencion,2),format8) #Total de retenciones


        # Totales al final de la tabla
        row_number += 5
        sheet.write('F{}'.format(row_number),'Base imponible',format8)
        sheet.write('G{}'.format(row_number),'Debito fiscal',format8)
        sheet.write('H{}'.format(row_number),'IVA Retenido por el Comprador',format8)
        sheet.write('I{}'.format(row_number),'IVA de Ventas Percibido',format8)
        
        sheet.merge_range('C{}:E{}'.format(row_number+1,row_number+1),'Total: Ventas Interna No Gravadas [40]',format3)
        sheet.merge_range('C{}:E{}'.format(row_number+2,row_number+2),'Suma de las: Ventas de Exportación [41]',format3)
        sheet.merge_range('C{}:E{}'.format(row_number+4,row_number+4),'Suma de las: Ventas Internas Afectas solo Alicuota General [42]   [43]',format3)
        sheet.merge_range('C{}:E{}'.format(row_number+5,row_number+5),'Suma de las: Ventas Internas Afectas en Alicuota General + Adicional [442]   [452]',format3)
        sheet.merge_range('C{}:E{}'.format(row_number+6,row_number+6),'Suma de las: Ventas Internas Afectas en Alicuota Reducida [443]   [453]',format3)
        sheet.merge_range('C{}:E{}'.format(row_number+7,row_number+7),'Total',format8)

        sheet.write_number('F{}'.format(row_number+1),round(acum_exento,2) if R40 else 0.0,format3)
        sheet.write_number('G{}'.format(row_number+1),0.0,format3)

        sheet.write_number('F{}'.format(row_number+2),round(R31,2) if R31 else 0.0,format3)
        sheet.write_number('G{}'.format(row_number+2),0.0,format3)

        sheet.write_number('F{}'.format(row_number+3),round(R312,2) if R312 else 0.0,format3)
        sheet.write_number('G{}'.format(row_number+3),round(R322,2) if R322 else 0.0,format3)

        sheet.write_number('F{}'.format(row_number+4),round(R42,2) if R42 else 0.0,format3)
        sheet.write_number('G{}'.format(row_number+4),round(R34,2) if R34 else 0.0,format3)

        sheet.write_number('F{}'.format(row_number+5),round(R313,2) if R313 else 0.0,format3)
        sheet.write_number('G{}'.format(row_number+5),round(R323,2) if R323 else 0.0,format3)
        sheet.write_number('H{}'.format(row_number+5),round(retencion,2),format3)

        sheet.write_number('F{}'.format(row_number+6),round(R442,2) if R442 else 0.0,format3)
        sheet.write_number('G{}'.format(row_number+6),round(R342,2) if R342 else 0.0,format3)

        sheet.write_number('F{}'.format(row_number+7),round(R40+R31+R312+R313+R42+R442+R443,2),format8)
        sheet.write_number('G{}'.format(row_number+7),round(R34+R342+R343+R32+R322+R323,2),format8)
        
        row_number_aux = row_number
        row_number_aux += 14

        sheet.write('B{}'.format(row_number_aux),'Contribuyente',format8)
        sheet.write('C{}'.format(row_number_aux),round(R42,2),format8)
        sheet.write('D{}'.format(row_number_aux),round(R34,2),format8)

        sheet.write('B{}'.format(row_number_aux+1),'No Contribuyente',format8)
        sheet.write('C{}'.format(row_number_aux+1),0,format8)
        sheet.write('D{}'.format(row_number_aux+1),0,format8)

        row_number += 12
        sheet.merge_range('F{}:H{}'.format(row_number,row_number),'Resumen Tasa General',format8)
        sheet.write('F{}'.format(row_number+1),'Tasa',format8)
        sheet.write('G{}'.format(row_number+1),'Base Imponible',format8)
        sheet.write('H{}'.format(row_number+1),'Débito Fiscal',format8)

        sheet.write('F{}'.format(row_number+2),'16%',format3)
        sheet.write_number('G{}'.format(row_number+2),round(R42,2),format3)
        sheet.write_number('H{}'.format(row_number+2),round(R34,2),format3) 

        sheet.write('F{}'.format(row_number+3),'-',format3)
        sheet.write_number('G{}'.format(row_number+3),0,format3)
        sheet.write_number('H{}'.format(row_number+3),0,format3)
        
        sheet.write('F{}'.format(row_number+4),'-',format3)
        sheet.write_number('G{}'.format(row_number+4),round(R312 + R442,2),format3)
        sheet.write_number('H{}'.format(row_number+4),round(R322 + R342,2),format3)

        sheet.write_number('G{}'.format(row_number+5),round(R313 + R443 + R42 + R31 + R312 + R442,2),format8)
        sheet.write_number('H{}'.format(row_number+5),round(R343 + R323 + R34 + R32 + R322 + R342,2),format8)

        workbook.close()

    def _get_account_move_entry(self, accounts, form_data, sortby, pass_date, display_account):
        cr = self.env.cr
        move_line = self.env['account.move.line']

        tables, where_clause, where_params = move_line._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        if form_data['target_move'] == 'posted':
            target_move = "AND m.state = 'posted'"
        else:
            target_move = ''
        sql = ('''
                SELECT l.id AS lid, acc.name as accname, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, 
                l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, 
                COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,
                m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                JOIN account_account acc ON (l.account_id = acc.id) 
                WHERE l.account_id IN %s AND l.journal_id IN %s ''' + target_move + ''' AND l.date = %s
                GROUP BY l.id, l.account_id, l.date,
                     j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name , acc.name
                     ORDER BY l.date DESC
        ''')
        params = (
            tuple(accounts.ids), tuple(form_data['journal_ids']), pass_date)
        cr.execute(sql, params)
        data = cr.dictfetchall()
        res = {}
        debit = credit = balance = 0.00
        for line in data:
            debit += line['debit']
            credit += line['credit']
            balance += line['balance']
        res['debit'] = debit
        res['credit'] = credit
        res['balance'] = balance
        res['lines'] = data
        return res

    @api.model
    def _use_data_dict(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        sortby = data['form'].get('sortby')
        in_bs = data['form'].get('in_bs')
        form_data = data['form']
        #branch_ids = data['form'].get('branch_ids',False)
        target_mov = ('posted','cancel') if form_data['target_move'] =='posted' else ('draft','cancel','posted')
        currency_id = self.env['res.currency'].browse([form_data['currency_id'][0]])
        company_id = self.env.company
        active_acc = data['form']['account_ids']
        accounts = self.env['account.account'].search(
            [('id', 'in', active_acc)]) if data['form']['account_ids'] else \
            self.env['account.account'].search([])
        date_start = datetime.strptime(form_data['date_from'],'%Y-%m-%d')
        date_end = datetime.strptime(form_data['date_to'], '%Y-%m-%d')
        docs_ret = self.env['account.wh.iva'].search([('move_type', 'in', ('out_invoice', 'out_refund'))])
        docs_fac = self.env['account.move'].search([('move_type', 'in', ('out_refund', 'out_invoice')),
                                                     ('date', '<=', date_end),
                                                     ('date', '>=', date_start),
                                                     #('currency_id', '=', currency_id.id),
                                                     ('state', 'in', target_mov),
                                                     #('branch_id', 'in', (branch_ids)),
                                                     ('journal_id', 'in', form_data['journal_ids'])]).sorted(key=lambda x: x.journal_id.id and x.partner_id.name if sortby == 'sort_journal_partner' else x.date).filtered(lambda c: c.line_ids.mapped('account_id') & accounts != self.env['account.account'])
        rete = self.env['account.wh.iva.line'].search([
                                        ('retention_id.date', '>=', date_start),
                                        ('retention_id.date', '<=', date_end),
                                        ('retention_id.move_type', 'in', ('out_invoice','out_refund')),
                                        ('state', 'not in', ('draft','anulled')),
                                        ('retention_id.company_id','=',self.env.company.id),
                                        ])
        con_documento = True
        model = self.env.context.get('active_model')
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        #branch = []
        #if branch_ids:
        #    branch = [branch.name for branch in
        #             self.env['res.branch'].search(
        #                 [('id', 'in', branch_ids)])]
        if not docs_fac:
            con_documento = False
            return {
                'doc_ids': docids,
                'doc_model': model,
                'data': data['form'],
                'docs': docs_ret,
                'rete': rete,
                'fact': False,
                'Accounts': False,
                'print_journal': codes,
                #'branch': branch,
                'currency_id': currency_id,
                'company_id': company_id,
                'company_vat':  company_id.vat[:10]+'-'+company_id.vat[10:] if company_id.vat else False,
                'in_bs':in_bs,
                'con_documento': con_documento,
            }
        
        display_account = 'movement'
        dates = []
        record = []
        for head in dates:
            pass_date = str(head)
            accounts_res = self.with_context(
                data['form'].get('used_context', {}))._get_account_move_entry(
                accounts, form_data, sortby,pass_date, display_account)
            if accounts_res['lines']:
                record.append({
                    'date': head,
                    'debit': accounts_res['debit'],
                    'credit': accounts_res['credit'],
                    'balance': accounts_res['balance'],
                    'child_lines': accounts_res['lines']
                })
        hora_printer = (datetime.now()).astimezone(pytz.timezone(self.env.user.tz)).strftime('%I:%M:%S %p')
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs_ret,
            'rete': rete,
            'fact': docs_fac,
            'time': hora_printer,
            'hora_printer': hora_printer,
            'Accounts': record,
            'print_journal': codes,
            #'branch': branch,
            'currency_id': currency_id,
            'company_id': company_id,
            'company_vat':  company_id.vat[:10]+'-'+company_id.vat[10:] if company_id.vat else False,
            'in_bs':in_bs,
            'con_documento': con_documento,
        }
    #----------------------------Version para pdf

class SaleBook(models.TransientModel):
    _inherit = 'wizard.book.sale'
    _description = 'Libro de ventas'

    def generate_excel_book(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = \
        self.read(['date_from', 'date_to', 'journal_ids','display_account', 'target_move','account_ids','sortby','currency_id','in_bs'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,lang=self.env.context.get('lang') or 'es_ES')
        return self.env.ref('extend_l10n_ve.action_report_sale_book_excel').report_action(self,data=data)