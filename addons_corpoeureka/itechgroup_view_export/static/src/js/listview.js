odoo.define('itechgroup_view_export_tree', function (require) {
"use strict";

    var core = require('web.core');
    var Sidebar = require('web.Sidebar');
    var session = require('web.session');

    var QWeb = core.qweb;
    var _t = core._t;

    Sidebar.include({
        init : function (parent, options) {
            this._super.apply(this, arguments);
            var view = this.getParent();
            var self = this;
            if (view.renderer.viewType && view.renderer.viewType === "list") {
                this.sections.splice(
                    10, 0, { 'name' : 'customExport', 'label' : _t('Custom Export')});
                self.items.customExport = [];
                session.user_has_group('itechgroup_view_export.group_can_export_view_to_pdf').then(function(has_group) {
                    if(has_group) {
                        self.items.customExport.push({
                            label: 'Como PDF',
                            callback: self.on_sidebar_export_to_pdf,
                        });
                        if(self.$el !== undefined){
                            self._redraw();
                        }
                    }
                });
                session.user_has_group('itechgroup_view_export.group_can_export_view_to_excel').then(function(has_group) {
                    if(has_group) {
                        self.items.customExport.push({
                            label: 'Como Excel',
                            callback: self.on_sidebar_export_excel,
                        });
                        if(self.$el !== undefined){
                            self._redraw();
                        }
                    }
                });
                session.user_has_group('itechgroup_view_export.group_can_export_view_to_csv').then(function(has_group) {
                    if(has_group) {
                        self.items.customExport.push({
                            label: 'Como CSV',
                            callback: self.on_sidebar_export_csv,
                        });
                        if(self.$el !== undefined){
                            self._redraw();
                        }
                    }
                });
            }
        },

        on_sidebar_export_to_pdf: function() {
            var view = this.getParent();
            var children = view.getChildren();
            var self = this;
            var data = this._get_treeview_data(children, view);
            session.user_has_group('itechgroup_view_export.group_can_export_view_to_pdf').then(function(has_group) {
                if(has_group) {
                    var doc = new jsPDF('l', 'pt', 'a4');
                    var marign_left = 510;
                    var size_30 = 30;
                    var size_32 = 32;
                    var size_13 = 12;
                    var size_110 = 110;
                    var font_size = 12;

                    // Getting company data
                    self._rpc({
                        model: "res.company",
                        method: "get_datas",
                        args: [[self.id]]
                    }).then(function (result) {
                            // Preparing Header
                            var header = function(data) {
                                var pageSize = doc.internal.pageSize;
                                if (result['with_header']) {
                                    doc.setFontSize(font_size);
                                    // Check if the logo exist or not
                                    if (result['logo']){
                                        var headerImgData = "data:image/png;base64," + result['logo'];
                                        doc.addImage(headerImgData, 'JPEG', size_30, size_30, 150, 60);
                                    }
                                    doc.setFontType("bold");
                                    doc.text(marign_left, size_30, result['name']);
                                    doc.setFontStyle('normal');
                                    doc.setFontSize(size_13);
                                    if (result['street'] !== undefined){
                                        doc.text(marign_left, 48, result['street']);
                                    }
                                    if (result['phone'] !== undefined){
                                        doc.text(marign_left, 84, 'Tel: ' + result['phone']);
                                    }
                                    if (result['email'] !== undefined){
                                        doc.text(marign_left, 102, result['email']);
                                    }
                                    doc.setFontSize(font_size);
                                }
                                // Header line
                                if(result['with_header_bar']) {
                                    doc.setLineWidth(1.5);
                                    
                                    doc.setDrawColor(result['header_bar_color']);
                                    doc.line(size_30, size_110, pageSize.width - size_30, size_110); 
                                }
                                // Footer
                                if(result['with_footer']) {
                                    var str = "Page " + data.pageCount;
                                    if (typeof doc.putTotalPages === 'function') {
                                        str = str
                                    }
                                    doc.setFontSize(size_13);
                                    doc.text(str, 745, pageSize.height - size_32);
                                    if (result['vat'] !== undefined){
                                        var vat = result['vat'] ? result['vat'] : '';
                                        doc.text('Vat/GSTIN : ' + vat, size_30, pageSize.height - size_32);
                                    }
                                    if (result['website'] !== undefined){
                                        doc.text(result['website'], size_30, pageSize.height - 15);
                                    }
                                    doc.text('', marign_left, pageSize.height - size_32);
                                    doc.text('', marign_left, pageSize.height - size_13);
                                }

                                // Footer line
                                if (result['with_footer_bar']) {
                                    doc.setDrawColor(result['footer_bar_color']);
                                    doc.line(size_30, pageSize.height - 45, pageSize.width - size_30, pageSize.height - 45);
                                }
                            };

                            var options = {
                                beforePageContent: header,
                                startY: doc.previousAutoTable.finalY,
                                margin: {
                                    top: 65,
                                    bottom: 65,
                                },
                            };
                        doc.setFontSize(10);
                        doc.autoTable({
                            didDrawPage: header,
                            head: [data.header],
                            body: data.rows,
                            theme: result['table_theme'],
                            startY: 140,
                            margin: {
                                top: 140,
                                left: size_30,
                                right: size_30,
                            },
                            overflowColumns: false,
                            pageBreak: 'auto',
                            rowPageBreak: 'avoid',
                        });

                        doc.save(view.modelName.replace('.', '_') + '.pdf');
                        $.unblockUI();
                    });
                }
            });
        },

        on_sidebar_export_excel: function() {
            var view = this.getParent();
            var children = view.getChildren();
            var data = this._get_treeview_data(children, view);
            this.getSession().get_file({
                url: '/web/export/xls_view',
                data: {data: JSON.stringify({
                    model: view.modelName,
                    headers: data.header,
                    rows: data.rows
                })},
                complete: $.unblockUI
            });
        },

        on_sidebar_export_csv: function() {
            var view = this.getParent();
            var children = view.getChildren();
            var data = this._get_treeview_data(children, view);
            this.getSession().get_file({
                url: '/web/export/csv_view',
                data: {data: JSON.stringify({
                    model: view.modelName,
                    headers: data.header,
                    rows: data.rows
                })},
                complete: $.unblockUI
            });
        },

        _get_treeview_data: function(children, view) {
            var export_columns_keys = [];
            var export_columns_names = [];
            var column_index = 0;
            var export_rows = [];
            var column_header_selector;

            if (children) {
                children.every(function (child) {
                    if (child.field && child.field.type == 'one2many') {
                        view = child.viewmanager.views.list.controller;
                        return false;
                    }
                    if (child.field && child.field.type == 'many2many') {
                        view = child.list_view;
                        return false;
                    }
                    return true;
                });
            }

            $.each(view.renderer.columns, function () {
                if (this.tag == 'field' && (this.attrs.widget === undefined || this.attrs.widget != 'handle')) {
                    export_columns_keys.push(column_index);
                    column_header_selector = '.o_list_table  > thead > tr> th:not([class*="o_list_record_selector"]):eq('+column_index+')';
                    export_columns_names.push(view.$el.find(column_header_selector)[0].textContent);
                }
                column_index ++;
            });
            $.blockUI();
            if (children) {
                // Getting the data from the dom
                view.$el.find('.o_list_table  > tbody > tr.o_data_row:has(.o_list_record_selector input:checkbox:checked)')
                    .each(function () {
                        var $row = $(this);
                        var export_row = [];
                        $.each(export_columns_keys, function () {
                            var $cell = $row.find('td.o_data_cell:eq('+this+')');
                            var text = $cell.text().trim();
                            var $cellcheckbox = $cell.find('.o_checkbox input:checkbox');
                            if ($cellcheckbox.length) {
                                export_row.push(
                                    $cellcheckbox.is(":checked")
                                    ? _t("True") : _t("False")
                                );
                            }
                            else {
                                var text = $cell.text().trim();
                                var is_number = (
                                    $cell.hasClass('o_list_number') &&
                                    !$cell.hasClass('o_float_time_cell')
                                );
                                if (is_number) {
                                    export_row.push(
                                        text
                                        .split(_t.database.parameters.thousands_sep)
                                        .join("")
                                        .replace(_t.database.parameters.decimal_point, ".")
                                    );
                                } else {
                                    export_row.push(text);
                                }
                            }
                        });
                        export_rows.push(export_row);
                    });
            }

            return {
                "header":export_columns_names,
                "rows": export_rows
            }
        }
    });
});
