var m = require('mithril');

var ParamFloat = {
    view: function(ctrl, args) {
        return  m('input.form-control[type=number]', {
            'name'      : args.param.name(),
            'value'     : args.data,
            'required'  : args.param.required(),
            'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
            'step'      : args.param.precision(),
            'data-step' : args.step || ''
        });
    }
};

exports.view = ParamFloat.view;

