var m = require('mithril');

var Param = {
    'int'        : require('./int'),
    'float'      : require('./float'),
    'boolean'    : require('./boolean'),
    'str'        : require('./str'),
    'dir'        : require('./dir'),
    'file'       : require('./file'),
    'enum'       : require('./enum'),
    'ref_genome' : require('./ref_genome'),
    'readonly'   : require('./readonly'),

    view: function(ctrl, args) {
        var param = args.param;

        return (
            m('li.pipeline-run-param', {
                class: param.required()
                       ? 'required'
                       : args.filter === '*'
                         ? 'optional'
                         : 'hidden'
                },
                m('.param', {class: param.error()? 'has-error': ''},
                    m('.param-name', {
                        class: param.required() && args.data === '' || args.data.length === 0? 'missing': '',
                    }, param.name() + (param.required()? ' *': '')),
                    param.readonly()
                    ? m('.param-input',  m.component(
                        Param['readonly'], {
                            filter : args.filter,
                            param  : param,
                            step   : args.step,
                            data   : args.data  // value of param in that is bound to the submit object
                        }),
                        m('.param-desc', m('.param-value', {},  '['+param.type()+'] ' + args.data), param.descr()))

                    : [ m('.param-error', param.error()),
                        m('.param-input', m.component(
                            Param[param.type()], {
                                filter : args.filter,
                                param  : param,
                                step   : args.step,
                                data   : args.data  // value of param in that is bound to the submit object
                            }
                            ),
                            m('.param-desc', m('.param-value', {},  '['+param.type()+'] ' + args.data), param.descr())
                        )
                      ]
                )
            )
        );
    }
};

exports.controller = Param.controller;
exports.view = Param.view;

