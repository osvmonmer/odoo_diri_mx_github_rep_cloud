# -*- coding: utf-8 -*-

import base64
from lxml import etree, objectify
from lxml.objectify import fromstring
from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_mx_edi_ordencompra = fields.Char(string='Orden de Compra ')

    def l10n_mx_edi_ordencompra_update_addenda(self):
        self.ensure_one()
        # addenda = self.env.ref('l10n_mx_addenda_waldos.l10n_mx_edi_addenda_waldos', raise_if_not_found=False)
        addenda = (
            self.partner_id.l10n_mx_edi_addenda or
            self.partner_id.commercial_partner_id.l10n_mx_edi_addenda)
        if not addenda:
            return True
        values = {
            'record': self,
        }
        addenda_node_str = addenda.render(values=values).strip()
        if not addenda_node_str:
            return True
        addenda_node = fromstring(addenda_node_str)
        if addenda_node.tag != '{http://www.sat.gob.mx/cfd/3}Addenda':
            node = etree.Element(etree.QName(
                'http://www.sat.gob.mx/cfd/3', 'Addenda'))
            node.append(addenda_node)
            addenda_node = node
        cfdi = self.l10n_mx_edi_get_xml_etree()
        cfdi.Addenda = addenda_node
        xml_signed = base64.encodestring(etree.tostring( cfdi, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        attachment_id = self.l10n_mx_edi_retrieve_last_attachment()
        attachment_id.write({
            'datas': xml_signed,
            'mimetype': 'application/xml'
        })
        self.message_post(
            body=_('Addenda has been added in the CFDI with success'),
            subtype='account.mt_invoice_validated')        
        return True
