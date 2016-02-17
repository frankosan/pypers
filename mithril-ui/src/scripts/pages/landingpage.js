var m = require('mithril'),
    _ = require('lodash');

var models = require('../models');

var utils = require('../utils');

var NesLayout  = require('../components/neslayout');

var RunsStats = {
    list: function(type) {
        return utils.request.background({
            method: 'GET',
            url: '/api/pypers/runs/' + type + '/stats',
            type: models.RunsStats,
            data: {user: utils.user.get().sAMAccountName},
            extract: utils.request.authenticate
        });
    }
};

var LandingPagePage = {
    controller: function() {
        var ctrl = this;

        ctrl.stats = RunsStats.list('pipelines');
        ctrl.stepStats = RunsStats.list('steps');

        ctrl.gotoRuns = function(filter) {
            m.route('/runs/' + _.compact([filter.type, filter.name]).join('/'), {
                status: filter.status,
                user: filter.user
            });
        };
    },
    view: function(ctrl) {
        return m.component(NesLayout, {
            menu: 'pipelines',
            header: 'Pypers Dashboard',
            breadcrumbs: [],
            main: !(ctrl.stats.ready() && ctrl.stepStats.ready())
                  ? m('.ajax-loading', m('i.fa fa-circle-o-notch fa-spin'))
                  : (!ctrl.stats.success()
                     ? m('.landing-page', m('.fa fa-ban'), ' Could not connect to server')
                     : m.component(RunsStatsList, {
                        stats: ctrl.stats.data,
                        stepsStats: ctrl.stepStats.data,
                        onclick: ctrl.gotoRuns
                    }))
        });
    }
};

var RunsStatsList = {
    controller: function() {
        var ctrl = this;

        ctrl.createNewRun = function(type) {
            m.route('/run/new/' + type);
        };

        ctrl.user = utils.user.get().sAMAccountName;
    },
    view: function(ctrl, args) {
        // view helpers
        _getPipelineIcon = function(stats) {
            if(stats.running()) return 'fa-cog running';
            if(stats.queued())  return 'fa-cog';
            else return '';
        };
        _getPipelineStat = function(type, name, stats, status, label, by_user) {
            var active = _.findIndex(status, function(s) {
                return stats[s]() > 0;
            });
            var total = _.sum(status, function(s) {
                return stats[s]();
            });

            filter = { type: type, name: name, status: status }
            if ( by_user ) {
                filter['user'] = ctrl.user;
            }

            return [
                m('.stat-detail', {
                        class: active > -1? 'active': '',
                        onclick: args.onclick.bind(this, filter)
                    },
                    m('em', total),
                    m('div',label)
                )
            ]
        };

        return (
            m('.landing-page',
            m('.row.pipeline-list.top',
                m('div.pipeline.col-md-3',
                    m('.pipeline-label',
                        m('a.active', {onclick: args.onclick.bind(ctrl, {type: 'all'})}, 'All Runs')
                    ),
                    m('.flex-row',
                        m('.pipeline-stat', [
                            m('.pipeline-label',
                                m('a.active', { onclick: args.onclick.bind(ctrl, {type: 'pipelines'}) }, 'Pipelines')
                            ),
                            _getPipelineStat('pipelines', '', args.stats().totals().stats(), ['queued'], 'queued'),
                            _getPipelineStat('pipelines', '', args.stats().totals().stats(), ['running'], 'running'),
                            _getPipelineStat('pipelines', '', args.stats().totals().stats(), ['interrupted'], 'interrupted'),
                            _getPipelineStat('pipelines', '', args.stats().totals().stats(), ['failed'], 'failed'),
                            _getPipelineStat('pipelines', '', args.stats().totals().stats(), ['succeeded'], 'succeeded'),
                            m('.stat-total', {
                                class: args.stats().totals().total()? 'active' : '',
                                onclick: args.onclick.bind(this, {
                                    type: 'pipelines',
                                    name: ''
                                })},
                                args.stats().totals().total() + ' total'
                            )
                        ]),
                        m('.pipeline-stat', [
                            m('.pipeline-label',
                                m('a.active', { onclick: args.onclick.bind(ctrl, {type: 'steps'}) }, 'Steps')



                            ),
                            _getPipelineStat('steps', '', args.stepsStats().totals().stats(), ['queued'], 'queued'),
                            _getPipelineStat('steps', '', args.stepsStats().totals().stats(), ['running'], 'running'),
                            _getPipelineStat('steps', '', args.stepsStats().totals().stats(), ['interrupted'], 'interrupted'),
                            _getPipelineStat('steps', '', args.stepsStats().totals().stats(), ['failed'], 'failed'),
                            _getPipelineStat('steps', '', args.stepsStats().totals().stats(), ['succeeded'], 'succeeded'),
                            m('.stat-total', {
                                class: args.stats().totals().total()? 'active' : '',
                                onclick: args.onclick.bind(this, {
                                    type: 'steps'
                                })},
                                args.stepsStats().totals().total() + ' total'
                            )
                        ])
                    )
                ),
                m('div.pipeline.col-md-3',
                    m('.pipeline-label',
                        m('a.active', {onclick: args.onclick.bind(ctrl, {type: 'all', user: ctrl.user})}, 'My Runs')
                    ),
                    m('.flex-row',
                        m('.pipeline-stat', [
                            m('.pipeline-label',
                                m('a.active', { onclick: args.onclick.bind(ctrl, {type: 'pipelines', user:ctrl.user}) }, 'Pipelines')
                            ),
                            _getPipelineStat('pipelines', '', args.stats().user().stats(), ['queued'], 'queued', 1),
                            _getPipelineStat('pipelines', '', args.stats().user().stats(), ['running'], 'running', 1),
                            _getPipelineStat('pipelines', '', args.stats().user().stats(), ['interrupted'], 'interrupted', 1),
                            _getPipelineStat('pipelines', '', args.stats().user().stats(), ['failed'], 'failed', 1),
                            _getPipelineStat('pipelines', '', args.stats().user().stats(), ['succeeded'], 'succeeded', 1),
                            m('.stat-total', {
                                class: args.stats().totals().total()? 'active' : '',
                                onclick: args.onclick.bind(ctrl, {
                                    type: 'pipelines',
                                    name: '',
                                    user: ctrl.user
                                })},
                                args.stats().totals().total() + ' total'
                            )
                        ]),
                        m('.pipeline-stat', [
                            m('.pipeline-label',
                                m('a.active', { onclick: args.onclick.bind(ctrl, {type: 'steps', user : ctrl.user}) }, 'Steps')
                            ),
                            _getPipelineStat('steps', '', args.stepsStats().user().stats(), ['queued'], 'queued', 1),
                            _getPipelineStat('steps', '', args.stepsStats().user().stats(), ['running'], 'running', 1),
                            _getPipelineStat('steps', '', args.stepsStats().user().stats(), ['interrupted'], 'interrupted', 1),
                            _getPipelineStat('steps', '', args.stepsStats().user().stats(), ['failed'], 'failed', 1),
                            _getPipelineStat('steps', '', args.stepsStats().user().stats(), ['succeeded'], 'succeeded', 1),
                            m('.stat-total', {
                                class: args.stepsStats().totals().total()? 'active' : '',
                                onclick: args.onclick.bind(this, {
                                    type: 'steps',
                                    user: ctrl.user
                                })},
                                args.stepsStats().totals().total() + ' total'
                            )
                        ])
                    )
                )
            ),
            m('.row.pipeline-list',
                args.stats().pipelines().map(function(pipeline) {
                    return  (
                        m('div.pipeline col-md-3',
                            m('.pipeline-label',
                                m('i.fa status', {class: _getPipelineIcon(pipeline.stats())}),
                                m('i.fa new fa-wrench[title=Create New Run]', {onclick: ctrl.createNewRun.bind(ctrl, pipeline.name())}),
                                m('a', {
                                    class: pipeline.total()? 'active' : '',
                                    onclick: args.onclick.bind(ctrl, {name: pipeline.name(), type: 'pipelines'})
                                }, utils.pipeline.label(pipeline.name()))
                            ),
                            m('.pipeline-stat', [
                                _getPipelineStat('pipelines', pipeline.name(), pipeline.stats(), ['queued'], 'queued'),
                                _getPipelineStat('pipelines', pipeline.name(), pipeline.stats(), ['running'], 'running'),
                                _getPipelineStat('pipelines', pipeline.name(), pipeline.stats(), ['interrupted'], 'interrupted'),
                                _getPipelineStat('pipelines', pipeline.name(), pipeline.stats(), ['failed'], 'failed'),
                                _getPipelineStat('pipelines', pipeline.name(), pipeline.stats(), ['succeeded'], 'succeeded'),
                            ]),
                            m('.stat-total', {
                                class: pipeline.total()? 'active' : '',
                                onclick: args.onclick.bind(this, {name: pipeline.name()})
                            },  pipeline.total() + ' executions')
                        )
                    )
                }),
                function ghostBlocks() {
                    var ghosts = [];
                    var delta = (3 - (args.stats().pipelines().length % 3)) % 3;
                    while(delta--) {
                       ghosts.push(m('div.pipeline.col-md-3.ghost'));
                    }
                    return ghosts;
                }()
             ))
        );
    }
};

exports.view = LandingPagePage.view;
exports.controller = LandingPagePage.controller;
