var m = require('mithril');

var utils  = require('../utils');

var NesLayout   = require('../components/neslayout'),
    PipelineDag = require('../components/pipeline-dag'),
    ParamForm   = require('../components/param-form');


var Pipeline = {
    config: function(type, data) {
        data = data || {};

        this.name = m.prop(type);

        this.config = m.request({
            method: 'GET',
            url: '/api/pypers/pipelines/' + type + '/config',
            extract: utils.request.authenticate
        });
    },
    dag: function(type) {
        return m.request({
            method: 'GET',
            url: '/api/pypers/pipelines/' + type + '/dag',
            extract: utils.request.authenticate
        });
    }
};


var PipelinePage = {
    controller: function() {
        var ctrl = this;

        ctrl.type   = m.route.param('type');
        ctrl.params = m.prop(new Pipeline.config(ctrl.type));
        ctrl.dag    = Pipeline.dag(ctrl.type);

        ctrl.status = m.prop({code: -1});

        ctrl.submit = function(data) {
            // client side validation
            // if(! document.forms['param-form'].checkValidity()) return;
            document.forms['param-form'].noValidate = true; // skip client side validation

            // sanitize data to match backend expectations
            var obj = { dag: { load: ctrl.type } };
            // var obj = { dag: { load: 'pypers/pipelines/rnaseq.json' } };
            obj.config = data;
            // delete obj.config.pipeline.refgenome;
            //

            m.request({
                method: 'PUT',
                url: '/api/pypers/pipelines/submit',
                data: {
                    config: obj,
                    user : utils.user.get().sAMAccountName
                },
                extract: utils.request.authenticate
            }).then(
            function(response) {
                ctrl.status({
                    code: 200,
                    message: response
                });
                window.setTimeout(function() {
                    m.route('/runs/pipelines', {user: utils.user.get().sAMAccountName});
                }, 3000);
            },
            function(errorObj) {
                ctrl.status({
                    code: 400,
                    errors: errorObj
                });
            });
        };

        ctrl.scroll = function(step) {
            var elt = $('.group-label.step-'+step);
            if(elt.length) {
                var focused = $('.param-input.focus').find('.form-control').get(0);
                // remove focus from previous input
                if(focused) {
                    focused.blur();
                }

                var delta = elt.offset().top - 100;
                $('ul.param-list').animate({
                    scrollTop: '+=' + delta
                }, Math.max(0, Math.abs(delta/2) - 300),
                // animation complete
                function() {
                    var inpt = elt.find('i.doc');
                    if(inpt) {
                        inpt.click();
                    }
                });
            }
        };
    },
    view: function(ctrl) {
        return (
            m.component(NesLayout, {
                menu: 'pipelines',
                breadcrumbs: [{label: utils.pipeline.label(ctrl.type) + ' Pipeline'}],
                main: [
                    m('.run-form-container',
                        m('.run-dag',
                            m.component(PipelineDag, {
                                mode: 'new',
                                type: ctrl.type,
                                dag: ctrl.dag(),
                                onnodeclick: ctrl.scroll
                            })
                        ),
                        m.component(ParamForm, {
                            type  : ctrl.type,
                            config: ctrl.params().config(),
                            submit: ctrl.submit,
                            status: ctrl.status()
                        })
                    )
                ]
            })
        );
    }
};

exports.view       = PipelinePage.view
exports.controller = PipelinePage.controller

