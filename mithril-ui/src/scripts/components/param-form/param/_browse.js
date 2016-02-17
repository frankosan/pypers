/**
 * This is a private component that gets inhereted by file and dir input type
 */

var m = require('mithril'),
    _ = require('lodash'),
    $ = require('jquery');

var Observable = require('../../../utils/observable');

var ParamBrowse = {
    controller: function(args) {
        var ctrl = this;

        // this is to be able to trigger the change event
        // on the input after setting it
        // using the file browser
        ctrl.elt = null;
        ctrl.setElt = function(elt, isInit) {
            if(! isInit) return;
            ctrl.elt = elt;
        };

        ctrl.set = function(val) {
            $(ctrl.elt).val(val).trigger('change');
        };

        ctrl.browse = function(root, selection) {
            Observable.trigger('pypers.run.new.param.browse', {
                root: root,
                selection: _.clone(selection),
                multiple: args.param.multiple(),
                target: ctrl.set
            });
        };
    },
    view: function(ctrl, args) {
        return (
            m('.input-group',
                function multiDisplay() {
                    if(args.param.multiple()) {
                        return [
                            m('.param-multilist-selection.listof-'+args.data.length, {
                                onclick: function() {
                                    var root = args.param.rdir();
                                    if(args.data.length) {
                                        root = args.data[0];
                                        root = root.substring(0, root.lastIndexOf('/'));
                                    }
                                    ctrl.browse(args.type + ':'+root, args.data || []);
                                    // if(args.data.length) {
                                    //     $('#'+args.param.name()+'_list').toggleClass('visible');
                                    // }
                                }
                            }, '(' + (args.data || []).length + ' selected)'),

                            m('#'+args.param.name()+'_list.param-multilist',
                                function selectionList() {
                                    var list = args.data || [];
                                    if(list.length) {
                                        return list.map(function(l, i) {
                                            return m('.param-multilist-item', (i+1) + ': ' + l,
                                                        m('i.fa.fa-times', {
                                                            onclick: function() {
                                                                list.splice(i, 1);
                                                                if(! list.length) {
                                                                    $('#'+args.param.name()+'_list').removeClass('visible');
                                                                }
                                                            }
                                                        })
                                                   );
                                        });
                                    }
                                    else {
                                        return m('.empty', {
                                            'onclick': ctrl.browse.bind(ctrl, args.type + ':'+(args.data || args.param.rdir()))
                                        }, 'none chosen');
                                    }
                                }(),
                                m('input[type=hidden]', {
                                    'config'    : ctrl.setElt,
                                    'name'      : args.param.name(),
                                    'value'     : args.data,
                                    'data-mult' : true,
                                    'data-step' : args.step || ''
                                })
                            ),
                            m('span.input-group-btn',
                                m('button[type=button].btn btn-secondary', {
                                    'tabIndex': -1,
                                    'onclick': function() {
                                        var root = args.param.rdir();
                                        if(args.data.length) {
                                            root = args.data[0];
                                            root = root.substring(0, root.lastIndexOf('/'));
                                        }
                                        ctrl.browse(args.type + ':'+root, args.data || []);
                                    }
                                }, m('i.fa fa-folder-open'))
                            )
                        ];
                    }
                    else {
                        return [
                            m('input.form-control.form-control-'+args.type+'[type=text]', {
                                'config'    : ctrl.setElt,
                                'name'      : args.param.name(),
                                'value'     : args.data,
                                'required'  : args.param.required(),
                                'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
                                'data-step' : args.step || ''
                            }),
                            m('span.input-group-btn',
                                m('button[type=button].btn btn-secondary', {
                                    'tabIndex': -1,
                                    'onclick': ctrl.browse.bind(ctrl, args.type+':'+(args.data || args.param.rdir()))
                                }, m('i.fa fa-folder-open'))
                            )
                        ];
                    }
                }()
            )
        );
    }
};

exports.view = ParamBrowse.view;
exports.controller = ParamBrowse.controller;


