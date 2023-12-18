/**************************************************
        01. Search in Header
        02. Page Scroll up
        03. Theme Wishlist
        04. Shop Events
        05. cart Popover
        06. Theme layout
        07. Compare short name
**************************************************/
odoo.define('theme_clarico_vega.theme_script', function(require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');
    var Widget = require('web.Widget');
    var core = require('web.core');
    var _t = core._t
    var ajax = require('web.ajax');
    var config = require('web.config');
    var sale = new sAnimations.registry.WebsiteSale();

    //------------------------------------------
    // 01. Search in Header
    //------------------------------------------
    sAnimations.registry.themeSearch = sAnimations.Class.extend({
        selector: '#wrapwrap',
        read_events: {
            'click .te_srch_icon': '_onSearchClickOpen',
            'click .te_srch_close': '_onSearchClickClose',
            'click .mycart-popover .js_delete_product': '_onClickDeleteProduct',
        },
        start: function() {
            this.scrollbarCallbacks();
            $('.variant_attribute  .list-inline-item').find('.active').parent().addClass('active_li');
            $( ".list-inline-item .css_attribute_color" ).change(function(ev) {
                var $parent = $(ev.target).closest('.js_product');
                $parent.find('.css_attribute_color').parent('.list-inline-item').removeClass("active_li");
                $parent.find('.css_attribute_color').filter(':has(input:checked)').parent('.list-inline-item').addClass("active_li");
            });
        },
        /* Custom jquery scrollbar*/
        scrollbarCallbacks: function(){
            $('.te_attr_title').click(function(ev) {
                var ul_height = $(this).siblings("ul").height();
                if(ul_height > 141)
                {
                    $(this).siblings("ul").mCustomScrollbar({
                        axis:"y",
                        theme:"dark-thin",
                        alwaysShowScrollbar: 1,
                    });
                }
            });
        },
        _onSearchClickOpen: function(ev) {
            var self = ev.currentTarget;
            //style1
            if ($(".te_header_1_right").length) {
                $(".te_search_popover").addClass("visible");
                $(self).hide()
                $(".te_srch_close").show();
                setTimeout(function(){
                    $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                }, 500);
            }
            //style 2 and 3 resp view
            if ($(window).width() < 768) {
                if ($(".te_header_style_2_right").length || $(".te_header_style_3_inner_first").length) {
                    $(".te_search_popover").addClass("visible");
                    $(self).hide()
                    $(".te_srch_close").show();
                    setTimeout(function(){
                        $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                    }, 500);
                }
            }
            //style4
            if ($(".te_header_4_search").length) {
                $(".te_search_4_form").addClass("open_search");
                var $h_menu = $("#oe_main_menu_navbar").height();
                $(".te_search_4_form").css({
                    top: $h_menu + 0
                });
                setTimeout(function(){
                    $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                }, 500);
            }
             //style5
            if ($("header.o_header_is_scrolled .te_searchform__popup").length) {
                $('header.o_header_is_scrolled').css({'transform':'none','transition':'none'});
                $(".te_searchform__popup").addClass("open");
                $(".te_srch_close").show();
                setTimeout(function(){
                    $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                }, 500);
            }
            else{
                if ($(".te_searchform__popup").length) {
                    $(".te_searchform__popup").addClass("open");
                    $(".te_srch_close").show();
                    setTimeout(function(){
                        $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                    }, 500);
                }
            }
            //style7 and style9
            if ($(".te_header_7_srch_icon, .te_header_9_srch_icon").length) {
                if($(window).width() <= 767){
                    if($('.te_header_9_srch_icon').length){
                        $('.navbar-expand-md .navbar-toggler, .te_header_9_srch_icon, header .navbar-brand').hide();
                    }
                    else{
                        $(".navbar-expand-md .navbar-toggler").hide();
                    }
                }
                if ($(window).width() <= 991) {
                    if($('.te_header_9_srch_icon').length){
                        $(".te_header_9_srch_icon, div#top_menu_collapse .navbar-nav, div#top_menu_collapse_clone .navbar-nav").hide();
                    }
                    else{
                        $(".navbar-expand-md .navbar-nav, .te_header_right_icon, .te_header_navbar label.label_checkbox, div#top_menu_collapse .navbar-nav").hide();
                    }
                }
                $(".te_header_search input").css("width","100%");
                setTimeout(function(){
                    if ($(window).width() >= 992) {
                        $(".te_header_right_icon").hide();
                        $(".navbar-expand-md .navbar-nav").hide();
                    }
                    $(".te_header_search_popover").fadeIn(200);
                }, 500);
                setTimeout(function(){
                    $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                }, 500);
            }
            //style8
            if ($(".te_srch_icon_mobile_header").length) {
                setTimeout(function(){
                    $('.o_wsale_products_searchbar_form input[name="search"]').focus();
                }, 500);
                if ($(window).width() <= 991) {
                    $(".te_header_8_search").addClass("active");
                    $(".navbar-expand-md .navbar-nav").hide();
                    $(self).hide()
                    $(".te_srch_close").show();
                }
            }
        },
        _onSearchClickClose: function(ev) {
            var self = ev.currentTarget;
            //style1
            if ($(".te_header_1_right").length) {
                $(".te_search_popover").removeClass("visible");
                $(self).hide();
                $(".te_srch_icon").show();
            }
            //style 2 and 3 resp view
            if ($(window).width() < 768) {
                if ($(".te_header_style_2_right").length || $(".te_header_style_3_inner_first").length) {
                    $(".te_search_popover").removeClass("visible");
                    $(self).hide();
                    $(".te_srch_icon").show();
                }
            }
            //style4
            if ($(".te_header_4_search").length) {
                $(".te_search_4_form").removeClass("open_search");
                $(".te_search_icon_4").css("display", "inline-block");
            }
            //style5
            if ($(".te_searchform__popup").length) {
                $(".te_searchform__popup").removeClass("open");
                $(".te_srch_icon").show();
            }
            //style7 and style9
            if ($(".te_header_7_srch_icon, .te_header_9_srch_icon").length) {
                $(".te_header_right_icon, .navbar-expand-md .navbar-nav").show();
                $(".te_header_search_popover").hide();
                $(".te_header_search_popover input").css("width", "0%");
                $(".te_srch_icon").css("display", "flex");
                if($(window).width() <= 767){
                    if($('.te_header_9_srch_icon').length){
                        $('.navbar-expand-md .navbar-toggler, .te_header_11_srch_icon, header .navbar-brand').fadeIn(300);
                    }
                    else{
                        $(".navbar-expand-md .navbar-toggler").fadeIn(300);
                    }
                }
                if ($(window).width() <= 991) {
                    if($('.te_header_9_srch_icon').length){
                        $("div#top_menu_collapse .navbar-nav, div#top_menu_collapse_clone .navbar-nav").fadeIn(400);
                    }
                    else{
                        $(".te_header_right_icon, .navbar-expand-md .navbar-nav, .te_header_navbar label.label_checkbox").fadeIn(400);
                    }
                }
            }
            //style8
            if ($(".te_srch_icon_mobile_header").length) {
                if ($(window).width() <= 991) {
                    $(".te_header_8_search").removeClass("active");
                    $(".navbar-expand-md .navbar-nav, .te_srch_icon").show();
                    $(".te_srch_close").hide();
                }
            }
        },
    });

    //------------------------------------------
    // 02. Page Scroll up
    //------------------------------------------
    sAnimations.registry.themeLayout = sAnimations.Class.extend({
        selector: '.o_footer',
        read_events: {
            'click .scrollup-div': '_onClickAnimate',
        },
        _onClickAnimate: function(ev) {
            $("html, body").animate({
                scrollTop: 0
            }, 1000);
        },
    });
    //------------------------------------------
    // 03. Theme Wishlist
    //------------------------------------------
    sAnimations.registry.themeWishlist = sAnimations.Class.extend({
        selector: '#o_comparelist_table',
        read_events: {
            'click .o_wish_rm': '_onRemoveClick',
            'click .o_wish_add' : '_onAddToCartClick',
        },
        _onAddToCartClick: function(ev) {
            if($('body').hasClass('editor_enable')){
                ev.stopImmediatePropagation();
                ev.preventDefault();
            }
        },
        _onRemoveClick: function(ev) {
            if($('body').hasClass('editor_enable')){
                ev.stopImmediatePropagation();
                ev.preventDefault();
            } else{
                var ajax = require('web.ajax');
                var tr = $(ev.currentTarget).parents('tr');
                var wish = tr.data('wish-id');
                var route = '/shop/wishlist/remove/' + wish;
                ajax.jsonRpc(route, 'call', {
                    'wish': wish
                }).then(function(data) {
                    $(tr).hide();
                    if ($('.t_wish_table tr:visible').length == 0) {
                        window.location.href = '/shop';
                    }
                })
            }
        },

    });

    //------------------------------------------
    // 04. Shop Events
    //------------------------------------------
    sAnimations.registry.themeEvent = sAnimations.Class.extend({
        selector: '.oe_website_sale',
        read_events: {
            'click .te_attr_title': '_onAttribSection',
            'click .te_shop_filter_resp': '_onRespFilter',
            'click .te_filter_close': '_onFilterClose',
            'click .te_color-name':'_oncolorattr',
            'click .te_show_category':'_onShowCategBtnResp',
            'click .te_show_option':'_onShowOptionBtnResp',
            'click .te_ctg_h4': '_onCategorySection',
        },
        start: function() {
            $("img.lazyload").lazyload();
            this.onShowClearVariant();
            this.onSelectAttribute();
        },
        onShowClearVariant: function() {
            $("form.js_attributes .te_shop_attr_ul input:checked, form.js_attributes .te_shop_attr_ul select").each(function() {
                var self = $(this);
                var type = ($(self).prop("tagName"));
                var type_value;
                var attr_value;
                var attr_value_str;
                var attr_name;
                var target_select;
                var curr_parent;
                var target_select = self.parents("li.nav-item").find("a.te_clear_all_variant");
                if ($(type).is("input")) {
                    type_value = this.value;
                    attr_value = $(this).parent("label").find("span").html();
                    if (attr_value) {
                        attr_value_str = attr_value.toLowerCase();
                        attr_value_str = attr_value_str.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value_str = attr_value_str.replace(/\s+/g, "-");
                    }
                    curr_parent = self.parents("ul");
                    target_select = curr_parent.parent("li.nav-item").find("a.te_clear_all_variant");
                    attr_name = curr_parent.parent("li.nav-item").find("a.te_clear_all_variant").attr('attribute-name');
                    if (self.parent("label").hasClass("css_attribute_color")) {
                        attr_value = self.parent("label").siblings(".te_color-name").html();
                        if(attr_value) {
                            attr_value_str = attr_value.toLowerCase();
                            attr_value_str = attr_value_str.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                            attr_value_str = attr_value_str.replace(/\s+/g, "-");
                        }
                    }
                    var first_li = self.closest("ul").find("li").first();
                    var selected_li = self.closest("li.nav-item");
                    $(first_li).before(selected_li);
                    if (!curr_parent.hasClass("open_ul")) {
                        curr_parent.parent("li.nav-item").find('.te_attr_title').click();
                    }
                } else if ($(type).is("select")) {
                    type_value = self.find("option:selected").val();
                    attr_value = self.find("option:selected").html();
                    if(attr_value) {
                        attr_value_str = attr_value.toLowerCase();
                        attr_value_str = attr_value_str.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value_str = attr_value_str.replace(/\s+/g, "-");
                    }
                    attr_name = self.find("option:selected").parents("li.nav-item").find('a.te_clear_all_variant').attr('attribute-name');
                    target_select = self.parents("li.nav-item").find("a.te_clear_all_variant");
                }
                if (type_value) {
                    $(".te_clear_all_form_selection").css("display", "inline-block");
                    $(".te_view_all_filter_div").css("display", "inline-block");
                    if (target_select) {
                    var temp_attr_value = attr_value.toString().split('(');
                    var cust_attr_value = '';
                        switch(parseInt(temp_attr_value.length)) {
                          case 4:
                            cust_attr_value += temp_attr_value[0] +' ('+ temp_attr_value[1] +' ('+temp_attr_value[2];
                            break;
                          case 3:
                            cust_attr_value += temp_attr_value[0] +'('+ temp_attr_value[1];
                            break;
                          default:
                            cust_attr_value += temp_attr_value[0];
                        }
                        $(".te_view_all_filter_inner").append("<div class='attribute'>" + cust_attr_value + "<a data-id='" + type_value + "' class='te_clear_attr_a "+attr_name+" "+attr_value_str+" '>x</a></div>");
                    }
                }
            });
            $("form.js_attributes input:checked, form.js_attributes select").each(function() {
                var self = $(this);
                var type = ($(self).prop("tagName"));
                var target_select = self.parents("li.nav-item").find("a.te_clear_all_variant");
                var type_value;
                if ($(type).is("input")) {
                    type_value = this.value;
                    var first_li = self.closest("ul").find("li").first();
                    var selected_li = self.closest("li.nav-item");
                    $(first_li).before(selected_li);
                } else if ($(type).is("select")) {
                    type_value = self.find("option:selected").val();
                }
                if (type_value) {
                    target_select.css("display", "inline-block");
                }
            });
        },

        // If any attribute are selected then automatically this section is Expand(only for type select)
        onSelectAttribute: function(ev){
            $("form.js_attributes .te_shop_attr_ul input:checked, form.js_attributes .te_shop_attr_ul select").each(function() {
                var self = $(this);
                var type = ($(self).prop("tagName"));
                var type_value;
                if ($(type).is("select")) {
                    type_value = self.find("option:selected").val();
                }
                if (type_value) {
                    self.addClass("open_select").css('display','inline-block');
                    self.siblings('.te_attr_title').addClass('te_fa-minus');
                }
            });
        },
        _onClearAttribInd: function(ev) {
            var self = ev.currentTarget;
            var id = $(self).attr("data-id");
            if (id) {
                $("form.js_attributes option:selected[value=" + id + "]").remove();
                $("form.js_attributes").find("input[value=" + id + "]").removeAttr("checked");
            }
            ajaxorformload(ev);
        },
        _onClearAttribAll: function(ev) {
            $("form.js_attributes option:selected").remove();
            $("form.js_attributes").find("input:checked").removeAttr("checked");
            ajaxorformload(ev);
        },
        _onClearAttribDiv: function(ev) {
            var self = ev.currentTarget;
            var curent_div = $(self).parents("li.nav-item");
            var curr_divinput = $(curent_div).find("input:checked");
            var curr_divselect = $(curent_div).find("option:selected");
            _.each(curr_divselect, function(ev) {
                $(curr_divselect).remove();
            });
            _.each(curr_divinput, function(ev) {
                $(curr_divinput).removeAttr("checked");
            });
            ajaxorformload(ev);
        },
        _onCategorySection: function(){
            var ctg_ul = $('.te_ctg_h4').siblings('.te_shop_ctg_list');
             if (ctg_ul.hasClass("open_ul")) {
                ctg_ul.removeClass("open_ul");
                ctg_ul.siblings(".te_ctg_h4").addClass('te_fa-plus');
                ctg_ul.toggle('slow');
            }
            else{
                ctg_ul.addClass("open_ul");
                ctg_ul.siblings(".te_ctg_h4").removeClass('te_fa-plus');
                ctg_ul.toggle('slow');
            }
        },
        _onAttribSection: function(ev) {
            var self = ev.currentTarget;
            var main_li = $(self).parents("li.nav-item");
            var ul_H = main_li.find("ul").height();
            if (main_li.find("select").length == 1) {
                $("select.form-control.open_select").css('display','block');
                var main_select = main_li.find("select");
                if (main_select.hasClass("open_select")) {
                    main_select.removeClass("open_select");
                    main_select.parent(".nav-item").find(".te_attr_title").removeClass('te_fa-minus');
                    main_select.toggle('slow');
                }
                else {
                    main_select.addClass("open_select");
                    main_select.parent(".nav-item").find(".te_attr_title").addClass('te_fa-minus');
                    main_select.toggle('slow');
                }
            }
            var main_ul = main_li.find("ul");

            if (main_ul.hasClass("open_ul")) {
                main_ul.removeClass("open_ul");
                $(main_ul).parent('.nav-item').find(".te_attr_title").removeClass('te_fa-minus');
                main_ul.toggle('slow');

            } else {
                main_ul.addClass("open_ul");
                $(main_ul).parent('.nav-item').find(".te_attr_title").addClass('te_fa-minus');
                main_ul.toggle('slow');
            }
        },
        _onRespFilter: function(ev) {
            $("#products_grid_before").addClass("te_filter_slide");
            $("#products_grid_before").mCustomScrollbar({
               axis:"y",
               theme:"dark-thin",
               alwaysShowScrollbar: 1
            });
            $("#wrapwrap").addClass("wrapwrap_trans");
            $('body').css("overflow-x", "hidden");
            $("#wsale_products_attributes_collapse").addClass("show");
            if($('#products_grid_before').find('#wsale_products_attributes_collapse').length < 1) {
                $("#wsale_products_categories_collapse").addClass("show");
                if($("#wsale_products_categories_collapse .show")){
                    $(".te_show_category").find("i").addClass('fa-chevron-down').removeClass('fa-chevron-right');
                }
            }
            if($("#wsale_products_attributes_collapse .show")){
                $(".te_show_option").find("i").addClass('fa-chevron-down').removeClass('fa-chevron-right');
            }
        },
        _onFilterClose: function(ev) {
            $("#products_grid_before").removeClass("te_filter_slide")
            $("#wrapwrap").removeClass("wrapwrap_trans");
        },
        _oncolorattr: function(ev){
            var self=ev.currentTarget;
             //$(self).parents("li.color-with-name-divmaxW").find("input").click();
             $(self).parent().find("input").click();
        },
         _onShowCategBtnResp: function(ev){
            $(".te_show_category").find("i").toggleClass('fa-chevron-right fa-chevron-down');
        },
        _onShowOptionBtnResp: function(ev){
            $(".te_show_option").find("i").toggleClass('fa-chevron-down fa-chevron-right');
        },
    });

    sAnimations.registry.StickyFilter = sAnimations.Animation.extend({
        selector: '#wrapwrap',
         effects: [{
            startEvents: 'scroll',
            update: '_stickyFilter',
        }],
        init: function () {
            this._super(...arguments);
            this.header_height = 20;
            if($('header#top').length && !$('header').hasClass('o_header_sidebar')) {
                if($('header nav').hasClass('te_header_navbar')) {
                    this.header_height = $('header nav').height() + 20;
                } else {
                    this.header_height = $('header').height() + 20;
                }
            }
            if($( window ).width() < 992) {
                this.header_height = $('header').height() + 50;
                var $stickyFilter = $('.te_shop_filter_resp');
                if (!!$stickyFilter.offset()) {
                    this.stickyTop = $('div.te_shop_filter_resp').offset().top;
                    this.footerTop = $('footer').offset().top - 300;
                }
            }
        },
        _stickyFilter: function (scroll) {
            if($( window ).width() > 991) {
                if($('.o_wsale_products_main_row').hasClass('enabled')){
                    var $stickySidebar = $('.te_product_sticky_sidebar');
                    if (!!$stickySidebar.offset()) {
                        var sidebar_height = $stickySidebar.innerHeight();
                        var stickyTop = $stickySidebar.offset().top;
                        var windowHeight = $( window ).height() - 200;
                        var quickView = $('.te_quick_filter_dropdown_menu').is(":visible");
                        if(!quickView) {
                            if (stickyTop < scroll + this.header_height) {
                                $stickySidebar.css({ position: 'sticky', top: this.header_height, height: windowHeight});
                                $stickySidebar.addClass('sticky-media');
                                $("#products_grid_before").mCustomScrollbar({
                                   axis:"y",
                                   theme:"dark-thin",
                                   alwaysShowScrollbar: 1
                                });
                            } else {
                                $stickySidebar.css({ position: 'unset', top: 'initial', height: 'auto'});
                                $stickySidebar.removeClass('sticky-media');
                                $("#products_grid_before").mCustomScrollbar("destroy");
                            }
                        } else {
                            $stickySidebar.css({ position: 'unset', top: 'initial', height: 'auto'});
                            $stickySidebar.removeClass('sticky-media');
                            $("#products_grid_before").mCustomScrollbar("destroy");
                        }
                    }
                }
            }
            if($( window ).width() < 992) {
                var $stickyFilter = $('.te_shop_filter_resp');
                if (!!$stickyFilter.offset()) {
                    //var stickyTop = $('div.te_shop_filter_resp').offset().top;
                    /*var header_height = 20;
                    if($('header#top').length && !$('header').hasClass('o_header_sidebar')) {
                        header_height = $('header').height() + 10;
                    }*/
                    //var footerTop = $('footer').offset().top - 300;
                    if ((this.footerTop > scroll + this.header_height) && (this.stickyTop < scroll)) {
                        $('.filters-title-ept').hide();
                        $('.te_shop_filter_resp').css({top: this.header_height});
                        $('.te_shop_filter_resp').addClass('sticky-filter');
                    } else {
                        $('.filters-title-ept').show();
                        $('.te_shop_filter_resp').css({top: 'initial'});
                        $('.te_shop_filter_resp').removeClass('sticky-filter');
                    }
                }
            }
        },
    });

    sAnimations.registry.StickyGallery = sAnimations.Animation.extend({
        selector: '#wrapwrap',
         effects: [{
            startEvents: 'scroll',
            update: '_stickyGallery',
        }],
        init: function () {
            this._super(...arguments);
            this.$sticky = $('#product_detail .row.te_row_main > .col-lg-6:first-child');
            if ($(this.$sticky).length) {
                this.stickyTop = this.$sticky.offset().top;
            }
            this.header_height = 20;
            if($('header#top').length && !$('header').hasClass('o_header_sidebar')) {
                if($('header nav').hasClass('te_header_navbar')) {
                    this.header_height = $('header nav').height() + 20;
                } else {
                    this.header_height = $('header').height() + 20;
                }
            }
        },
        _stickyGallery: function (scroll) {
            if($( window ).width() > 991) {
                if (!!this.$sticky.offset() && this.$sticky) {
                    if (this.stickyTop < scroll+this.header_height+this.header_height) {
                        this.$sticky.css({ position: 'sticky', top: this.header_height });
                        this.$sticky.addClass('sticky-media');
                    } else {
                        this.$sticky.css({ position: 'relative', top: 'initial'});
                        this.$sticky.removeClass('sticky-media');
                    }
                }
            }
            // Sticky add to cart bar
            if($('.product_details_sticky').length){
                if($('div#product_details a#add_to_cart').length){
                    var getPriceHtml = $('div#product_details .product_price').html();
                    var stickHeight = $('.product_details_sticky .prod_details_sticky_div').height();
                    var cookie_height = 0;
                    if($('.o_cookies_discrete .s_popup_size_full').length) {
                       cookie_height = $('.s_popup_size_full .modal-content').height()
                       stickHeight = cookie_height + stickHeight
                    }
                    var fixIconHeight8 = $('.te_header_icon_right').height();
                    var fixIconHeight9 = $('.head_9_rest_icons').height();
                    if (scroll > $('div#product_details a#add_to_cart').offset().top) {
                        $('footer#bottom').css('padding-bottom', stickHeight+'px'); /* Add below spaces on the footer */
                        if ($(window).width() < 992){
                            if($('.fixed-header-8-bar').length){
                                $('div#wrapwrap .product_details_sticky').css('bottom',fixIconHeight8+'px').fadeIn();
                            }
                            else{
                                $('#product_detail').find('.o_product_feature_panel').css('bottom',stickHeight+'px').fadeIn();
                            }

                            if($('.fixed-header-top-bar').length){
                                $('div#wrapwrap .product_details_sticky').css('bottom',fixIconHeight9+'px').fadeIn();
                            }
                            else{
                                $('#product_detail').find('.o_product_feature_panel').css('bottom',stickHeight+'px').fadeIn();
                            }
                        }
                        else{
                            $('div#wrapwrap .product_details_sticky').css('bottom', cookie_height+'px');
                            $('div#wrapwrap .product_details_sticky').fadeIn();
                        }

                        if ($(window).width() >= 992){
                            $('#product_detail').find('.o_product_feature_panel').css('bottom',stickHeight+'px').fadeIn();
                        }
                        else
                        {
                            $('div#wrapwrap .product_details_sticky').css('bottom', cookie_height+'px');
                            $('div#wrapwrap .product_details_sticky').fadeIn();
                            if($('.fixed-header-8-bar').length){
                                $('#product_detail').find('.o_product_feature_panel').css('bottom',(stickHeight + fixIconHeight8)+'px').fadeIn();
                            }
                            else{
                                $('#product_detail').find('.o_product_feature_panel').css('bottom', fixIconHeight8+'px').fadeIn();
                            }
                            if($('.fixed-header-top-bar').length){
                                $('#product_detail').find('.o_product_feature_panel').css('bottom',(stickHeight + fixIconHeight9)+'px').fadeIn();
                            }
                            else{
                                $('#product_detail').find('.o_product_feature_panel').css('bottom', fixIconHeight9+'px').fadeIn();
                            }
                        }

                        /* Display prices on add to cart sticky*/
                        if( $( ".js_product.js_main_product" ).hasClass( "css_not_available" )){
                           $('div#wrapwrap .prod_price').html('');
                           //$(".product_details_sticky .prod_add_cart #add_to_cart, .product_details_sticky .prod_add_cart #buy_now").addClass('disabled');
                        }
                        else{
                            $('div#wrapwrap .prod_price').html(getPriceHtml);
                            //$(".product_details_sticky .prod_add_cart #add_to_cart, .product_details_sticky .prod_add_cart #buy_now").removeClass('disabled');
                        }
                       
                        $(".product_details_sticky .prod_add_cart #add_to_cart").click(function(e){
                            if($('body').hasClass('editor_enable')){
                                e.stopPropagation();
                            }
                            else{
                                $("div#product_details .js_product.js_main_product #add_to_cart").trigger( "click" );
                                return false;
                            }
                        });
                        $(".product_details_sticky .prod_add_cart #buy_now").click(function(e){
                            if($('body').hasClass('editor_enable')){
                                e.stopPropagation();
                            }
                            else{
                                $("div#product_details .js_product.js_main_product #buy_now").trigger( "click" );
                                return false;
                            }
                        });
                    } else {
                        if ($(window).width() < 992){
                            if($('.fixed-header-8-bar').length){
                                $('#product_detail').find('.o_product_feature_panel').css('bottom', fixIconHeight8+'px');
                            }
                            else{
                                $('#product_detail').find('.o_product_feature_panel').css('bottom', '0px');
                            }

                            if($('.fixed-header-top-bar').length){
                                $('#product_detail').find('.o_product_feature_panel').css('bottom', fixIconHeight9+'px');
                            }
                            else{
                                $('#product_detail').find('.o_product_feature_panel').css('bottom', '0px');
                            }
                        }
                        else{
                            $('#product_detail').find('.o_product_feature_panel').css('bottom', '0px');
                        }
                        $('div#wrapwrap .product_details_sticky').css('bottom', cookie_height+'px');
                        $('div#wrapwrap .product_details_sticky').fadeOut();
                    }
                }
            }
            var HHeight = $('header#top').height();
            if (scroll >= 72) {
                $('body').addClass('fixed-header-bar');
            } else {
                $('body').removeClass('fixed-header-bar');
            }
            /* For Header 11 scroll top*/
            if (scroll >= 44) {
                $('body').addClass('fixed-header-top-bar');
            } else {
                $('body').removeClass('fixed-header-top-bar');
            }
            if($('#wrapwrap').hasClass('homepage')){
                $('#wrapwrap').addClass('header_top_overlay');
                $('#wrapwrap:not(.header_top_overlay)').css("margin-top", HHeight);
                if (scroll >= 196) {
                    $('body').addClass('fixed-header');
                } else {
                    $('body').removeClass('fixed-header');
                }
            }
            if ($('.te_header_navbar_8').length) {
                var headerHeight = $('.te_header_navbar_8').height();
                if (scroll > headerHeight) {
                    $('body').addClass('fixed-header-8-bar');
                    $('.te_header_navbar_8').addClass('start-sticky');
                } else {
                    $('body').removeClass('fixed-header-8-bar');
                    $('.te_header_navbar_8').removeClass('start-sticky');
                }
            }
            /* Prevent search bar while scrolling header */
            if($('.navbar-light.navbar-expand-lg').length){
                /* odoo default header search */
                if ($("header .te_searchform__popup.open").length) {
                    $('header').css({'transform':'none','transition':'none'});
                }
            }
            if ($('.te_header_navbar').length) {
                var headerHeight = $('.te_header_navbar').height();
                if ( scroll > headerHeight ) {
                    if($('header').hasClass('o_header_affixed') && !$("header.o_header_affixed").hasClass("o_header_is_scrolled")){
                      if ($(".te_header_1_right").length) {
                          $(".te_search_popover").removeClass("visible");
                          $('.te_srch_close').hide();
                          $(".te_srch_icon").show();
                      }
                      if ($(window).width() < 768) {
                         if ($(".te_header_style_2_right").length || $(".te_header_style_3_inner_first").length) {
                             $(".te_search_popover").removeClass("visible");
                             $('.te_srch_close').hide();
                             $(".te_srch_icon").show();
                         }
                      }
                      if ($(".te_header_4_search").length) {
                          $(".te_search_4_form").removeClass("open_search");
                          $(".te_search_icon_4").css("display", "inline-block");
                      }
                      if($(".te_searchform__popup").length){
                         $(".te_searchform__popup").removeClass("open");
                         $(".te_srch_icon").show();
                      }
                      $(".search_btn_close").trigger('click');
                      $('.o_wsale_products_searchbar_form .dropdown-menu.show').removeClass('show');
                    }
                }
            }
        },
    });

    /*---- Shop Functions ------*/
    //function for ajax form load
    function ajaxorformload(ev) {
        var ajax_load = $(".ajax_loading").val();
        if (ajax_load == 'True') {
            ajaxform(ev);
        } else {
            $("form.js_attributes input,form.js_attributes select").closest("form").submit();
        }
    }
    sAnimations.registry.WebsiteSale.include({
        /*
         Adds the stock checking to the regular _onChangeCombination method
        @override
        */
        _updateProductImage: function (){

        this._super.apply(this, arguments);
        },
    });




    /** Product image gallery for product page */
    sAnimations.registry.product_detail = sAnimations.Class.extend({
        selector: "#product_detail",
        productGallery: function(){
            /* Remove compare duplicate class div*/
            setTimeout(function(){
                if($('.quick_view_modal').length){
                    $('.modal-body.oe_website_sale > .o_product_feature_panel').remove();
                }
            }, 500);
            var owl_rtl = false;
            if ($('#wrapwrap').hasClass('o_rtl')) {
                owl_rtl = true;
            }
            var slider = $('#mainSlider .owl-carousel');
            var thumbnailSlider = $('#thumbnailSlider .owl-carousel');
            $('#thumbnailSlider').show();
            var duration = 400;
            var img_length = $('#len-ept-image').val();

            if($('#len-ept-image').val() < 2) {
                $('#mainSlider').addClass('mainslider-full');
            }

            if($('#len-ept-image').val() > 5) {
                var slider_length = ($('#len-ept-image').val() - 2);
                var thumb_length =  $('#len-ept-image').val() - ($('#len-ept-image').val() - 5);
            } else {
                var slider_length = 0;
                var thumb_length = 0;
            }
            slider.owlCarousel({
                nav:true,
                rtl: owl_rtl,
                navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
                items:1,
                loop: $('#len-ept-image').val() > 1 ? true : false,
                rewind: true,
            }).on('changed.owl.carousel', function (event) {
                // On change of main item to trigger thumbnail item
                let currentIndex = event.item.index + slider_length;
                thumbnailSlider.trigger('to.owl.carousel', [currentIndex, duration, true]);
                if($('#len-ept-image').val() <= 5) {
                    thumbnailSlider.find('.owl-item').removeClass('center');
                    thumbnailSlider.find('.owl-item').eq(currentIndex - 2).addClass('center');
                }
                $("#mainSlider img").each(function() {
                    $(this).attr('loading','');
                })
            }).on('refreshed.owl.carousel', function () {
                if($('#id_lazyload').length) {
                    $("img.lazyload").lazyload();
                }
            });;

                // carousel function for thumbnail slider
            thumbnailSlider.owlCarousel({
                loop: $('#len-ept-image').val() > 5 ? true : false,
                center: $('#len-ept-image').val() > 5 ? true : false,
                margin: 4,
                rtl: owl_rtl,
                nav:true,
                navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
                responsive:{
                    0:{
                        items:5,
                    },
                    600:{
                        items:5
                    },
                    1000:{
                        items:5
                    }
                }
            }).on('click', '.owl-item', function () {
                // On click of thumbnail items to trigger same main item
                let currentIndex = $(this).find('li').attr('data-slide-to');
                slider.trigger('to.owl.carousel', [currentIndex, duration, true]);
            }).on('refreshed.owl.carousel', function () {
                if($('#len-ept-image').val() <= 5) {
                    $('#thumbnailSlider .owl-carousel .owl-item').first().addClass('center');
                }
                if($('#id_lazyload').length) {
                    $("img.lazyload").lazyload();
                }
            });

            var thumb_width = $('#thumbnailSlider').find('.owl-item').width();
            $('#thumbnailSlider').find('.owl-item').height(thumb_width);
            if ($(window).width() > 767) {
                if($('.o_rtl').length == 1){
                    $('#thumbnailSlider').find('.owl-carousel').css('right', (0-(thumb_width*2)));
                }
                $('#thumbnailSlider').find('.owl-carousel').css('left', (0-(thumb_width*2)));
                $('#thumbnailSlider').find('.owl-carousel').css('top', (thumb_width*2)+26);
            }
        },
    });


    //------------------------------------------
    // 06. Theme layout
    //------------------------------------------

    $(document).ready(function($) {
        $(document).on('click',".te_quick_filter_dropdown",function(ev) {
            $(".te_quick_filter_dropdown_menu .te_quick_filter_ul >li").each(function() {
                var ul_H = $(this).find("ul").height();
                if (ul_H >= 177) {

                    $(this).find("ul").mCustomScrollbar({
                        axis:"y",
                        theme:"dark-thin",
                        alwaysShowScrollbar: 1,
                    });
                }
            });
        });
        $(document).on('click',".quick_close",function(ev) {
            $('.modal-backdrop').remove();
            $('body').css("padding-right","0");
        });
        $(document).mouseup(function(ev)
		{
		    var container = $(".quick_view_modal");
		    if (!container.is(ev.target) && container.has(ev.target).length === 0)
		    {
		        if($('#quick_view_model_shop').hasClass("show")){
		            $('.modal-backdrop').remove();
                    $('body').css("padding-right","0");
                }
		    }
		});
        if($(document).find('.te_recently_viewed'))
        {
            var r_name = $("#te_rect_cnt").text();
            $('.te_recently_viewed').find('h6').each(function(){

                $(document).find('h6.card-title').addClass("te_rect_name")
                if(r_name == 2)
                {
                    $('h6.card-title').addClass('te_2_line');
                }
                if(r_name == 3)
                {
                    $('h6.card-title').addClass('te_3_line');
                }
            });
        }
        if($('.o_comparelist_button')) {
            setTimeout(function(){
                $('.o_comparelist_button').find('a').addClass('te_theme_button');
            }, 700);
        }
        setTimeout(function(){
            $(".o_portal_chatter_composer_form").find("button").addClass("te_theme_button");
            $(".js_subscribe_btn").addClass("te_theme_button");
            $(".o_portal_sign_submit").addClass("te_theme_button");
        }, 1000);

        //extra menu dropdown
        $('.o_extra_menu_items .dropdown-menu').css("display", "none")
        $('li.o_extra_menu_items .dropdown').click(function(event) {
            event.stopImmediatePropagation();
            $(this).find(".dropdown-menu").slideToggle();
        });
        //Header top when transparent header
        var header_before_height = $(".te_header_before_overlay").outerHeight();
        if ($("body").find(".o_header_overlay").length > 0) {
            $("header:not(.o_header_affix)").addClass("transparent_top")
            $(".transparent_top").css("top", header_before_height);
            $(".o_header_affix.affix").removeClass("transparent_top")
        }
        //Category mega menu
//        if($('.te_dynamic_ept'))
//		{
//		    setTimeout(function(){
//			$('.te_dynamic_ept >.dropdown-toggle').removeAttr('data-toggle');
//			$('.te_dynamic_ept >.dropdown-toggle').removeAttr('aria-expanded');
//			},100);
//		}
		var li_count = $("#top_menu_collapse >#top_menu >li").length;
        var li_pos = $('.te_dynamic_ept').index()+1;
        $("#custom_menu li").each(function() {
            var has_ctg = $(this).find("ul.t_custom_subctg").length > 0
            if (has_ctg) {
                $(this).append("<span class='ctg_arrow fa fa-angle-right' />")
                var ul_index = 0;
                if(li_pos > li_count/2)
                {
                    $(this).children("#custom_recursive").css({
                        "transform": "translateX(-20px)",
                    });
                }
                if($(document).find('#wrapwrap').hasClass('o_rtl')){
                    if(li_pos > li_count/2)
                    {
                        $(this).children("#custom_recursive").css({
                            "transform": "translateX(20px)",
                        });
                    }
                    else
                    {
                        $(this).children("#custom_recursive").css({
                            "transform": "translateX(-20px)",
                        });
                    }
                }
                if ($(window).width() > 1200) {
                    $(document).on('mouseenter',"#custom_menu_li",function(ev) {
                        var li_place = $(this).position().top;
                        $(this).children("#custom_recursive").css("top", li_place);
                        var self = $(this).children("#custom_recursive");
                        if($(this).children("#custom_recursive").length > 0)
                        {
                            ul_index = $(self).parents("ul").length == 0 ? $(self).parents("ul").length : ul_index + 1;
                            $(self).css({
                                    "opacity":"1",
                                    "visibility": "visible",
                                    "transform": "translateX(-10px)",
                                    "transition": "all 0.2s",
                            });
                            if(li_pos > li_count/2) {
                                $(self).css({
                                    "right": "100%",
                                    "left": "auto",
                                    "transform": "translateX(10px)",
                                });
                            }
                            if($(document).find('#wrapwrap').hasClass('o_rtl')){
                                $(self).css({
                                    "transform": "translateX(12px)",
                                });
                                if(li_pos > li_count/2) {
                                    $(self).css({
                                        "left": "100%",
                                        "right": "auto",
                                        "transform": "translateX(-12px)",
                                    });
                                }
                            }
                        }
                    });
                    $(document).on('mouseleave',"#custom_menu_li",function(ev) {
                        $(this).children("ul#custom_recursive").css({
                            "opacity":"0",
                            "visibility": "hidden",
                            "transform": "translateX(20px)",
                        });
                        if(li_pos > li_count/2) {
                            $(this).children("ul#custom_recursive").css({
                                "transform": "translateX(-20px)",
                            });
                        }
                    });
                }
            }
        })
        if ($(window).width() <= 1200) {
            $(".te_dynamic_ept >a").append('<span class = "fa fa-chevron-down te_icon" />');
	        $('.te_icon').attr('data-toggle', 'true');
            $('.te_icon').attr('aria-expanded', 'true');
	        $(document).on('click',"span.te_icon",function(ev) {
	        	if( $(ev.target).is('.te_icon') ) {
			       	ev.preventDefault();
					$(this).parent("a").siblings('.te_custom_submenu').slideDown('slow');
					$(this).addClass('te_icon_ctg');
	        	}
	        });
	        $(document).mouseup(function(e)
			{
			    var container = $(".te_dynamic_ept");
			    if (!container.is(e.target) && container.has(e.target).length === 0)
			    {
			        $('.te_icon').parent("a").siblings('.te_custom_submenu').slideUp('slow');
			    }
			});
            $(document).keyup(function(e) {
                 if (e.keyCode == 27) {
                    $('.te_icon').parent("a").siblings('.te_custom_submenu').slideUp('slow');
                 }
            })
        	$(document).on('click',"span.te_icon_ctg",function(ev) {
        		$(this).parent("a").siblings('.te_custom_submenu').slideUp('slow');
        		$(this).removeClass('te_icon_ctg');
        	});
        	$(document).on('click',".ctg_arrow",function(ev) {
		        $(this).toggleClass('te_down_ctg_icon');
				if($(this).hasClass('te_down_ctg_icon'))
				{
				    ev.preventDefault();
				    $(this).siblings("ul#custom_recursive").slideDown('slow');
				    return false;
				}
				else
				{
		            $(this).siblings("ul#custom_recursive").slideUp('slow');
			    }
			});
        }
        //Changed search form action in theme's search when website search is installed
        if ($("body").find(".website_search_form_main").length > 0) {
            $(".te_header_search,.te_searchform__popup").each(function() {
                $(this).find("form").attr("action", "/search-result");
            })
            $(".website_search_form_main").html("");
        }
        //Recently viewed title
        if ($('#carousel_recently_view .carousel-inner .img_hover').length >= 1) {
            $('.te_product_recent_h2').css('display', 'block')
        }
        //expertise progress bar
        $('.progress').each(function() {
            var area_val = $(this).find('.progress-bar').attr("aria-valuenow")
            $(this).find('.progress-bar').css("max-width", area_val + "%")
        })
        //Remove images in extra menu
        $("li.o_extra_menu_items").find("img").removeAttr("src alt");

        // if slider then active first slide
        if ($('.recommended_product_slider_main').length) {
            $(".theme_carousel_common").each(function() {
                $(this).find(".carousel-item").first().addClass("active");
            })
        }
        // Change in carousel to display two slide
        $('.theme_carousel_common .carousel-item').each(function() {
            var next = $(this).next();
            if (!next.length) {
                next = $(this).siblings(':first');
            }
            next.children(':first-child').clone().appendTo($(this));
        });
        // quantity design in cart lines when promotion app installed
        $(".te_cart_table .css_quantity > span").siblings("div").css("display", "none")
        // Portal script
        if ($('div').hasClass('o_portal_my_home')) {
            if (!$('a').hasClass('list-group-item')) {
                $(".page-header").css({
                    'display': 'none'
                })
            }
        }

        /** On click selected input, filter will be clear*/
        $('.nav-item input[type="checkbox"]').click(function(){
            if($(this).prop("checked") == false){
                var self = $(this);
                var attr_value;
                if (self.parent("label").hasClass("css_attribute_color")) {
                    attr_value = self.parent("label").siblings(".te_color-name").html();
                    if(attr_value) {
                        attr_value = attr_value.toLowerCase();
                        attr_value = attr_value.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value = attr_value.replace(/\s+/g, "-");
                    }
                } else {
                    attr_value = self.siblings("span").html();
                    if(attr_value) {
                        attr_value = attr_value.toLowerCase();
                        attr_value = attr_value.replace(/(^\s+|[^a-zA-Z0-9 ]+|\s+$)/g,"");
                        attr_value = attr_value.replace(/\s+/g, "-");
                    }
                }
                $('.te_view_all_filter_div .te_view_all_filter_inner').find('.te_clear_attr_a.'+attr_value).trigger('click');
            }
        });
        $( "select" ).change(function () {
            $(this).find("option:selected").each(function() {
                var attr_value = $(this).parents('.nav-item').find('.te_clear_all_variant').attr('attribute-name');
                if(!$(this).text()) {
                    $('.te_view_all_filter_div .te_view_all_filter_inner').find('.te_clear_attr_a.'+attr_value).trigger('click');
                }
            });
        });
        var product_detail = new sAnimations.registry.product_detail();
        product_detail.productGallery();
    })


    //------------------------------------------
    // 07. Compare short name
    //------------------------------------------
    $(document).ready(function(){
        var maxLength = 26;
        var number_compare_item = $("#o_comparelist_table").find('tr:first').find('td').length;
        if(number_compare_item == 4)
        {
            maxLength = 35;
        }
        else if(number_compare_item == 3)
        {
            maxLength = 46;
        }

        var ellipsestext = "...";
        $(".more").each(function(){
            var myStr = $(this).text();
            if($.trim(myStr).length > maxLength){
                var newStr = myStr.substring(0, maxLength);
                var html = newStr + '<span class="moreellipses">' + ellipsestext+ '</span>';
                $(this).html(html);
            }
        });

        /* Slider 14 animation on mouse hover */
        var lFollowX = 0,
         lFollowY = 0,
         x = 0,
         y = 0,
        friction = 1 / 30;

        function moveBackground(e) {
          x += (lFollowX - x) * friction;
          y += (lFollowY - y) * friction;

          var translate = 'translate(' + x + 'px, ' + y + 'px) scale(1.1)';

          $('.te_s14_img').css({
            '-webit-transform': translate,
            '-moz-transform': translate,
            'transform': translate
          });

          window.requestAnimationFrame(moveBackground);
        }

        $(window).on('mousemove click', function(e) {

          var lMouseX = Math.max(-100, Math.min(100, $(window).width() / 2 - e.clientX));
          var lMouseY = Math.max(-100, Math.min(100, $(window).height() / 2 - e.clientY));
          lFollowX = (20 * lMouseX) / 100;
          lFollowY = (10 * lMouseY) / 100;

        });

        moveBackground();

        var owl_rtl = false;
        if ($('#wrapwrap').hasClass('o_rtl')) {
            owl_rtl = true;
        }

        $("#myCarousel_banner_prod_slider").find(".a-submit").click(function (event) {
            sale._onClickSubmit(event)
        });

        var myCarousel_acce_full = $('.accessory_product_main.full-width .owl-carousel, .alternative_product_main.full-width .owl-carousel').owlCarousel({
            loop: false,
            rtl: owl_rtl,
            rewind: true,
            margin: 10,
            lazyLoad:true,
            nav: true,
            dots: false,
            autoplay: true,
            autoplayTimeout: 4000,
            navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
            autoplayHoverPause:true,
            items: 4,
            responsive: {
                0: {
                    items: 1,
                },
                576: {
                    items: 2,
                },
                991: {
                    items: 3,
                },
                1200: {
                    items: 4,
                }
            }
        });

        var myCarousel_acce_prod = $('.accessory_product_main .owl-carousel, .alternative_product_main .owl-carousel').owlCarousel({
            loop: false,
            rtl: owl_rtl,
            rewind: true,
            margin: 10,
            lazyLoad:true,
            nav: true,
            dots: false,
            autoplay: true,
            autoplayTimeout: 4000,
            navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
            autoplayHoverPause:true,
            items: 2,
            responsive: {
                0: {
                    items: 1,
                },
                576: {
                    items: 2,
                }
            }
        });
    });

    $(".o_portal_my_doc_table tr").click(function(){
      window.location = $(this).find('td > a').attr("href");
      return false;
    });

    publicWidget.registry.productsRecentlyViewedSnippet.include({
        /*
         Adds the stock checking to the regular _render method
        @override
        */
        _render: function (){
            this._super.apply(this, arguments);
            var r_name = $("#te_rect_cnt").text();
            $('.te_recently_viewed').find('h6').each(function(){
                $(this).addClass("te_rect_name")
                if(r_name == 2) {
                    $('h6.card-title').addClass('te_2_line');
                }
                if(r_name == 3) {
                    $('h6.card-title').addClass('te_3_line');
                }
            });
        },
    });



    sAnimations.registry.productTab = sAnimations.Class.extend({
        selector: "#wrapwrap",
        start: function () {
            self = this;
            self.selectProductTab();
        },

        selectProductTab: function(){
            $('#te_product_tabs').find('li:first-child').find('.nav-link').addClass('active');
            var firstAttr = $('#te_product_tabs').find('li:first-child').find('.nav-link').attr('aria-controls');
            $('.tabs_container_main .product-body .tab-pane').removeClass('active show');
            $('#'+ firstAttr).addClass('active show');
        },
    });

    var owl_rtl = false;
    if ($('#wrapwrap').hasClass('o_rtl')) {
        owl_rtl = true;
    }
    $('.te_banner_slider_content').owlCarousel({
        loop: true,
        rtl: owl_rtl,
        nav: true,
        dots: false,
        lazyLoad:true,
        navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
        autoplay: true,
        autoplayTimeout: 4000,
        autoplayHoverPause:true,
        items: 1,
        responsive: {
            0: {
                items: 1,
            },
            576: {
                items: 1,
            },
        },
    });

    /* For counting number */

    sAnimations.registry.NumberCount = sAnimations.Animation.extend({
        selector: '#wrapwrap',
         effects: [{
            startEvents: 'scroll',
            update: '_numberCount',
        }],
        init: function () {
            this._super(...arguments);
            this.viewed = false;
        },
        _numberCount: function (scroll) {
            if (scroll > 200 && this.isScrolledIntoView($(".te_numbers")) && !this.viewed) {
                this.viewed = true;
                $('.te_count_value').each(function () {
                    $(this).prop('Counter',0).animate({
                        Counter: $(this).text()
                    }, {
                        duration: 4000,
                        easing: 'swing',
                        step: function (now) {
                            $(this).text(Math.ceil(now));
                        }
                    });
                });
            }
        },
        isScrolledIntoView: function (elem) {
            if(elem.length){
                var docViewTop = $(window).scrollTop();
                var docViewBottom = docViewTop + $(window).height();

                var elemTop = $(elem).offset().top;
                var elemBottom = elemTop + $(elem).height();

                return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
            }
        }
    });
    /**/

    $(window).on("orientationchange",function(){
      location.reload();
    });

    publicWidget.registry.ScrollReview = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        events: {
            'click .ept-total-review': 'scroll_review_tab',
        },
        scroll_review_tab: function() {
            if ($("#nav_tabs_link_ratings").length > 0){
                var header_height = 10;
                if($('header#top').length && !$('header').hasClass('o_header_sidebar')) {
                    if($('header nav').hasClass('te_header_navbar')) {
                        this.header_height = $('header nav').height() + 30;
                    } else {
                        this.header_height = $('header').height() + 30;
                    }
                }
                var totalHeight = parseInt($("#te_product_tabs").offset().top) - parseInt(header_height) - parseInt($("#te_product_tabs").outerHeight());
                $([document.documentElement, document.body]).animate({
                    scrollTop: totalHeight
                }, 2000);
                $('#nav_tabs_link_ratings').trigger('click');
            }
        },
    })

    publicWidget.registry.WebsiteSale.include({
        /*@Author  : Angel Patel (24/09/2020)*/
        /*add restrict sign for if the zip code is the required field in the customer address form. */
        _changeCountry: function () {
            if (!$("#country_id").val()) {
            return;
        }
        this._rpc({
            route: "/shop/country_infos/" + $("#country_id").val(),
            params: {
                mode: $("#country_id").attr('mode'),
            },
        }).then(function (data) {
            // placeholder phone_code
            $("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

            // populate states and display
            var selectStates = $("select[name='state_id']");
            // dont reload state at first loading (done in qweb)
            if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                if (data.states.length || data.state_required) {
                    selectStates.html('');
                    _.each(data.states, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);
                        selectStates.append(opt);
                    });
                    selectStates.parent('div').show();
                } else {
                    selectStates.val('').parent('div').hide();
                }
                selectStates.data('init', 0);
            } else {
                selectStates.data('init', 0);
            }

            // manage fields order / visibility
            if (data.fields) {
                if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                    $(".div_zip").before($(".div_city"));
                } else {
                    $(".div_zip").after($(".div_city"));
                }
                var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                _.each(all_fields, function (field) {
                    $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                });
            }
            $("label[for='zip']").toggleClass('label-optional', !data.zip_required);
            $("label[for='state_id']").toggleClass('label-optional', !data.state_required);
            $("label[for='zip']").get(0).toggleAttribute('required', !!data.zip_required);
            $("label[for='state_id']").get(0).toggleAttribute('required', !!data.state_required);
            var zip_text = $("label[for='zip']").text();
            if (zip_text.indexOf('*')!= -1){zip_text = zip_text.replace('*','')}
            if(data.zip_required){
                zip_text = zip_text + "*";
            }
            $("label[for='zip']").text(zip_text);
        });
        }
    })


    publicWidget.registry.portalDetails.include({
        /*
            @Author : Angel Patel (10/11/2020)
            Make Zip Code as a required based on the Country ID.
        */
        init: function () {
            this._super.apply(this, arguments);
            var self = this;
            var country = $('select[name="country_id"]').val();
            if (!country) {
                return;
            }
            this._rpc({
                route: "/shop/country_information/" + country,
            }).then(function (data) {
                $("label[for='zipcode']").toggleClass('label-optional', !data.zip_required);
                var zip_text = $("label[for='zipcode']").text();
                if (zip_text.indexOf('*')!= -1){zip_text = zip_text.replace('*','')}
                $("label[for='zipcode']").text(zip_text);
            });
        },
        _onCountryChange: function () {
            var self = this;
            this._super();
            var $country = this.$('select[name="country_id"]');
            if (!$country.val()) {
                return;
            }
            this._rpc({
                route: "/shop/country_information/" + $country.val(),
            }).then(function (data) {
                $("label[for='zipcode']").toggleClass('label-optional', !data.zip_required);
                var zip_text = $("label[for='zipcode']").text();
                if (zip_text.indexOf('*')!= -1){zip_text = zip_text.replace('*','')}
                $("label[for='zipcode']").text(zip_text);
            });
        }
    })
});
