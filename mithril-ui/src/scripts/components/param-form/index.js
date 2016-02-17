var m = require('mithril'),
    $ = require('jquery'),
    _ = require('lodash');

var models = require('../../models');

var utils      = require('../../utils'),
    Observable = require('../../utils/observable');

var Param       = require('./param');
    FileBrowser = require('../file-browser');

var fileBrowser     = m.component(FileBrowser, {onclose: function() {ParamFormVM.browsing = false}});
var fileBrowserCtrl = new fileBrowser.controller();

var ParamFormVM = {
    browsing: '',        // used to show/hide the file browser modal
    filter: m.prop('*'), // *|required

    init: function() {
        ParamFormVM.browsing = '';
        Observable.on(['pypers.run.new.param.browse'], ParamFormVM.browse);
    },

    onunload: function() {
        Observable.off(['pypers.run.new.param.browse'], ParamFormVM.browse);
    },

    browse: function(args) {
        var parts = args.root.split(':');

        ParamFormVM.browsing = args.root;
        window.setTimeout(function() {
            fileBrowserCtrl.init(parts[1], parts[0], args.multiple, args.target, args.selection);
        }, 0);
    },

    toggleView: function() {
        ParamFormVM.filter(ParamFormVM.filter() === '*'? 'required': '*');
    }
};

var ParamForm = {
    controller: function(args) {
        var ctrl = this;

        // prepping the submit data
        ctrl.data = m.prop({
            pipeline: {},
            steps: {}
        });

        // massaging the config data
        ctrl.params = m.prop({
            refgenomes: {},
            pipeline: [],
            steps: []
        });

        ctrl.params().refgenomes = args.config.pipeline.refgenomes || {};
        // initializing submit data with default values in
        // the config params
        ctrl.params().pipeline = args.config.pipeline.params.map(function(param) {
            var param = new models.Param(param);
            ctrl.data().pipeline[param.name()] = param.value();
            return param;
        });

        var ordered = _.reject(args.config.steps_order, function(s) {
            return args.config.steps[s] === undefined;
        });
        ctrl.params().steps = ordered.map(function(k) {
            ctrl.data().steps[k] = {};
            var step = args.config.steps[k] || {};
            var params = (step.params || []).concat(step.inputs || []).map(function(param) {
                var param = new models.Param(param);
                ctrl.data().steps[k][param.name()] = param.value();
                return param;
            });
            return { "params": params, "name": k, "info": {"descr": step.descr, "url": step.url} };
        });

        // handles the browse of file and dir params
        ctrl.browse = function(root, target) {
            var parts = root.split(':');

            fileBrowserCtrl.init(parts[1], parts[0], target);
            ParamFormVM.browsing = root;
        };

        ctrl.submit = function() {
            (args.submit || function() {})(ctrl.data());
        };

        // handling the onclick of the step info button
        ctrl.onclick = function(e) {
            var elt = $(e.target); // Expects i.doc by default, but also parent 'step-header'
            var active = $('ul.param-list').find('.step-desc.show').parents('.step-header').find('i.doc');
            window.setTimeout(function() {
                if (elt.attr('data-step') !== active.attr('data-step')) {
                    active.parents('.step-header').find('.step-desc').toggleClass('show');
                    active.parents('.step-header').toggleClass('focus');
                    Observable.trigger('pypers.run.new.param.blur', {
                        step: active.attr('data-step')
                    });
                }
                elt.parents('.step-header').find('.step-desc').toggleClass('show');
                elt.parents('.step-header').toggleClass('focus');
                Observable.trigger('pypers.run.new.param.focus', {
                    step: elt.attr('data-step')
                });
            }, 0);
        };
        // handling the onfocus of every input
        ctrl.onfocus = function(e) {
            // First deactivate any step info
            var active_info = $('ul.param-list').find('.step-desc.show').parents('.step-header').find('i.doc');
            if (active_info != undefined) { ctrl.onclick(active_info); }
            var elt = $(e.target);
            window.setTimeout(function() {
                elt.parents('.param-input').find('.param-desc').addClass('show');
                elt.parents('.param-input').addClass('focus');

                Observable.trigger('pypers.run.new.param.focus', {
                    step: elt.attr('data-step')
                });
            }, 0);
        };
        // handling the onblur of every input
        ctrl.onblur = function(e) {
            var elt = $(e.target);
            window.setTimeout(function() {
                elt.parents('.param-input').find('.param-desc').removeClass('show');
                elt.parents('.param-input').removeClass('focus');

                Observable.trigger('pypers.run.new.param.blur', {
                    step: elt.attr('data-step')
                });
            }, 0);
        };
        ctrl.setfocus = function(elt, isInit) {
            if(isInit) return;
            $(elt).on('click', 'i[class~="doc"]', ctrl.onclick);
            $(elt).on('blur',  'div[class~="info-header focus"]', ctrl.onclick);
            $(elt).on('focus', 'input, select', ctrl.onfocus);
            $(elt).on('blur',  'input, select', ctrl.onblur);
        };

        // handling the onchange of every input
        ctrl.onchange = function(e) {
            var step  = e.target.getAttribute('data-step');
            var name  = e.target.getAttribute('name');
            var type  = e.target.getAttribute('type');
            var mult  = e.target.getAttribute('data-mult');
            var value = e.target.value;

            var isRefGenome      = name === '_REFGENOMES_';
            var isPipelineParam  = !isRefGenome && step === '';
            var isStepParam      = !isRefGenome && step !== '';

            switch(type) {
                case 'number':   value = value? parseFloat(value): value; break;
                case 'checkbox': value = e.target.checked; break;
                default:         value = value; break; // select included here
            }
            if(mult === 'true') {
                value = _.compact(value.split(','));
            }

            if(isStepParam) {
                ctrl.data().steps[step][name] = value;
            }
            else
            if(isPipelineParam) {
                ctrl.data().pipeline[name] = value;
            }
            else
            if(isRefGenome) {
               ctrl.data().pipeline.refgenome = value;
               _.each(ctrl.params().refgenomes[value], function(params, step) {
                    _.each(params, function(val, name) {
                        ctrl.data().steps[step][name] = val;
                    });
                });
            }
        };

        ParamFormVM.init();
        ctrl.onunload = function() {
            ParamFormVM.onunload();
        };
    },
    view: function(ctrl, args) {
        return (
            m('.run-form', {class: ParamFormVM.browsing? 'browsing': ''},
                m('form[name="param-form"]', {
                        onsubmit: function() {return false;},
                        onchange: ctrl.onchange,
                        config:   ctrl.setfocus
                    },
                    m('a.filter',  {onclick: ParamFormVM.toggleView, class: ParamFormVM.filter() === 'required'? 'active': ''}, m('i.fa fa-filter')),
                    m.component(MessageBox, {
                        status: args.status
                    }),
                    m.component(ParamList, {
                        params : ctrl.params(),
                        data   : ctrl.data(),
                        filter : ParamFormVM.filter()
                    }),

                    m('.submit-bar',
                      m('button.btn btn-primary btn-submit', {
                          type: 'submit',
                          onclick: ctrl.submit
                      }, 'Start Run')
                    )
                ),
                fileBrowser.view(fileBrowserCtrl)
             )
        );

    }
};

var MessageBox = {
    view: function(ctrl, args) {
        return (
            m('.form-message', {
                    class: args.status.code < 0
                            ? 'hidden'
                            : args.status.code === 200
                                ? 'success'
                                : 'error'
                },
                args.status.code < 0
                ? ''
                : args.status.code === 200
                  ? m('.message', args.status.message)
                  : m.component(ErrorList, args.status.errors)
            )
        );
    }
};

var ErrorList = {
    controller: function(args) {
        var ctrl = this;

        ctrl.jump = function(step, param) {
            var elt = $('.group-label.'+step+' .param-input *[name='+param+']');
            if(elt.length) {
                elt.get(0).focus();
            }
        };
    },
    view: function(ctrl, args) {
        return (
            m('table.error-list',
                _.map(args.pipeline, function(v, k) {
                    return m('tr', {onclick: ctrl.jump.bind(ctrl, 'pipeline', k)},
                                   m('td.pname[colspan=2]', k + ' : '),
                                   m('td.txt', v)
                           );
                }),
                _.map(args.steps, function(e, s) {
                    return _.map(e, function(v, k) {
                        return m('tr', {onclick: ctrl.jump.bind(ctrl, 'step-'+s, k)},
                                       m('td.sname', '[' + s + ']'),
                                       m('td.pname', k + ' : '),
                                       m('td.txt', v)
                               );
                    });
                })
            )
        );
    }
};

// loops thru the params in the config and displays each
var ParamList = {
    view: function(ctrl, args) {
        return (
            m('ul.param-list',
                // pipeline params
                m('.group-label.pipeline',
                    args.params.pipeline.map(function(param) {
                        return m.component(Param, {
                            param  : param,
                            data   : args.data.pipeline[param.name()],
                            filter : args.filter
                        });
                    }),
                    // global ref genomes selection
                    function() {
                        if(! _.isEmpty(args.params.refgenomes)) {
                            return m.component(RefGenomes, {
                                list: args.params.refgenomes,
                                data: args.data.pipeline.refgenome
                            });
                        }
                        return null;
                    }()
                ),
                // steps params
                args.params.steps.map(function(step) {
                    return (
                        m('.group-label.step-'+step.name,
                            m('.step-header',
                                m('.label', step.name),
                                (step.info.url ?   m('a.doc fa fa-external-link',
                                                        { href: step.info.url, target: "_blank" }
                                                    )
                                               : ''
                                ),
                                (step.info.descr != undefined
                                    ? m('i.doc fa fa-info-circle', {'data-step': step.name}) : ''),
                                m('.step-desc',
                                        m('.info-header',
                                            m('.step-name', '['+step.name+'] ')
                                            //m('.fa fa-times')
                                         ),
                                        step.info.descr != undefined ? step.info.descr.join('\n') : ''
                                        //m('.fa fa-times')
                                )
                            ),
                            step.params.map(function(param) {
                                return m.component(Param, {
                                    param  : param,
                                    step   : step.name,
                                    data   : args.data.steps[step.name][param.name()],
                                    filter : args.filter
                                });
                            })
                         )
                    );
                })
            )
        );
    }
};


// display refgenomes on the pipeline level
var RefGenomes = {
    view: function(ctrl, args) {
        return (
            m('li.pipeline-run-param', {class: 'required'},
                m('.param',
                    m('.param-name', {
                        class: !args.data? 'missing': ''
                    }, 'ref_genome *'),
                    m('.param-input',
                        m('select.form-control', {
                                'name'      : '_REFGENOMES_',
                                'data-step' : '' // it's pipeline wide
                            },
                            m('option', {value: ''}, '--- choose ---'),
                            _.map(args.list, function(v, k) {
                                    return m('option', {value: k}, k);
                            })
                        )
                    )
                )
            )
        );
    }
};


exports.view = ParamForm.view;
exports.controller = ParamForm.controller;
