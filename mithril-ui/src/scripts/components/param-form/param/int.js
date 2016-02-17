var m = require('mithril');

var ParamInt = {
    view: function(ctrl, args) {
        return  m('input.form-control[type=number]', {
            'name'      : args.param.name(),
            'required'  : args.param.required(),
            'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
            'value'     : args.data,
            'data-step' : args.step || ''
        });
    }
};

exports.view = ParamInt.view;
