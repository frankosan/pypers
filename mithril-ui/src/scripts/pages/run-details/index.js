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
    $ = jQuery = require('jquery'),
    _ = require('lodash');

var models = require('../../models');
var utils  = require('../../utils');

var NesLayout   = require('../../components/neslayout'),
    FilePreview = require('../../components/file-preview'),
    PipelineDag = require('../../components/pipeline-dag');


var RunStepList        = require('./run-step-list'),
    RunStepJobList     = require('./run-step-job-list');
    RunStepJobFileList = require('./run-step-job-file-list');
    RunOutputs         = require('./run-outputs')


var filePreview     = m.component(FilePreview);
var filePreviewCtrl = new filePreview.controller();

var runStepJobFileList = m.component(RunStepJobFileList, {
    onselect: filePreviewCtrl.toggle,
    ondeselect: filePreviewCtrl.toggle
});
var runStepJobFileListCtrl = new runStepJobFileList.controller();

var runStepJobList     = m.component(RunStepJobList, {
    onselect:   function(job) { runStepJobFileListCtrl.reload(job); },
    ondeselect: function()    { runStepJobFileListCtrl.reset(); }
});
var runStepJobListCtrl = new runStepJobList.controller();


var Services = {
    getPipeline: function(id) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/runs/pipelines/' + id,
            extract: utils.request.authenticate,
            type: models.Run
        });
    },
    getDag: function(id) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/runs/pipelines/'+id+'/dag',
            extract: utils.request.authenticate
        })
    }
};

// Page State
var RunDetailsPage = {}

RunDetailsPage.vm = {

    init : function(ctrl){
        this.view     = m.prop('list');
        this.runId    = m.prop(ctrl.id);
        this.stepName = m.prop('');
        this.jobIdx   = m.prop(-1);
    },

    // reset VM variables with controller init
    reset: function(id) {
        // check if new run id, then reset selection
        // keep selection for same run id
        if(id !== this.runId()) {
            this.stepName('');
            this.jobIdx(-1);
        }
        this.runId(id);
    },

    getParentStatusParam: function(status) {
        if(status === 'Succeeded' || status === 'Failed') {
            return ['Succeeded', 'Failed'];
        }
        return status
    },

    getParentStatusLabel: function(status) {
        if(status === 'Succeeded' || status === 'Failed') {
            status = 'Completed';
        }
        return status;
    },

    hasStep: function() {
        return this.stepName() !== '';
    },

    hasJob: function() {
        return this.hasStep() && this.jobIdx() > -1;
    },

    toggleView: function(view) {
        this.view(view);
        m.route('/run/' + this.runId() + '?' + this.view(), {}, true);
    },

    showStepDetails: function(step) {
        runStepJobListCtrl.reload(step);
    }
};


RunDetailsPage.controller = function() {
    var ctrl = this;

    ctrl.onunload = function() {
        filePreviewCtrl.close();
        runStepJobFileListCtrl.reset();
        runStepJobListCtrl.reset();
    };

    ctrl.id  = parseInt(m.route.param('id') || -1);
    ctrl.run = Services.getPipeline(ctrl.id);
    ctrl.dag = Services.getDag(ctrl.id);

    ctrl.vm = RunDetailsPage.vm
    ctrl.vm.init(ctrl)
    ctrl.vm.reset(ctrl.id); // reset selections for new runs
    ctrl.vm.view(
        m.route.param('dag') !== undefined
        ? 'dag'
        : m.route.param('outputs') !== undefined
          ? 'outputs'
          : 'list'
    );

    ctrl.selectStep = function(name) {
        var step = ctrl.run().getStep(name);

        RunStepList.vm.setActive(step);

        ctrl.vm.showStepDetails(step);
        ctrl.vm.view('list');
    };


    ctrl.reload = function() {
        ctrl.run = Services.getPipeline(ctrl.id);
        ctrl.dag = Services.getDag(ctrl.id);
    };
    Observable.on(['pypers.rundetails.reload'], ctrl.reload);

    ctrl.getViewComponent = function() {
        if (ctrl.vm.view() === 'outputs'){
            return m.component(RunOutputs, {
                id: ctrl.id
            });
        }
        else if(ctrl.vm.view() === 'dag') {
            return m.component(PipelineDag, {
                mode: 'monitor',
                type: ctrl.run().name(),
                dag: ctrl.dag(),
                onnodeclick: ctrl.selectStep
            });
        }
        else {
            return m.component(RunDetailList, {
                run: ctrl.run()
            });
        }
    };

    // extend the dag from data in run
    m.sync([ctrl.run, ctrl.dag]).then(function(data) {
        var run = data[0];
        var dag = data[1];

        run.steps().map(function(step) {
            var jobs_status = {};

            if(step.status() === 'succeeded') {
                jobs_status = { 'succeeded': 100 };
            }
            else  {
                jobs_status = _.chain(step.jobs())
                               .pluck('status')
                               .countBy(function(e) {return e();})
                               .mapValues(function(v) { return (v/step.total()) * 100; })
                               .value();
            }

            jobs_status = _.assign({
                'succeeded': 0,
                'running': 0,
                'failed': 0
            }, jobs_status);

            // extending nodes
            // ---------------
            var node = _.find(dag.elements.nodes, function(node) {
                return node.data.name === step.name();
            });
            node.data.status = step.status(); // assign node status to easier identify queued ones
            _.assign(node.data, jobs_status);

            // extending edges
            // ---------------
            var edges = _.select(dag.elements.edges, function(edge) {
                return edge.data.source === step.name();
            });
            edges.map(function(edge) {
                if     (jobs_status.failed  > 0)       edge.data.failed    = true;
                else if(jobs_status.running > 0)       edge.data.running   = true;
                else if(jobs_status.succeeded === 100) edge.data.succeeded = true;
                else                                   edge.data.queued    = true;
            });

        });

        ctrl.dag(dag);
    });
};


RunDetailsPage.view = function(ctrl, args) {
    return (
        m.component(NesLayout, {
            menu: 'pipelines',
            breadcrumbs: function() {
                var bcrumbs = [];
                var isMine  = ctrl.run().user() === utils.user.get().sAMAccountName;
                if(ctrl.run().isStep()) {
                    bcrumbs.push({
                        label: (isMine? 'My': 'All') + ' Pipeline Runs',
                        link: '/runs/pipelines' + (isMine? '?user=' + ctrl.run().user() : '')
                    });
                    bcrumbs.push({
                        label: 'Step: ' + ctrl.run().name(),
                        link: '/runs/steps'
                    });
                }
                else {
                    bcrumbs.push({
                        label: (isMine? 'My': 'All') + ' Pipeline Runs',
                        link: '/runs/pipelines' + (isMine? '?user=' + ctrl.run().user() : '')
                    });
                    bcrumbs.push({
                        label: utils.pipeline.label(ctrl.run().name()),
                        link: '/runs/pipelines/' + ctrl.run().name()
                    });
                }
                bcrumbs.push({label: ctrl.id});

                return bcrumbs;
            }(),
            main: [
                m('.run-details', {class: 'view-'+RunDetailsPage.vm.view()},
                    m('a.view-switch.to-list', {
                            onclick: ctrl.vm.toggleView.bind(ctrl.vm, 'list')
                        },
                        m('i.fa', {class: 'fa-list'})
                    ),
                    function toDagLink() {
                        if(! ctrl.run().isStep()) {
                            return m('a.view-switch.to-dag', {
                                    onclick: ctrl.vm.toggleView.bind(ctrl.vm, 'dag')
                                },
                                m('i.fa', {class: 'fa-share-alt'})
                            );
                        }
                        else {
                            return null;
                        }
                    }(),
                    m('a.view-switch.to-outputs', {
                            onclick: ctrl.vm.toggleView.bind(ctrl.vm, 'outputs')
                        },
                        m('i.fa', {class: 'fa-files-o'})
                    ),
                    ctrl.getViewComponent()
                ),
                filePreview.view(filePreviewCtrl)
            ]
        })
    )
};


var RunDetailList = {
    view: function(ctrl, args) {
        var run = args.run;

        return (
            m('.details-container',
                m.component(RunHeader, { run: run }),
                m.component(RunStepList, {
                    run: run,
                    onselect:   function(step) { runStepJobListCtrl.reload(step); },
                    ondeselect: function()     { runStepJobFileListCtrl.reset(); runStepJobListCtrl.reset(); }
                }),
                runStepJobList.view(runStepJobListCtrl),
                runStepJobFileList.view(runStepJobFileListCtrl)
            )
        )
    }
};

var RunHeader = {
    controller: function(args) {
        var ctrl = this;

        ctrl.action = function(run, action) {
            run.action(action).then(
                function() {
                    if(action === 'delete') {
                        m.route('/runs?user=' + utils.user.get().sAMAccountName);
                    }
                    else {
                        Observable.trigger('pypers.rundetails.reload');
                    }
                }
            );
        };
    },
    view: function(ctrl, args) {
        var run = args.run;
        return (
            m('.run-header',
                function getAction() {
                    var mine = run.user() === utils.user.get().sAMAccountName;
                    if(! mine) return null;

                    switch(run.status()) {
                        case 'failed':
                            return m('.info--action.' + run.status(), m('a', {onclick: ctrl.action.bind(ctrl, run, 'delete')}, m('i.fa.fa-trash')));
                            break;
                        case 'running':
                            return m('.info--action.' + run.status(), m('a', {onclick: ctrl.action.bind(ctrl, run, 'pause')}, m('i.fa.fa-pause')));
                            break;
                        case 'interrupted':
                            return m('.info--action.' + run.status(), m('a', {onclick: ctrl.action.bind(ctrl, run, 'resume')}, m('i.fa.fa-play')));
                            break;
                        default: return null;
                    }
                }(),
                m('.info', m('.info-name', 'config:'), m('.info-value', m('a', {
                    target: '_blank',
                    href: '/api/fs/txt?path='+run.wdir() + '/pipeline.cfg'
                }, 'pipeline.cfg', m('i.fa fa-external-link')))),
                m('.info', m('.info-name', 'log:'), m('.info-value', m('a', {
                    target: '_blank',
                    href: '/api/fs/txt?path='+run.wdir() + '/pipeline.log'
                }, 'pipeline.log', m('i.fa fa-external-link')))),
                m('.info', m('.info-name', 'submitted by:'), m('.info-value', utils.user.description(run.user()))),
                m('.info', m('.info-name', 'submitted on:'), m('.info-value', run.createdAt())),

                m('.info', m('.info-name', 'project name:'), m('.info-value', run.meta().project_name)),
                m('.info', m('.info-name', 'project description:'), m('.info-value', run.meta().descr)),
                m('.info', m('.info-name', 'output directory:'), m('.info-value', {onclick: utils.misc.hiliteText}, m('span', run.dir()))),
                m('.info', m('.info-name', 'work directory:'), m('.info-value', {onclick: utils.misc.hiliteText}, m('span', run.wdir()))),

                m('.info', m('.info-name', 'execution time:'), m('.info-value', run.execTime())),
                m('.info', m('.info-name', 'ended on:'), m('.info-value', run.completedAt() || '...'))

            )
        );

    }
};


exports.view = RunDetailsPage.view
exports.controller = RunDetailsPage.controller

