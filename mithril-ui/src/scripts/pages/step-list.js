var m = require('mithril'),
    _ = require('lodash'),
    fuzzy = require('fuzzy');

var models = require('../models');

var utils      = require('../utils'),
    Observable = require('../utils/observable');

var NesLayout = require('../components/neslayout'),
    StepForm  = require('../components/param-form/step');


var Step = {
    list: function(filter) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/steps',
            data: filter,
            extract: utils.request.authenticate
        });
    }
};


var StepListPage = {};

StepListPage.vm = {
    groupList: m.prop([]),

    groupIsOpen: m.prop({}),
    step: m.prop(''),
    embedList: m.prop(false), // when it scrolls

    init: function(steps) {
        StepListPage.vm.clearSelection();
        StepListPage.vm.groupList(
            Object.keys(steps)
        );
        StepListPage.vm.closeAll();
    },

    toggle: function(group) {
        if(StepListPage.vm.groupIsOpen()[group] === 1) {
            StepListPage.vm.groupIsOpen()[group] = 0;
        }
        else {
            StepListPage.vm.groupIsOpen()[group] = 1;
        }
    },

    openAll: function() {
        StepListPage.vm.groupList().map(function(group) {
            StepListPage.vm.groupIsOpen()[group] = 1;
        });
    },
    closeAll: function() {
        StepListPage.vm.groupList().map(function(group) {
            StepListPage.vm.groupIsOpen()[group] = 0;
        });
    },
    isAllOpen: function() {
        var oneClosed = _.find(StepListPage.vm.groupIsOpen(), function(v, k) {
            return v === 0;
        });
        return oneClosed === undefined; // can't find any closed
    },

    clearSelection: function(steps) {
        StepListPage.vm.step('');
        StepListPage.vm.closeAll();
    },

    hasSelected: function(group) {
        return StepListPage.vm.step().startsWith(group + '/');
    },

    isStepSelected: function(group, step) {
        return StepListPage.vm.step() === group + '/' + step;
    },

    scrollList: function(elt) {
        StepListPage.vm.embedList(elt.scrollTop > 0);
    }

};

StepListPage.controller = function() {
    var ctrl = this;
    ctrl.vm = StepListPage.vm;

    ctrl.steps = Step.list();
};

StepListPage.view = function(ctrl, args) {
    return m.component(NesLayout, {
        menu: 'steps',
        breadcrumbs: [{label: 'Steps'}],
        main: [
            m.component(StepList, {steps: ctrl.steps})
        ]
    });
};


var StepList = {
    controller: function(args) {
        var ctrl = this;
        ctrl.vm = StepListPage.vm;
        ctrl.vm.init(args.steps());

        ctrl.searchVal = m.prop('');

        ctrl.search = function(val) {
            ctrl.searchVal(val);
            StepListPage.vm.openAll();
        };

        ctrl.select = function(group, step) {
            if(StepListPage.vm.isStepSelected(group, step)) {
                StepListPage.vm.step('');
                ctrl.stepFormCtrl.clear();
            }
            else {
                StepListPage.vm.step(group + '/' + step);
                ctrl.stepFormCtrl.fetch(group, step);
            }
        };

        ctrl.submit = function(sname, sclass, data) {
            // client side validation
            // if(! document.forms['param-form'].checkValidity()) return;
            document.forms['param-form'].noValidate = true; // skip client side validation

            m.request({
                method: 'PUT',
                url: '/api/pypers/steps/submit',
                data: {
                    config: _.extend({}, data, {name: sname, step_class: sclass}),
                    user : utils.user.get().sAMAccountName
                },
                extract: utils.request.authenticate
            }).then(
            function(response) {
                Observable.trigger('pypers.feedback', {
                    msg  : response,
                    level: 'success'
                });
                window.setTimeout(function() {
                    m.route('/');
                }, 3000);
                // ctrl.status({
                //     code: 200,
                //     message: response
                // });
            },
            function(errorObj) {
                ctrl.stepFormCtrl.error(errorObj);
                // Observable.trigger('pypers.feedback', {
                //     msg  : 'oops',
                //     level: 'error'
                // });
            });
        };

        ctrl.stepForm = m.component(StepForm, { submit: ctrl.submit });
        ctrl.stepFormCtrl = new ctrl.stepForm.controller();

        ctrl.onunload = function() {
            ctrl.stepFormCtrl.onunload();
        };
    },
    view: function(ctrl, args) {
        return (
            m('.step-list-container',
                m('.menu-bar', {class: ctrl.vm.embedList()? 'pop': ''},
                    m('input.search-bar', {
                            'class': ctrl.searchVal()? 'open': '',
                            'value': ctrl.searchVal(),
                            'autofocus': true,
                            'placeholder': 'Search',
                            onkeyup : m.withAttr('value', ctrl.search)
                    }),
                    m('i.icon.fa.fa-search', {onclick: function() {$('input.search-bar').focus();}, class: ctrl.searchVal()? 'hidden': ''} ),
                    m('i.icon.fa.fa-times',  {onclick: function() {$('input.search-bar').focus();ctrl.searchVal('');}, class: ctrl.searchVal()? '': 'hidden'} ),
                    m('.open-close',
                        m('a', {class: ctrl.vm.isAllOpen()? '': 'hidden', onclick: ctrl.vm.closeAll.bind(ctrl.vm)}, m('i.fa.fa-chevron-up')),
                        m('a', {class: ctrl.vm.isAllOpen()? 'hidden': '', onclick: ctrl.vm.openAll.bind(ctrl.vm)}, m('i.fa.fa-chevron-down'))
                    )
                ),
                m('.step-list', {onscroll: function(e) {ctrl.vm.scrollList(e.target);}},
                _.map(args.steps(), function(steps, group) {
                    var filtSteps = []
                    filtSteps = _.filter(steps, function(s){
                        return (
                            fuzzy.filter(ctrl.searchVal(), [s]).length ||
                            ctrl.vm.isStepSelected(group, s)
                        );
                    })
                    if (fuzzy.filter(ctrl.searchVal(), [group]).length) {
                        filtSteps = steps;
                    }
                    if (filtSteps.length) {
                        return (
                            m('.group', {
                                     class: [
                                         ctrl.vm.groupIsOpen()[group] === 1 || ctrl.searchVal() !== '' ? 'open'     : '',
                                         ctrl.vm.hasSelected(group)   ? 'selected' : ''
                                     ].join(' ')
                                 },
                                 m('.group--label', {
                                     onclick: ctrl.vm.toggle.bind(ctrl.vm, group)
                                 }, group + (ctrl.vm.hasSelected(group)? ' *': '')),
                                 m('ul.group--steps',
                                    filtSteps.map(function(s) {
                                        return m('li', {
                                                class: ctrl.vm.isStepSelected(group, s)? 'selected': '',
                                                onclick: ctrl.select.bind(ctrl, group, s)
                                            }, s
                                        )
                                    })
                                )
                            )
                        )
                    }
                })
            ),
            m('.step-details-container',
                ctrl.stepForm.view(ctrl.stepFormCtrl)
            ))
        );
    }
};


exports.view = StepListPage.view;
exports.controller = StepListPage.controller;
