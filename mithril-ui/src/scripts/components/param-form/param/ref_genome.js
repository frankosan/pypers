var m = require('mithril');

var ParamRefGenome = {
    view: function(ctrl, args) {
        return  m('input.form-control[type=text]', {
            'required'  : args.param.required(),
            'data-step' : args.step || '',
            'value'     : args.data,
            'tabIndex'  : !args.param.required() && args.filter === 'required'? -1: 0,
            'readonly'  : true
        });
    }
};

exports.view = ParamRefGenome.view;

