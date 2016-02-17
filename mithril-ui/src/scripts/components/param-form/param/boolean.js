var m = require('mithril');

var ParamBoolean = {
    view: function(ctrl, args) {
        return  m('input.form-control.chb[type=checkbox]', {
            'name'      : args.param.name(),
            'checked'   : args.data,
            'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
            'data-step' : args.step || ''
        });
    }
};

exports.view = ParamBoolean.view;



