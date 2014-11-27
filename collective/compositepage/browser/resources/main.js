  /*global console, window, jQuery, document, alert, initTinyMCE */
(function ($) {
    "use strict";
    if ((typeof window.composite) === 'undefined') {
        window.composite = {};
    }

    var composite = window.composite;

    composite.editmode_tile = null;
    composite.add_mode = null;
    composite.to_delete = [];

    composite.ajaxform = function (form, action) {
        form.ajaxForm({
            type: 'POST',
            dataType: 'html',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: action,
            error: function () {
                alert('Error');
            }
        });
    };

    composite.scroll_to = function(el, offset){
        if(typeof(offset)==='undefined'){
            offset = 0;
        }
        $('html, body').animate({
            scrollTop: $(el).offset().top - $('header .navbar').height() + offset
        }, 2000);
    };

    composite.expose = function (el) {
        $(el).expose({
            'closeOnEsc': false,
            'closeOnClick': false,
            'color': '#333'
        });
    };
    composite.unexpose = function () {
        $.mask.close();
    };

    composite.autocomplete = function(){
        // this is a porting to pure JS of the autocomplete widget
        // from plone.formwidget.autocomplete that unfortunately
        // is totally generate via python :S
        $("div[id$='autocomplete']").each(function(){
            // for some strange reason we have to do this to get the fieldname properly
            var fname = $(this).parent().find('[data-fieldname]')
                               .data('fieldname').replace('.widgets.query', '');
            var self = $(this),
                baseurl = self.closest('form').attr('action'),
                widget_url = baseurl + '/++widget++' + fname,
                autocomplete_url = widget_url + '/@@autocomplete-search';

            self.data({
                'klass': 'contenttree-widget relationlist-field',
                'title': 'None',
                'input_type': 'checkbox',
                'multiple': true
            });
            self.find('[id$="search"]').remove();
            var query_field = $(this).find('input[id$="query"]');
            query_field.autocomplete(
                autocomplete_url, {
                    autoFill: true,
                    minChars: 2,
                    max: 10,
                    mustMatch: false,
                    matchContains: true,
                    formatItem: function(row, idx, count, value) {  return row[1] + " (" + row[0] + ")"; },
                    formatResult: function(row, idx, count) { return ""; },
                    parse: formwidget_autocomplete_parser(function(row, idx, count) { return ""; }, 1)
                }
            ).result(formwidget_autocomplete_ready);

            query_field.each(function() {
                if($(this).siblings('input.searchButton').length > 0) { return; }
                $(document.createElement('input'))
                    .attr({
                        'type': 'button',
                        'value': 'browse...'
                    })
                    .addClass('searchButton')
                    .click( function () {
                        var parent = $(this).parents("*[id$='-autocomplete']")
                        var window = parent.siblings("*[id$='-contenttree-window']")
                        window.showDialog(widget_url + '/@@contenttree-fetch', 200);
                        $('#' + parent.attr('id').replace('autocomplete', 'contenttree')).contentTree(
                            {
                                script: widget_url + '/@@contenttree-fetch',
                                folderEvent: 'click',
                                selectEvent: 'click',
                                expandSpeed: 200,
                                collapseSpeed: 200,
                                multiFolder: true,
                                multiSelect: true,
                                rootUrl: '/Plone'
                            },
                            function(event, selected, data, title) {
                                // alert(event + ', ' + selected + ', ' + data + ', ' + title);
                            }
                        );
                    }).insertAfter($(this));
            });
            var contenttree = self.find('[id$="-contenttree-window"]');
            contenttree.find('.contentTreeAdd').unbind('click').click(function () {
                $(this).contentTreeAdd();
            });
            contenttree.find('.contentTreeCancel').unbind('click').click(function () {
                $(this).contentTreeCancel();
            });
            query_field.after(" ");

        });
    };

    composite.formUnloadProtection = function(){
        var tool = window.onbeforeunload && window.onbeforeunload.tool;
        if (tool && $('form.enableUnloadProtection').length) {
            tool.addForms.apply(tool, $('form.enableUnloadProtection').get());
        }
    };

    composite.Tile = function (manager, tile) {
        var self = this;
        self.manager = manager;
        self.tile = $(tile);
        self.init_actions();
    };

    composite.Tile.prototype = {

        load_content: function (result) {
            var self = this,
                div_container = $('<div class="tile-form-wrapper' +
                                  ' tile-edit-form-wrapper' +
                                  ' container-narrow"></div>');
            div_container.html($(result).find('div#content').html());
            self.tile.html(div_container);
        },

        // gestione via ajax della form di edit dei tiles
        editAjaxForm: function (form) {
            var self = this;

            composite.ajaxform(
                form,
                function (result) {
                    self.tile.empty();
                    if ($(result).find('form#edit_tile').length !== 0) {
                        self.load_content(result);
                        self.editAjaxForm(
                            self.tile.find('form#edit_tile')
                        );
                    } else {
                        self.tile.html(result);
                        composite.scroll_to(self.tile);
                    }
                    self.init_actions();
                    self.manager.init_js();
                    composite.editmode_tile = null;
                    composite.unexpose();
                }
            );
        },

        init_actions: function () {
            var self = this;
            self.init_edit_actions();
            self.init_delete_actions();
            self.init_sorting_actions();
        },

        // ogni link delete-tile deve richiamare la relativa vista
        // e dev'essere rimosso dall pagina
        init_delete_actions: function () {
            var self = this;
            self.tile.find('a.delete-tile').click(function (evt) {
                var link = $(this);
                composite.to_delete.push(link.attr('href'));
                link.parents('div[data-tile]').slideUp('slow').remove();
                self.manager.update_status('info', 'Layout changed.');
                evt.preventDefault();
            });
        },

        init_edit_actions: function () {
            var self = this;
            self.tile.find('a.edit-tile').click(function (evt) {
                var link = $(this);

                $.get(link.attr('href'), function(result) {
                    self.load_content(result)
                    self.editAjaxForm(
                        self.tile.find('form#edit_tile')
                    );
                    composite.expose(self.tile);
                    self.manager.init_js();
                });
                evt.preventDefault();
            });
            self.tile.find('.tile-actions').hide();
            self.tile.mouseenter(function(evt){
                self.tile.find('.tile-actions').delay(200).show('slide');
                evt.stopPropagation();
            })
            .mouseleave(function(evt){
                self.tile.find('.tile-actions').delay(800).hide('slide');
                evt.stopPropagation();
            });
        },

        refresh_tile: function () {
            var self = this;
            $.get(
                self.tile.data('tile'),
                function(data) {
                    self.tile.html(data);
                    self.init_actions();
                    self.manager.init_js();
                }
            );

        },

        init_sorting_actions: function(){
            var self = this,
                buttons = $('.sort-buttons').html();

            $('.sorting-enabled .tile-actions').each(function(){
                $(this).find('.sort-buttons').remove();
                $(this).append(buttons);
            });
            $('.move-up:first, .move-top:first').addClass('disabled');
            $('.move-down:last, .move-bottom:last').addClass('disabled');
            $('.move-down').not('.disabled').click(function(){
                self.manager.move(this, 'down');
                self.init_sorting_actions();
            });
            $('.move-up').not('.disabled').click(function(){
                self.manager.move(this, 'up');
                self.init_sorting_actions();
            });
            $('.move-top').not('.disabled').click(function(){
                self.manager.move(this, 'top');
                self.init_sorting_actions();
            });
            $('.move-bottom').not('.disabled').click(function(){
                self.manager.move(this, 'bottom');
                self.init_sorting_actions();
            });
        }
    }

    composite.TileManager = function (wrapper, settings) {
        var self = this;
        $.extend(self, settings);
        self.wrapper = $(wrapper);
        self.baseurl = self.wrapper.data('baseurl');
        self.tools = self.init_tools();
        self.tiles = self.load_tiles();
        self.placeholder = $('.placeholder');
        self.init_showhide_actions();
    };

    composite.TileManager.prototype = {

        load_tiles: function () {
            var self = this,
                data = self.wrapper.find('div[data-tile]');
            return $.map(
                data,
                function(item) {
                    return new composite.Tile(self, item);
                }
            );
        },

        init_tools: function(){
            var self = this,
                tools = $('.composite-tools');
            $('a.btn.save', tools).click(function(){
                self.save();
                // XXX: use events to save
            });

            tools.find('a.add-tile').each(function () {
                var link = $(this);
                link.click(function (evt) {
                    evt.preventDefault();
                    $.get(link.attr('href'), function(result) {
                        self.load_content(result);
                        var form = self.placeholder.find('form#add_tile')
                        self.addAjaxForm(form);
                        composite.expose(self.placeholder);
                        composite.scroll_to(form, -120);
                        self.init_js();
                    });
                });
            });
            return tools;
        },

        save: function(force){
            var self = this,
                html = '',
                save_btn = $('a.btn.save', self.tools);

            if(save_btn.hasClass('disabled')){
                if(typeof(force)==='undefined'){
                    return false;
                }
            }

            $.each(composite.to_delete, function(){
                $.get(this, function() {});
            });

            $('> div', self.wrapper).each(function(){
              html += self.outer_html(this);
            });

            $.post(
              self.baseurl + '/save-html',
              $.param({
                  'html': html,
              }, true),
              function(data) {
                if(!data.error){
                    save_btn.removeClass('btn-primary')
                        .addClass('btn-success')
                        .addClass('disabled');
                    self.update_status('success', 'Layout saved.', true)
                }
              },
              'json'
            );
        },

        load_content: function (result) {
            var self = this,
                container = $('<div class="tile-form-wrapper tile-add-form-wrapper"></div>');
            container.html($(result).find('div#content').html());
            self.placeholder.hide().html(container).fadeIn(1500);
        },

        // handle tile form submit
        addAjaxForm: function (form) {
            var self = this;

            // bind cancel click
            form.find("input[name='buttons.cancel']").click(function (evt) {
                evt.preventDefault();
                self.placeholder.empty();
                composite.unexpose();
            });

            composite.ajaxform(
                form,
                function (result, status, xhr) {
                    var tile = null;
                    if ($(result).find('form#add_tile').length !== 0) {
                        self.load_content(result);
                        var form = self.placeholder.find('form#add_tile');
                        self.addAjaxForm(form);
                        composite.expose(self.placeholder);
                    } else {
                        // create new tile
                        tile = $('<div data-tile="./' + xhr.getResponseHeader('X-Tile-Url') + '"></div>');
                        tile.html(result);
                        self.placeholder.empty();
                        self.wrapper.append(tile);
                        self.tiles.push(new composite.Tile(self, tile));
                        self.save(true);
                        self.update_status('info', 'Tile added.', true)
                        composite.scroll_to(tile);
                    }
                    self.init_js();
                    composite.unexpose();
                }
            );
        },

        outer_html: function (el){
            var html = $(el).clone().empty().wrap('<div>').parent().html();
            var el = $(html).get(0);
            for (var i=0; i<el.attributes.length; i++){
                if (el.attributes[i].name != 'data-tile'){
                    console.log('removed attr: ' + el.attributes[i].name)
                    el.removeAttribute(el.attributes[i].name);
                }
            }
            console.log(el.outerHTML);
            return el.outerHTML;
        },

        update_status: function(status, message, saved){
            var self = $(this);
            $('.alert', self.tools).addClass('alert-' + status);
            $('.alert .message', self.tools).html(message);
            if(typeof(saved)==='undefined'){
                $('a.btn.save', self.tools).removeClass('disabled');
            }
        },

        init_js: function () {
            var self = this;
            initTinyMCE();
            ploneFormTabbing.initialize();
            composite.autocomplete();
            composite.formUnloadProtection();
            var init_js_event = new Event('init-js');
            // Dispatch the event.
            self.wrapper.trigger(init_js_event);
        },

        move: function (el, action){
            var self = this,
                current = $(el).closest('[data-tile]'),
                prev = current.prev(),
                next = current.next();
            switch (action){
                case 'up':
                    prev.before(current);
                    if (current.prev().length==0){
                        $(el).addClass('disabled');
                    }
                    if (current.next().length > 0){
                        $(el).siblings('.move-down').removeClass('disabled');
                        $('.move-down', prev).addClass('disabled');
                    };
                    break;
                case 'down':
                    next.after(current);
                    if (current.next().length==0){
                        $(el).addClass('disabled');
                    };
                    if (current.prev().length > 0){
                        $(el).siblings('.move-up').removeClass('disabled');
                        $('.move-up', next).addClass('disabled');
                    };
                    break;
                case 'top':
                    $(current).prependTo(self.wrapper);
                    break;
                case 'bottom':
                    $(current).appendTo(self.wrapper);
                    break;
            }
            composite.scroll_to(current);

            self.update_status('info', 'Layout changed.');
        },

        init_showhide_actions: function(){
            var self = this,
                tohide = '#before-content',
                $show_link = self.tools.find('a.show-tools'),
                $hide_link = self.tools.find('a.hide-tools');
            $show_link.hide().click(function(evt){
                $(tohide).fadeIn(1000);
                $(this).hide();
                $hide_link.show();
                $('body').toggleClass('composite-preview');
                $('.tile-edit-wrapper').show();
                evt.preventDefault();
                return false;
            });
            $hide_link.click(function(evt){
                $(tohide).fadeOut(1000);
                $(this).hide();
                $show_link.show();
                $('body').toggleClass('composite-preview');
                $('.tile-edit-wrapper').hide();
                evt.preventDefault();
                return false;
            });
        }

    }

    $.fn.extend({
        tilemanager: function (options) {
            return this.each(function () {

                var settings = $.extend(true, {}, options),
                    $this = $(this),
                    data = $this.data('tilemanager'),
                    tilemanager;

                // If the plugin hasn't been initialized yet
                if (!data) {
                    tilemanager = new composite.TileManager(this, settings);

                    $(this).data('tilemanager', {
                        target: $this,
                        tilemanager: tilemanager
                    });
                }
            });
        }
    });

    composite.initTileManager = function () {
        $('.composite-wrapper').tilemanager();
    };

    $(document).ready(function () {
        composite.initTileManager();
    });

}(jQuery));


