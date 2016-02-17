var m = require('mithril');

var ParamEnum = {
    view: function(ctrl, args) {
        return (
            m('select.form-control', {
                'name'      : args.param.name(),
                'value'     : args.data,
                'required'  : args.param.required(),
                'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
                'data-step' : args.step || ''
            },
            args.param.options().map(function(o) {
                return m('option', {selected: o === args.param.value()}, o);
            }))
        );
    },
};

exports.view = ParamEnum.view;
