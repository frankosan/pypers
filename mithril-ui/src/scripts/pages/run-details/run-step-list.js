var m = require('mithril');

var utils = require('../../utils');

var RunStepList = {

    // view model
    VM: {
        // unique indentifier of object in the list
        serialize: function(item) {
            if(item) return [item.runId(), item.name()].join(':');
            else     return '';
        },

        activeItem: m.prop(''),

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
            if(!item || this.isActive(item)) {
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

        ctrl.vm = RunStepList.VM;

        ctrl.toggle = function(item) {
            ( args[ ctrl.vm.toggle.bind(ctrl.vm)(item)
                    ? 'onselect'
                    : 'ondeselect'
                  ] || function() {}
            )(item);
        };
    },

    view: function(ctrl, args) {
        var run = args.run;

        var stepJobsTotal = function(step) {
            if(step.total() > 1) {
                return  '(' + step.total() + ')';
            }
            return '';
        };

        var stepCss = function(step) {
            return [ ctrl.vm.isActive.bind(ctrl.vm)(step)
                     ? 'active'
                     : '',
                     'step__' + step.status()
                   ].join(' ');
        };

        return (
            m('.steps-container',
                m('.step-list', run.steps().map(function(step) {
                    return (
                        m('div.step', {
                                class: stepCss(step),
                                onclick: function() {
                                    if(step.status() !== 'queued') {
                                        ctrl.toggle(step);
                                    }
                                }
                            },
                            m('.step-label',
                                m('i', { class: utils.misc.statusToCss(step.status()) }),
                                m('.step-name', step.name()),
                                m('.step-stat', stepJobsTotal(step))
                            )
                        )
                    );
                }))
            )
        )
    }
};


exports.view = RunStepList.view;
exports.controller = RunStepList.controller;
exports.vm = RunStepList.VM;

