var Pagination = {
    controller: function(args) {
        total  = args.total;
        offset = args.offset || 0;
        limit  = args.limit  || 5;

        // returns an array of page numbers
        // [1, 2, 3 ...]
        _calculatePages = function() {
            return _.range(1, Math.ceil(total/ctrl.limit()) + 1)
        };

        var ctrl = this;
        ctrl.page  = m.prop(offset/limit + 1);
        ctrl.limit = m.prop(limit);
        ctrl.pages = m.prop(_calculatePages());

        ctrl.doflip = function(page) {
            ctrl.page(page);

            args.onflip({
                offset: ctrl.limit() * page - ctrl.limit(),
                limit: ctrl.limit()
            });
        };
        ctrl.dolimit = function(limit) {
            args.onlimit({
                limit: ctrl.limit(limit),
                offset: 0
            });
            ctrl.pages(_calculatePages());
        };
    },
    view: function(ctrl, args) {
        return m('div',
            ctrl.pages().map(function(page) {
                _css = ctrl.page() === page? 'pagination--link__number active': 'pagination--link__number';
                return m('a', {onclick: ctrl.doflip.bind(this, page), css: _css}, page);
            }),
            m('select', {value: ctrl.limit(), onchange: m.withAttr('value', ctrl.dolimit)},
                [5, 10, 25, 50].map(function(limit) {
                    return m('option', {value: limit}, limit);
                })
            )
        );
    }
};


