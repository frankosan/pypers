var m = require('mithril');

var ParamStr = {
    view: function(ctrl, args) {
        return  m('input.form-control[type=text]', {
            'name'      : args.param.name(),
            'required'  : args.param.required(),
            'value'     : args.data,
            'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
            'data-step' : args.step || ''
        });
    }
};

exports.view = ParamStr.view;


