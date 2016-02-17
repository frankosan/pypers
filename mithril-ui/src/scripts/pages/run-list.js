var m = require('mithril'),
    _ = require('lodash'),
    fuzzy = require('fuzzy');

var models = require('../models');

var utils      = require('../utils'),
    Observable = require('../utils/observable');

var NesLayout  = require('../components/neslayout');

Observable.on(['pypers.rundetails.load'], function(args) {
    m.route('/run/'+args.id);
});

var Run = {
    count: function(filter) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/runs/' + filter.type + '/count',
            extract: utils.request.authenticate,
            data: filter
        });
    },
    list: function(filter) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/runs/' + filter.type,
            data: filter,
            extract: utils.request.authenticate,
            type: models.Run
        });
    }
};


var RunListPage = {};

RunListPage.vm = {
    view: m.prop('blocks'),

    // run card that is performing an action
    // (delete/pause/resume)
    inAction: m.prop(-1),

    // infinite scrolling props
    hasMore: m.prop(false),
    appending: m.prop(false),

    toggleView: function(id, view) {
        this.view(view || (this.view() === 'blocks'? 'list': 'blocks'));
    },

    // depends on the state of the page
    // -> All Runs? My Runs? Pre-filtered by run name?
    getBreadCrumbs: function() {
        var bcrumbs = [];
        var runType = m.route.param('type');
        var runName = m.route.param('name');
        var isMine  = m.route.param('user') === utils.user.get().sAMAccountName;
        var runStatus = m.route.param('status');
        var isSteps = runType === 'steps';

        if(runType === 'steps') {
            bcrumbs.push({
                label: (isMine? 'My': 'All') + ' Step Runs',
                link: '/runs/steps' + (isMine? '?user=' + m.route.param('user') : '')
            });

            bcrumbs.push({
                label: m.route.param('status') || 'All'
            });

            bcrumbs.push({
                label: m('i.fa fa-wrench'),
                title: 'Create New Step Run',
                css: 'create-link',
                link: '/steps'
            });

            return bcrumbs;
        }

        if(runType === 'pipelines') {
            bcrumbs.push({
                label: (isMine? 'My': 'All') + ' Pipeline Runs',
                link: '/runs/pipelines' + (isMine? '?user=' + m.route.param('user') : '')
            });

            if(runName) {
                bcrumbs.push({
                    label: utils.pipeline.label(runName),
                    link: '/runs/pipelines/' + runName
                });
                bcrumbs.push({
                    label: m('i.fa fa-wrench'),
                    title: 'Create New '+runName+' Run',
                    css: 'create-link',
                    link: '/run/new/' + m.route.param('name')
                });
            }

            bcrumbs.push({
                label: m.route.param('status') || 'All'
            });

            return bcrumbs;
        }

        if(runType === 'all') {
            bcrumbs.push({
                label: (isMine? 'My': 'All') + ' Steps & Pipeline Runs',
                link: '/runs/all' + (isMine? '?user=' + m.route.param('user') : '')
            });
        }

        return bcrumbs;
    }
};

RunListPage.controller = function() {
    var ctrl = this;
    ctrl.vm = RunListPage.vm;

    var filter = {
        type   : m.route.param('type'),
        status : m.route.param('status'),
        name   : m.route.param('name'),
        user   : m.route.param('user')
    };

    ctrl.page = {offset: 0, limit: 50};

    ctrl.count = Run.count(filter);
    ctrl.runs  = Run.list(_.assign(filter, ctrl.page));

    ctrl.moreRuns = function() {
        if(RunListPage.vm.appending()) return;

        var moreElt = document.getElementById('more');
        if(moreElt && utils.misc.isElementInViewport(moreElt)) {
            RunListPage.vm.appending(true);
            ctrl.append({
                offset: ctrl.page.offset + ctrl.page.limit,
                limit: ctrl.page.limit
            });
            if(ctrl.page.offset + ctrl.page.limit >= ctrl.count()) {
                Observable.off(['pypers.content.scroll'], ctrl.moreRuns);
                window.setTimeout(function() {
                    document.getElementById('more').remove();
                }, 0);
            }
        }
    };
    Observable.on(['pypers.content.scroll'], ctrl.moreRuns);

    ctrl.reload = function() {
        ctrl.count = Run.count(filter);
        ctrl.runs  = Run.list(_.assign(filter, ctrl.page));
    };
    Observable.on(['pypers.runlist.reload'], ctrl.reload);

    ctrl.append = function(args) {
        ctrl.page = {offset: args.offset, limit: args.limit};
        Run.list(_.assign(filter, ctrl.page)).then(function(data) {
            RunListPage.vm.appending(false);
            ctrl.runs(ctrl.runs().concat(data))
        });
    };
};

RunListPage.view = function(ctrl, args) {
    RunListPage.vm.hasMore(ctrl.count() > ctrl.page.offset + ctrl.page.limit);
    return m.component(NesLayout, {
        menu: 'pipelines',
        breadcrumbs: ctrl.vm.getBreadCrumbs(),
        main: [
            // !ctrl.runs.ready()
            // ? m('.ajax-loading', m('i.fa fa-circle-o-notch fa-spin')) :
            m.component(RunList, {runs: ctrl.runs, onmore: ctrl.moreRuns})
        ]
    });
};


var RunList = {
    controller: function(){
        var ctrl = this;
        ctrl.vm = RunListPage.vm;
        ctrl.searchVal = m.prop('');
    },
    view: function(ctrl, args) {
        return (
            m('.runs-list ' + ctrl.vm.view(),
                m('div',
                    m('input.search-bar', {
                        'class': ctrl.searchVal()? 'open': '',
                        'value': ctrl.searchVal(),
                        'placeholder': 'Search',
                        onkeyup : m.withAttr('value', ctrl.searchVal)
                    })
                ),
                m('a.view-switch', { onclick: ctrl.vm.toggleView.bind(ctrl.vm) },
                    m('i.fa', {class: ctrl.vm.view() === 'list'? 'fa-th': 'fa-bars'})
                ),
                args.runs().map(function(run) {
                    searchItems = [
                        'Run ' + String(run.id()),
                        run.createdAt(),
                        utils.user.description(run.user()),
                        run.meta()['project_name'],
                        run.meta()['descr'],
                        run.name()
                    ]

                    if (fuzzy.filter(ctrl.searchVal(), searchItems).length) {
                        return m.component(RunCard, {run: run});
                    }
                }),

                RunListPage.vm.hasMore() ? m('#more.more-link',  m('i.fa', {
                    class: RunListPage.vm.appending()? 'fa-circle-o-notch fa-spin': 'fa-chevron-down',
                    onclick: args.onmore
                }))
                : null
            )
        );
    }
};

var RunCard = {
    controller: function(args) {
        var ctrl = this;

        ctrl.action = function(run, action, event) {
            RunListPage.vm.inAction(run.id());

            var doTheAction = function() {
                run.action(action).then(
                    function() {
                        RunListPage.vm.inAction(-1);
                        Observable.trigger('pypers.runlist.reload');
                    },
                    function() {
                        RunListPage.vm.inAction(-1);
                    }
                );
            };

            window.setTimeout(doTheAction, 200);

            // to stop propagation
            if(event) {
                event.returnValue = false;
                event.stopPropagation();
                event.preventDefault();
            }
            return false;
        };

        ctrl.onclick = function(runId, e) {
            if(e && e.returnValue === false) return;

            Observable.trigger('pypers.rundetails.load', {
                id: runId
            });
        };
    },
    view: function(ctrl, args) {

        var run  = args.run;
        var mine = run.user() === utils.user.get().sAMAccountName;
        var updn = run.id()   === RunListPage.vm.inAction();  // is the run "in action" (updating its status)
        var perc = (run.stats().succeeded.length + run.stats().running.length) / Math.max(run.stats()['total'], 1) * 100; // do not divide by zero
            perc = perc.toFixed(0);

        return (
            m('.run.' + run.status(), {
                onclick: ctrl.onclick.bind(ctrl, run.id(), event),
                class: [mine? 'run__mine': '', updn? 'run__updn': ''].join(' '),
                id: 'run-' + run.id()
            },
                m('.run-header',
                    m('.run-id', run.id()),
                    function getRunLabel() {
                        var runType = m.route.param('type');
                        if(run.isStep()) {
                            return m('.run-type', m('span', run.name()));
                        }
                        else {
                            return m('.run-type', m('span', utils.pipeline.label(run.name())));
                        }
                        return null;
                    }(),
                    m('.run-header-info',
                        m('.run-date', run.createdAt()),
                        m('.run-user', utils.user.description(run.user())),
                        m('.run-jobs-stats', run.doneJobs() + ' job(s) completed')
                    ),
                    m('.run-status',
                        function() {
                            switch(run.status()) {
                                case 'queued':
                                    return m('i.fa.fa-ellipsis-h');
                                case 'interrupted':
                                    return [
                                        m('i.fa.fa-exclamation'),
                                        mine
                                            ? m('i.fa.fa-play', {onclick: ctrl.action.bind(ctrl, run, 'resume', event)})
                                            : null
                                    ];
                                case 'running':
                                    return [
                                        m('.run-perc', perc+'%'),
                                        mine
                                            ? m('i.fa.fa-pause', {onclick: ctrl.action.bind(ctrl, run, 'pause', event)})
                                            : null
                                    ];
                                case 'failed':
                                    return [
                                        m('i.fa.fa-flag'),
                                        mine
                                            ? m('i.fa.fa-trash', {title: 'trash run', onclick: ctrl.action.bind(ctrl, run, 'delete', event)})
                                            : null
                                    ];
                                case 'succeeded':
                                    return m('i.fa.fa-check');
                            }
                        }()
                    )
                ),
                m('.run-progress-bar', {class: 'meter blue' + (run.status() !== 'running'? ' nostripes': '')},
                    m('span', {style: {width: perc + '%'}})
                ),
                m('.run-body',
                    m('.run-metas',
                        m('.project-name',  run.meta().project_name),
                        m('.project-desc',  m('span', run.meta().descr)),
                        m('.time-infos',
                            m('.time-info',
                                m('i.fa fa-clock-o'),
                                m('span', run.execTime())
                            ),
                            m('.time-info',
                                m('i.fa', {
                                    class: run.status().toLowerCase() === 'succeeded'? 'fa-calendar-check-o' :
                                           run.status().toLowerCase() === 'failed'   ? 'fa-calendar-times-o' : ''
                                }),
                                m('span', run.completedAt())
                            )
                        )
                    ),
                    m('.run-jobs-info', ['queued', 'running', 'interrupted', 'failed', 'succeeded'].map(function(status) {
                        return m('.run-job-info', {class: 'info-' + run.stats()[status].length + ' info-' + status},
                                    m('em', run.stats()[status].length),
                                    ' ' + status
                               );
                    }))
                ),
                m('.run-updn-layer', {onclick: function() { return false; }}, m('i.fa.fa-spinner.fa-spin'))
            )
        );
    }
};

exports.view = RunListPage.view;
exports.controller = RunListPage.controller;
