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

