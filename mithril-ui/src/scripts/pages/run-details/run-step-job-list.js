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

var models = require('../../models');

var utils = require('../../utils');

var RunStepJobList = {

    // data from ajax
    XHR: {
        stepDetails: function(step, onsuccess, onerror) {
            return utils.request.background({
                method: 'GET',
                url: '/api/pypers/runs/pipelines/' +
                    step.runId() + '/' +
                    step.name(),
                onsuccess: onsuccess,
                onerror: onerror,
                extract: utils.request.authenticate,
                type: models.Step
            });
        }
    },

    // view model
    VM: {
        searchVal: m.prop(''),
        activeItem: m.prop(''),

        // unique indentifier of object in the list
        serialize: function(item) {
            if(item) return [item.runId(), item.stepName(), item.idx()].join(':');
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
            this.searchVal('');
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

        ctrl.loading = m.prop(false);

        ctrl.vm  = RunStepJobList.VM;
        ctrl.xhr = RunStepJobList.XHR

        ctrl.stepName = m.prop('');
        ctrl.step = {ready: function() { return false; }, data: function() { return new models.Step() }};

        ctrl.reload = function(step) {
            (args.ondeselect || function() {})();
            ctrl.stepName(step.name());
            ctrl.step = ctrl.xhr.stepDetails(
                step,
                function onsuccess(data) {
                    ctrl.toggle((data.jobs() || [])[0]);
                },
                function onerror() {
                    ctrl.toggle();
                }
            );
        };

        ctrl.reset = function() {
            ctrl.vm.reset.bind(ctrl.vm)();
            ctrl.stepName('');
            ctrl.step = {ready: function() { return false; }, data: function() { return new models.Step() }};
        };

        ctrl.toggle = function(item) {
            ( args[ ctrl.vm.toggle.bind(ctrl.vm)(item)
                    ? 'onselect'
                    : 'ondeselect'
                  ] || function() {}
            )(item);
        };
    },

    view: function(ctrl, args) {

        var jobCss = function(job) {
            return [ ctrl.vm.isActive.bind(ctrl.vm)(job)
                     ? 'active'
                     : '',
                     'step__' + job.status()
                   ].join(' ');
        };

        var step = ctrl.step.data() || new models.Step();
        return (
            m('.step-details-container', {
                    class: ctrl.stepName()? 'open' : '',
                },
                m('.step-details-title',
                    m('.step-title',  + ctrl.step.ready()? ctrl.stepName(): m('i.fa.fa-refresh.fa-spin')),
                    m('input.search-bar', {
                            'class': ctrl.vm.searchVal()? 'open': '',
                            'value': ctrl.vm.searchVal(),
                            'placeholder': 'Search',
                            'onkeyup' : m.withAttr('value', ctrl.vm.searchVal)
                        }
                    ),
                    m('i.icon.fa.fa-search', {onclick: function() {$('input.search-bar').focus();}, class: ctrl.vm.searchVal()? 'hidden': ''} ),
                    m('i.icon.fa.fa-times',  {onclick: function() {$('input.search-bar').focus();ctrl.vm.searchVal('');}, class: ctrl.vm.searchVal()? '': 'hidden'} )
                ),
                m('.step-datails',
                    step.jobs().map(function(job, idx) {
                        var jobLabel  = 'job ' + (idx+1);
                        var metaVal = [];
                        Object.keys(job.meta()).map(function(key) {
                            if (! Array.isArray(job.meta()[key])) {
                                metaVal.push((job.meta()[key]).toString());
                            }
                        });
                        if(! metaVal.length) metaVal.push(jobLabel);
                        metaVal.push(job.status());

                        if(fuzzy.filter(ctrl.vm.searchVal(), metaVal).length) {
                            var status = job.status().toLowerCase()
                            return (
                                m('div.step', {
                                        class: jobCss(job),
                                        onclick: function() {
                                            if(job.status() !== 'queued') {
                                                ctrl.toggle(job);
                                            }
                                        }
                                    },
                                    m('.job',
                                        m('span.job-name', m('i', {class: utils.misc.statusToCss(job.status())}), jobLabel),
                                        m('span.job-meta',
                                            m('ul',
                                                _.map(job.meta(), function(value, key) {
                                                    if (!Array.isArray(value)) {
                                                        return m('li', key + ' : ' + value);
                                                    }
                                                })
                                            )
                                        )
                                    )
                                )
                            )
                        }
                    })
                )
            )
        );
    }
};


exports.view = RunStepJobList.view
exports.controller = RunStepJobList.controller

