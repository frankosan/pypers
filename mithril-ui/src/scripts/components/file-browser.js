var m = require('mithril'),
    _ = require('lodash'),
    fuzzy = require('fuzzy');

var utils = require('../utils');


var Dir = {
    model: function(data) {
        data = data || {};

        this.path  = m.prop(data.path  || '');
        this.files = m.prop(data.files || []);
        this.dirs  = m.prop(data.dirs  || []);
    },
    list: function(path) {
        return m.request({
            method: 'GET',
            url: '/api/fs/dir',
            data: { path: path },
            extract: utils.request.authenticate,
            type: Dir.model
        })
    }
};

var FileBrowser = {
    controller: function(args) {
        var ctrl = this;

        ctrl.onclose = (args || {}).onclose || function() {};

        ctrl.mode      = m.prop((args || {}).mode || 'dir'); // file || dir
        ctrl.multiple  = m.prop(args.multiple || false);
        ctrl.selection = m.prop(ctrl.multiple()? []: ''); // single vs multiple selection

        ctrl.ls   = m.prop(new Dir.model());

        ctrl.target = function() {};

        ctrl.init = function(path, mode, multiple, target, selection) {
            ctrl.mode(mode || ctrl.mode()); // override mode if present
            ctrl.multiple(multiple); // override mode if present

            ctrl.target = target;
            ctrl.browse(path);

            if(ctrl.multiple()) {
                ctrl.selection(selection || []);
            }
        };

        ctrl.browse = function(path) {
            ctrl.searchVal('');
            ctrl.ls = Dir.list(path || '/');

            if(! ctrl.multiple()) {
                if(ctrl.mode() === 'dir') {
                    ctrl.selection(path);
                }
                else {
                    ctrl.selection('');
                }
            }
        };

        ctrl.loadfofn = function(event, fofn) {
            event.returnValue = false; // do not toggle the file

            m.request({
                method: 'GET',
                url: '/api/fs/fofn',
                data: { path: fofn },
                extract: utils.request.authenticate
            }).then(function(list) {
                var newlist = ctrl.selection().concat(list);
                ctrl.selection(_.unique(newlist));
            });
        };

        ctrl.toggle = function(event, type, path) {
            if(event.returnValue === false) return;
            if(type !== ctrl.mode()) return;

            ctrl[ctrl.isSelected(path)? 'unselect': 'select'](path);
        };

        ctrl.select = function(path) {
            if(ctrl.multiple()) {
                ctrl.selection().push(path);
            }
            else {
                ctrl.selection(path);
            }
        };
        ctrl.unselect = function(path) {
            if(ctrl.multiple()) {
                ctrl.selection().splice(ctrl.selection().indexOf(path), 1);
            }
            else {
                ctrl.selection('');
            }
        };

        ctrl.isSelected = function(path) {
            if(ctrl.multiple()) {
                return ctrl.selection().indexOf(path) > -1;
            }
            else {
                return ctrl.selection() === path;
            }
        };

        ctrl.isAllSelected = function() {
            var thisList = ctrl.ls()[ctrl.mode()+'s']().map(function(o) { return ctrl.ls().path() + '/' + o });
            var theSelection = ctrl.selection();

            return !ctrl.searchVal() && thisList.length === _.intersection(thisList, theSelection).length && thisList.length > 0;
        };

        ctrl.toggleAll = function() {
            var thisList = ctrl.ls()[ctrl.mode()+'s']().map(function(o) { return ctrl.ls().path() + '/' + o });
            var theSelection = ctrl.selection().slice();

            // deselect all
            if(ctrl.isAllSelected()) {
                theSelection.map(function(s) {
                    if(thisList.indexOf(s) > -1) {
                       ctrl.selection().splice(ctrl.selection().indexOf(s), 1);
                    }
                });
            }
            // select all
            else {
                thisList.map(function(o) {
                    if(ctrl.selection().indexOf(o) === -1) {
                        ctrl.selection().push(o);
                    }
                });
            }
        };

        ctrl.hasSelection = function() {
            if(ctrl.multiple()) {
                return true; //ctrl.selection().length > 0;
            }
            else {
                return ctrl.selection();
            }
        };

        ctrl.selectionSize = function() {
            if(ctrl.hasSelection() && ctrl.multiple()) {
                return ' (' + ctrl.selection().length + ')';
            }
            return '';
        };

        ctrl.close = function(andSelect) {
            if(andSelect) {
                ctrl.target(ctrl.selection());
            }
            ctrl.onclose();
        };

        ctrl.searchVal = m.prop('');
        ctrl.embedList = m.prop(false);

        ctrl.scrollList = function(elt) {
            ctrl.embedList(elt.scrollTop > 0);
        };

        ctrl.search = function(val) {
            ctrl.searchVal(val);
        };
    },

    view: function(ctrl, args) {
        // handle if the path is invalid
        if(! ctrl.ls()) {
            return m('.file-browser-modal',
                m('.file-browser.error', m('.message', 'Invalid Path'),
                    m('.action-buttons',
                        m('button.btn btn-default', {
                            onclick: ctrl.close.bind(ctrl, false)
                        }, 'Cancel')
                    )
                )
            );

        }
        else
        return (
            m('.file-browser-modal',
                m('.file-browser.multiple-'+ctrl.multiple(), m.component(PathCrumbs, {path: ctrl.ls().path(), browse: ctrl.browse}),
                    m('.content', m('.left',
                    m('.menu-bar', {class: ctrl.embedList()? 'pop': ''},
                        m('input.search-bar', {
                                'class': ctrl.searchVal()? 'open': '',
                                'value': ctrl.searchVal(),
                                'placeholder': 'Search',
                                onkeyup : m.withAttr('value', ctrl.search)
                        }),
                        m('i.icon.fa.fa-search', {onclick: function() {$('input.search-bar').focus();}, class: ctrl.searchVal()? 'hidden': ''} ),
                        m('i.icon.fa.fa-times',  {onclick: function() {$('input.search-bar').focus();ctrl.searchVal('');}, class: ctrl.searchVal()? '': 'hidden'} )
                    ),
                    m('.browser-list.multiple-'+ctrl.multiple(), {onscroll: function(e) {ctrl.scrollList(e.target);}},
                        m('ul.mode-' + ctrl.mode(),
                            function selectAllChb() {
                                if(ctrl.multiple()) {
                                    return m('li.ls-all', {class: ctrl.searchVal()? 'disabled': ''},
                                        m('a.chb', {
                                                onclick: function() {
                                                    if(! ctrl.searchVal()) {
                                                        ctrl.toggleAll();
                                                    }
                                                }
                                            },
                                            m('i.fa', {
                                                class: ctrl.isAllSelected()
                                                       ? 'fa-check-square-o'
                                                       : ctrl.searchVal()
                                                         ? 'fa-ban'
                                                         : 'fa-square-o'
                                            })
                                        ),
                                        m('em', {
                                            onclick: function() {
                                                if(! ctrl.searchVal()) {
                                                    ctrl.toggleAll();
                                                }
                                            }}, 'ALL')
                                    );
                                }
                                else return null;
                            }(),

                            fuzzy.filter(ctrl.searchVal(), ctrl.ls().dirs()).map(function(dir) {
                                var _path = ctrl.ls().path() + '/' + dir.original;
                                return m('li.ls-dir', {
                                        class: ctrl.isSelected(_path)? 'selected' : '',
                                        onclick: ctrl.toggle.bind(ctrl, event, 'dir', _path),
                                        ondblclick: ctrl.browse.bind(ctrl, _path)
                                    },

                                    ctrl.multiple() && ctrl.mode() === 'dir'
                                    ? m('a.chb',
                                        m('i.fa', {class: ctrl.isSelected(_path)? 'fa-check-square-o' : 'fa-square-o'})
                                      )
                                    : null,

                                    m('i.fa fa-folder'),
                                    m('a', {
                                        onclick: function(event) {
                                            event.stopPropagation();
                                            ctrl.browse(_path);
                                        }
                                    }, dir.original)
                                )
                            }),
                            fuzzy.filter(ctrl.searchVal(), ctrl.ls().files()).map(function(file) {
                                var _path = ctrl.ls().path() + '/' + file.original;
                                return m('li.ls-file', {
                                        class: ctrl.isSelected(_path)? 'selected' : '',
                                        onclick: ctrl.toggle.bind(ctrl, event, 'file', _path),
                                    },

                                    ctrl.multiple() && ctrl.mode() === 'file'
                                    ? m('a.chb',
                                        m('i.fa', {class: ctrl.isSelected(_path)? 'fa-check-square-o' : 'fa-square-o'})
                                      )
                                    : null,

                                    m('i.fa fa-file-o'),
                                    m('span', file.original),

                                    ctrl.multiple() && file.original.toLowerCase().indexOf('fofn') > -1
                                    ? m('a.loadfofn', {onclick: ctrl.loadfofn.bind(ctrl, event, _path)},
                                        m('i.fa.fa-share-square-o')
                                      )
                                    : null
                                )
                            })
                        )
                    )),
                    ctrl.multiple()
                        ? m('.right.selection-list', m('ul', (ctrl.selection() || []).map(function(path, i) {
                                return m('li', m('i.fa.fa-check-square-o', {
                                        onclick: function() {
                                            ctrl.selection().splice(i, 1);
                                        }
                                    }), m('span', {onclick: ctrl.browse.bind(ctrl, utils.filepath.dir(path))}, path));
                          })))
                        : null
                    ),
                    m('.action-buttons',
                        m('button.btn btn-default', {
                            onclick: ctrl.close.bind(ctrl, false)
                        }, 'Cancel'),
                        m('button.btn btn-primary', {
                            disabled: ! ctrl.hasSelection(),
                            onclick: ctrl.close.bind(ctrl, true)
                        }, 'Select' + ctrl.selectionSize())
                    )
                )
            )
        );
    }
};

var PathCrumbs = {
    view: function(ctrl, args) {
        var _crumb = [];
        return (
            m('.path-crumbs', m('a.crumb', {onclick: args.browse.bind(ctrl, '')}, '$'),
                 args.path.replace(/^\/$/, '').split('/').map(function(pathname) {
                    _crumb.push(pathname);
                    return [
                        m('a.crumb', {onclick: args.browse.bind(ctrl, _crumb.join('/'))}, pathname), '/'
                    ];
                 })
            )
        );
    }
};

exports.view = FileBrowser.view;
exports.controller = FileBrowser.controller;

