var m = require('mithril');

var ParamReadonly = {
    view: function(ctrl, args) {
        return  m('input.form-control[type=text].readonly', {
            'required'  : args.param.required(),
            'data-step' : args.step || '',
            'value'     : args.data,
            'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
            'readonly'  : true
        });
    }
};

exports.view = ParamReadonly.view;

