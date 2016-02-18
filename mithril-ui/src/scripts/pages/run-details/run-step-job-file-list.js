 // This file is part of Pypers.

 // Pypers is free software: you can redistribute it and/or modify
 // it under the terms of the GNU General Public License as published by
 // the Free Software Foundation, either version 3 of the License, or
 // (at your option) any later version.

 // Pypers is distributed in the hope that it will be useful,
 // but WITHOUT ANY WARRANTY; without even the implied warranty of
 // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 // GNU General Public License for more details.

 // You should have received a copy of the GNU General Public License
 // along with Pypers.  If not, see <http://www.gnu.org/licenses/>.

var m = require('mithril'),
    $ = require('jquery');

var models = require('../../models');

var utils = require('../../utils');


var RunStepJobFileList = {

    // data from ajax
    XHR: {
        list: function(job) {
            return m.request({
                method: 'GET',
                url: '/api/pypers/runs/pipelines/' +
                    job.runId()    + '/' +
                    job.stepName() + '/' +
                    job.idx() + '/' +
                    utils.user.get().sAMAccountName,
                extract: utils.request.authenticate,
                type: models.Files
            });
        }
    },

    // view model
    VM: {
        activeItem: m.prop(''),

        // unique indentifier of object in the list
        serialize: function(item) {
            if(item) return item.path();
            else     return '';
        },

        setActive: function(item) {
            this.activeItem(this.serialize(item));
        },

        isActive: function(item) {
            return this.serialize(item) === this.activeItem();
        },

        reset: function() {
            this.activeItem('');
        },

        toggle: function(item) {
            if(this.isActive(item)) {
                this.reset();
                return false;
            }
            else {
                this.setActive(item);
                return true;
            }
        }
    },

    controller: function(args) {
        var ctrl = this;

        ctrl.vm  = RunStepJobFileList.VM;
        ctrl.xhr = RunStepJobFileList.XHR

        ctrl.files = m.prop(new models.Files());
        ctrl.job   = m.prop(new models.Job());

        ctrl.toggle = function(item) {
            ( args[ ctrl.vm.toggle.bind(ctrl.vm)(item)
                    ? 'onselect'
                    : 'ondeselect'
                  ] || function() {}
            )(item);
        };

        ctrl.reload = function(job) {
            ctrl.files = ctrl.xhr.list(ctrl.job(job));
        };

        ctrl.reset = function() {
            ctrl.vm.reset.bind(ctrl.vm)();
            ctrl.files(new models.Files());
            ctrl.job(new models.Job());
        };

        // options for File Component
        ctrl.getOptions = function(file, type, idx) {
            return {
                onpreview: ctrl.onpreview, // pass the click handler
                isactive: ctrl.vm.isActive.bind(ctrl.vm, file),

                type : type,
                file : file,
                idx  : idx,
                uid  : (new Date()).getTime() + '_' + idx,

                // operations
                preview  : type === 'txt'? file.bytes() <= 5000000: false,
                open     : true,
                download : type === 'txt' || type === 'png'
            }
        };

        // onclick of an item in the list
        ctrl.onpreview = function(file) {
            ctrl.toggle(file);
            (args.onclick || function() {})(file);
        };
    },
    view: function(ctrl, args) {
        var files   = ctrl.files() || new models.Files(),
            logish  = [].concat(
                files.out(),
                files.err(),
                files.log()
            ),
            textish = [].concat(
                files.txt(),
                files.misc()
            );


        var txt_idx = 0;
        var meta_list = files.meta().map(function(file, idx) {
            txt_idx += 1;
            return m.component(File, ctrl.getOptions(file, 'txt', txt_idx));
        });
        var log_list = logish.map(function(file, idx) {
            txt_idx += 1;
            return m.component(File, ctrl.getOptions(file, 'txt', txt_idx));
        });
        var txt_list = textish.map(function(file, idx) {
            txt_idx += 1;
            return m.component(File, ctrl.getOptions(file, 'txt', txt_idx));
        });

        var pdf_list = files.pdf().map(function(file, idx) {
            return m.component(File, ctrl.getOptions(file, 'pdf', idx));
        });

        var html_list = files.html().map(function(file, idx) {
            return m.component(File, ctrl.getOptions(file, 'html', idx));
        });
        var png_list = files.png().map(function(file, idx) {
            return m.component(File, ctrl.getOptions(file, 'png', idx));
        });

        return (
            m('.job-details-container', {
                    class: files.dir() ? 'open' : ''
                },
            m('.job-title', 'job ' + (ctrl.job().idx() + 1)),
            m('ul.files-list',
                m('.group-label',
                    m('label', 'output dir'),
                    m('li.step-result-file.output_dir', {onclick: utils.misc.hiliteText},
                        m('span', files.dir())
                    )
                ),
                meta_list.length ? m('.group-label', m('label', 'meta'), meta_list) : [],
                log_list.length  ? m('.group-label', m('label', 'log'),  log_list) : [],
                pdf_list.length  ? m('.group-label', m('label', 'pdf'),  pdf_list) : [],
                html_list.length ? m('.group-label', m('label', 'html'), html_list) : [],
                txt_list.length  ? m('.group-label', m('label', 'output files'),  txt_list) : [],
                png_list.length  ? m('.group-label', m('label', 'images'),  png_list) : []
            ))
        );
    }
};

var File = {
    controller: function(args) {
        var ctrl = this;

        ctrl.download = function(name) {
            m.redraw.strategy('none');
            document.forms[name].submit();
        };

        ctrl.getImage = function(uid, imgUrl) {

            $.ajax({
                method: 'GET',
                url: imgUrl
            }).done(function (data) {
                if($('#' + uid).length) {
                    $('#' + uid).html('<img src="' + data + '" />');
                    $('#' + uid + '_dwn').attr('href', data);
                }
            });
        };
    },
    view: function(ctrl, args) {
        var file = args.file,
            idx  = args.idx,
            type = args.type,
            uid  = args.uid,

            // operations on a file
            download = args.download,
            preview  = args.preview,
            open     = args.open;

        return (
            m('li.step-result-file '+type, {
                class: args.isactive(file.path())? 'active': ''
            },
                m('span' , {class: type === 'png'? 'media--subtitle': ''},
                function downloadOperation() {
                    if(! download) return m('div.spacer', ' ');

                    return (
                        m('form.file-download', {
                            method: 'GET',
                            action: '/api/fs/file/download',
                            name  : type+'form'+idx
                        },
                            m('input', {
                                name: 'path',
                                type: 'hidden',
                                value: file.path()
                            }),

                            function downloadFunction() {
                                if(type === 'png') {
                                    return m('a[title=download]#'+uid+'_dwn', {
                                        download: utils.filepath.name(file.path())
                                    }, m('i.fa fa-arrow-circle-down'));
                                }
                                else {
                                    return m('a[title=download]', {
                                        href: 'javascript:void(0);',
                                        onclick: ctrl.download.bind(ctrl, type+'form'+idx)
                                    }, m('i.fa fa-arrow-circle-down'));
                                }
                            }()
                        )
                    );
                }(),

                function openOperation() {
                    if(! open) return;

                    return (
                        m('a.file-open', { href: '/api/fs/'+type+'?embed=true&path='+file.path(),
                                           target: '_blank',
                                           title: 'open in a new tab' },
                            m('i.fa fa-external-link')
                        )
                    );
                }(),

                function previewOperation() {
                    return (
                        m(preview? 'a': 'span', {
                            class: 'file-name',
                            title: utils.filepath.name(file.path()),
                            onclick: preview
                                ? args.onpreview.bind(ctrl, file)
                                : function(){}
                        }, utils.filepath.ellipsis(utils.filepath.name(file.path()), 40))
                    );
                }(),

                m('span.file-size', file.size().replace(/\.00/, '').replace(/^0B$/, '0'))),

                function imageViewOperation() {
                    if(type !== 'png') return;

                    setTimeout(function() {
                        ctrl.getImage(
                            uid,
                            '/api/fs/png?embed=false&path=' + file.path()
                        );
                    }, 10);

                    return m('#' + uid);
                }()
            )
        );
    }
};

exports.view = RunStepJobFileList.view;
exports.controller = RunStepJobFileList.controller;

