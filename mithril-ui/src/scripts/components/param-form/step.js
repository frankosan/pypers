
var m = require('mithril'),
    $ = require('jquery'),
    _ = require('lodash');

var models = require('../../models');

var utils      = require('../../utils'),
    Observable = require('../../utils/observable');

var Param       = require('./param');
    FileBrowser = require('../file-browser');

var fileBrowser     = m.component(FileBrowser, {onclose: function() {StepFormVM.browsing = false}});
var fileBrowserCtrl = new fileBrowser.controller();

var StepFormVM = {
    browsing: '',        // used to show/hide the file browser modal

    init: function() {
        StepFormVM.browsing = '';
        Observable.on(['pypers.run.new.param.browse'], StepFormVM.browse);
    },

    onunload: function() {
        Observable.off(['pypers.run.new.param.browse'], StepFormVM.browse);
    },

    browse: function(args) {
        var parts = args.root.split(':');

        StepFormVM.browsing = args.root;
        window.setTimeout(function() {
            fileBrowserCtrl.init(parts[1], parts[0], args.multiple, args.target, args.selection);
        }, 0);
    }
};


var Step = {
    config: function(group, step) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/steps/' + group + '.' + step,
            extract: utils.request.authenticate,
            type: models.StepConfig
        });
    }
};

var StepForm = {
    controller: function(args) {
        var ctrl = this;

        // make sure that the browser window is closed

        // prepping the submit data
        ctrl.data = m.prop({});
        ctrl.selection = m.prop('');
        ctrl.config = m.prop(new models.StepConfig());

        // massaging the config data
        ctrl.inputs  = m.prop([]);
        ctrl.outputs = m.prop([]);
        ctrl.params  = m.prop([]);
        ctrl.meta    = m.prop({});

        ctrl.fetch = function(group, step) {
            ctrl.clear();
            ctrl.selection(group + '.' + step);

            Step.config(group, step).then(function(data) {
                ctrl.config(data);
                // initializing submit data with default values in
                // the config params
                ['inputs', 'params'].map(function(ptype) {
                    ctrl.config()[ptype]().map(function(p) {
                        ctrl.data()[p.name()] = p.value();
                    });
                });
            });
        };

        ctrl.error = function(obj) {
            ctrl.config().error(obj);
        };

        ctrl.clear = function() {
            ctrl.data({});
            ctrl.selection('');
            ctrl.config(new models.StepConfig());
        };

        // handles the browse of file and dir params
        ctrl.browse = function(root, target) {
            var parts = root.split(':');

            fileBrowserCtrl.init(parts[1], parts[0], target);
            StepFormVM.browsing = root;
        };

        ctrl.submit = function() {
            (args.submit || function() {})(ctrl.config().name(), ctrl.selection(), ctrl.data());
        };

        // handling the onfocus of every input
        ctrl.onfocus = function(e) {
            // First deactivate any step info
            // var active_info = $('ul.param-list').find('.step-desc.show').parents('.step-header').find('i.doc');
            // if (active_info != undefined) { ctrl.onclick(active_info); }
            var elt = $(e.target);
            window.setTimeout(function() {
                elt.parents('.param-input').find('.param-desc').addClass('show').css({top: elt.offset().top + 41 + 'px'});
                elt.parents('.param-input').addClass('focus');
            }, 0);
        };
        // handling the onblur of every input
        ctrl.onblur = function(e) {
            var elt = $(e.target);
            window.setTimeout(function() {
                elt.parents('.param-input').find('.param-desc').removeClass('show');
                elt.parents('.param-input').removeClass('focus');
            }, 0);
        };
        ctrl.setfocus = function(elt, isInit) {
            if(isInit) return;
            $(elt).on('focus', 'input, select', ctrl.onfocus);
            $(elt).on('blur',  'input, select', ctrl.onblur);
        };

        // handling the onchange of every input
        ctrl.onchange = function(e) {
            var name  = e.target.getAttribute('name');
            var type  = e.target.getAttribute('type');
            var mult  = e.target.getAttribute('data-mult');
            var value = e.target.value;

            switch(type) {
                case 'number':   value = value? parseFloat(value): value; break;
                case 'checkbox': value = e.target.checked; break;
                default:         value = value; break; // select included here
            }
            if(mult === 'true') {
                value = value.split(',');
            }

            ctrl.data()[name] = value;
            ctrl.config().update(name, value); // update to remove the error
        };

        StepFormVM.init();
        ctrl.onunload = function() {
            StepFormVM.onunload();
        };
    },
    view: function(ctrl, args) {
        var config = ctrl.config();
        return (
            m('.step-form', {
                    class: [
                        StepFormVM.browsing ? 'browsing' : '',
                        !ctrl.selection()   ? 'hidden'   : ''
                    ].join(' ')
                },
                m('.header-1', ctrl.selection(),
                    m('em.version', 'v. ' + config.version()),
                    config.url()? m('a.link', {href: config.url(), target: '_blank'}, m('i.fa.fa-external-link')): null
                 ),
                m('form[name="param-form"]', {
                        onsubmit: function() {return false;},
                        onchange: ctrl.onchange,
                        config:   ctrl.setfocus
                    },
                    // m.component(MessageBox, {
                    //     status: args.status
                    // }),
                    m('.step-details',
                        m('.header-2', config.desc()),
                        m('.header-3', 'Step Input'),
                        m.component(ParamList, {
                            params : config.inputs(),
                            data   : ctrl.data(),
                            filter : '*'
                        }),
                        m('.header-3', 'Step Configuration'),
                        m.component(ParamList, {
                            params : config.params(),
                            data   : ctrl.data(),
                            filter : '*'
                        }),
                        m('.header-3', 'Step Output'),
                        m('ul.output-list-details', config.outputs().map(function(o) {
                            return m('li', o.type + ': ' + o.name + ' (' + o.descr + ')');
                        })),
                        function displayCmdLine() {
                            if(config.cmd()) {
                                return [
                                    m('.header-3', 'Step CmdLine'),
                                    m('code.cmdline', m('pre', config.cmd()))
                                ];
                            }
                            return null;
                        }()
                    ),
                    m('.submit-bar',
                      m('button.btn btn-primary btn-submit', {
                          type: 'submit',
                          onclick: ctrl.submit
                      }, 'Start Step')
                    )
                ),
                fileBrowser.view(fileBrowserCtrl)
             )
        );

    }
};


// loops thru the params in the config and displays each
var ParamList = {
    view: function(ctrl, args) {
        return (
            m('ul.param-list-details',
                // pipeline params
                m('.group-label',
                    args.params.map(function(param) {
                        return m.component(Param, {
                            param  : param,
                            data   : args.data[param.name()],
                            filter : args.filter
                        });
                    })
                )
            )
        );
    }
};


exports.view = StepForm.view;
exports.controller = StepForm.controller;

