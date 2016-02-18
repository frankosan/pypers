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
    fuzzy = require('fuzzy');
    _ = require('lodash');

var models = require('../../models');
var utils = require('../../utils');

var RunOutputs = {
    XHR: {
        getOutputs: function(id) {
            return m.request({
                method: 'GET',
                url: '/api/pypers/runs/pipelines/'+id+'/outputs',
                extract: utils.request.authenticate,
                type: models.RunOutput
            });
        }
    },

    VM: {
        groupList: m.prop([]),
        groupIsOpen: m.prop({}),
        embedList: m.prop(false), // when it scrolls

        metaIsOpen: m.prop(false),

        init: function(steps) {
            this.metaIsOpen(false);
        },

        toggle: function(group) {
            if(this.groupIsOpen()[group] === 1) {
                this.groupIsOpen()[group] = 0;
            }
            else {
                this.groupIsOpen()[group] = 1;
            }
        },

        openAll: function(steps) {
            steps.map(function(step) {
                this.groupIsOpen()[step.name()] = 1;
            }.bind(this));
        },
        closeAll: function(steps) {
            steps.map(function(step) {
                this.groupIsOpen()[step.name()] = 0;
            }.bind(this));
        },
        isAllClosed: function() {
            var oneOpen = _.find(this.groupIsOpen(), function(v, k) {
                return v === 1;
            });
            return oneOpen === undefined; // can't find any open
        },

        scrollList: function(elt) {
            this.embedList(elt.scrollTop > 0);
        }
    },

    controller: function(args) {
        var ctrl = this;

        ctrl.vm = RunOutputs.VM;
        ctrl.vm.init();

        ctrl.outputs = RunOutputs.XHR.getOutputs(args.id);

        ctrl.archive = function() {
            var fileSelection = ctrl.outputs().selection();
            var metaSelection = $('#run_meta_form').serializeArray();

            var metaJSON = {};
            metaSelection.forEach(function(meta) {
                metaJSON[meta.name] = meta.value;
            });

            var selection = {};
            Object.keys(fileSelection).forEach(function(step) {
                fileSelection[step].forEach(function(file) {
                    //selection[file.path] = _.extend({step: step}, {meta: _.extend(file.meta, metaJSON)});
                    selection[file.path] = _.extend({meta: _.extend(file.meta, metaJSON, {step: step})}); 
                });
            });

            m.request({
                method: 'POST',
                url: '/api/pypers/runs/pipelines/'+args.id+'/archive',
                data: {'selection': selection, 'user': utils.user.get().sAMAccountName},
                extract: utils.request.authenticate
            }).then(
                function(response) {
                    ctrl.vm.metaIsOpen(false);
                    ctrl.outputs().clearAll();
                    window.setTimeout(function() {
                        m.route('/run/' + args.id + '?list');
                    }, 500);
                }
            );

        };
    },

    view: function(ctrl, args) {
        var run = args.runId;

        var _count = ctrl.outputs().countSelection();
        return (
            m('.output-list-tab', m('.output-list-container', {class: ctrl.vm.metaIsOpen()? 'meta__visible': ''},
                m('.menu-bar', {class: ctrl.vm.embedList()? 'pop': ''},
                    m('.select-deselect',
                        m('i.fa', {
                            class: ctrl.outputs().archive()? 'fa-check-square-o': 'fa-square-o',
                            onclick: ctrl.outputs().toggle.bind(ctrl.outputs())
                        })
                    ),
                    m('button.btn.btn-link.meta--toggle', {
                        class: !_count? 'hidden': '',
                        onclick: ctrl.vm.metaIsOpen.bind(ctrl.vm, !ctrl.vm.metaIsOpen())
                    }, m('i.fa.fa-archive'), _count + ' files'),
                    m('.open-close',
                        m('a', {class: ctrl.vm.isAllClosed.apply(ctrl.vm)? 'hidden': '', onclick: ctrl.vm.closeAll.bind(ctrl.vm, ctrl.outputs().steps())}, m('i.fa.fa-chevron-up')),
                        m('a', {class: ctrl.vm.isAllClosed.apply(ctrl.vm)? '': 'hidden', onclick: ctrl.vm.openAll.bind(ctrl.vm, ctrl.outputs().steps())}, m('i.fa.fa-chevron-down'))
                    )
                ),
                m('.step-outputs-meta',
                    m('h2', 'METADATA'),
                    m.component(RunMeta, { id: args.id }),
                    m('button.btn.btn-submit.btn-primary.btn-archive', {
                        onclick: ctrl.archive
                    },'Move to Irods')
                ),
                m('.step-outputs-list', {onscroll: function(e) {ctrl.vm.scrollList.call(ctrl.vm, e.target);}},
                ctrl.outputs().steps().map(function(step) {
                    return (
                        m('.step-outputs', {
                            class: [
                                ctrl.vm.groupIsOpen()[step.name()] === 1? 'open': '' ,
                                step.countSelection()? 'selected' : ''
                            ].join(' ')
                        },
                            m('.step-label', {
                                  onclick: ctrl.vm.toggle.bind(ctrl.vm, step.name())
                              },
                              m('i.fa.step--archive', {
                                  onclick: function(event) {
                                      event.stopPropagation();
                                      step.toggle.apply(step);
                                  },
                                  class: step.archive()? 'fa-check-square-o': 'fa-square-o'
                              }),
                              m('.step--name', m('em', step.countSelection() + '/' + step.files().length), step.name())
                            ),
                            m('ul.step-files',
                            step.files().map(function(file){
                                return (
                                      m('li', {
                                            onclick: file.toggle.bind(file),
                                            class: file.archive()? 'file--archive': ''
                                        },
                                        //m('.file--path', file.path())
                                        m('.file--path', utils.filepath.ellipsis(file.path(), 140))
                                    )
                                );
                            }))
                        )
                    )
                }))
            ))
        );
    }
};

var RunMeta = {
    XHR: {
        getMeta: function(id) {
            return m.request({
                method: 'GET',
                url: '/api/pypers/runs/pipelines/'+id+'/meta',
                extract: utils.request.authenticate
            });
        }
    },
    controller: function(args) {
        var ctrl = this;

        ctrl.meta = RunMeta.XHR.getMeta(args.id);
        // ctrl.meta = m.prop([
        //     {name: 'run_id', label: 'Run ID', value: args.id, readonly: true},
        //     {name: 'study', label: 'Study', value: 'PROJECT_NAME_VAL'},
        //     {name: 'assay_platform', label: 'Assay Platform', value: 'ASSAY_PLTFRM_VAL'},
        //     {name: 'assay_id', label: 'Assay ID', value: 'ASSAY_ID_VAL'},
        // ]);
    },
    view: function(ctrl, args) {
        return (
            m('form#run_meta_form.form-horizontal', Object.keys(ctrl.meta()).map(function(pname) {
                return  (
                    m('.form-group',
                        m('label', pname),
                        m('input.form-control[type=text]', {
                            'name'      : pname,
                            // 'required'  : param.required,
                            'value'     : ctrl.meta()[pname]
                            // 'disabled'  : !!param.readonly
                        })
                    )
                )
            }))
        );
    }
};


exports.view = RunOutputs.view;
exports.controller = RunOutputs.controller;
