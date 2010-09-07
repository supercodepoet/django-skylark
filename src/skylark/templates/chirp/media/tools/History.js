dojo.provide('ChirpTools.Mvc.History');

dojo.require('dojo.back');
dojo.require('ChirpTools.Error');

dojo.setObject('ChirpTools.Mvc.History', {
    _history: [],

    registerTravel: function(context, travel) {
        if (typeof travel != 'string') {
            throw new ChirpTools.Error('Options for goesBackOrForwards must be a string');
        }

        travelMethod = this._wrap_method(context, context[travel]);
        context[travel] = travelMethod;
    },

    _navigate: function(index) {
        var obj = ChirpTools.Mvc.History._history[index];
        if (obj) {
            obj.originalMethod.apply(obj.context, obj.arguments);
            ChirpTools.Mvc.History._restoreInitial(index + 1);
        }
    },

    /**
     * Looks through the history for target, if from the index backwards this is
     * the last time we see it we need to call restoreInitialState on the object
     * to get things back to the beginning.
     */
    _restoreInitial: function(index) {
        var history = ChirpTools.Mvc.History._history;
        if (!history[index]) { return; }
        var context = history[index].context;
        // If it's zero, no need to go through the loop
        if (index == 0) {
            context._restoreInitialState();
            return true;
        }

        var obj;
        for (var i = index; i >= 0; i--) {
            obj = history[i].context;
            if (obj == context) {
                // It's not the last time we'll see this context in the history,
                // so we aren't going to restore
                return false;
            }
        }

        // Making it here means that we didn't find any other instance of the
        // context in the history items below it.  This means that it needs to
        // be restored to initial state.
        context._restoreInitialState();
        return true;
    },

    _wrap_method: function(context, originalMethod) {
        return function() {
            var history = ChirpTools.Mvc.History._history;

            history.push({
                'originalMethod': originalMethod,
                'context':        context,
                'arguments':      arguments
            });

            var histContext = {
                'arguments': arguments,
                'index':     history.length - 1
            };

            var navigateFunction = dojo.hitch(histContext, function() {
                ChirpTools.Mvc.History._navigate(histContext.index);
            });

            dojo.back.addToHistory({
                back: navigateFunction,
                forward: navigateFunction,
                changeUrl: true
            });

            ChirpTools.Mvc.History._history = history
            originalMethod.apply(context, arguments);
        }
    }
});

dojo.addOnLoad(
    function() {
        dojo.back.setInitialState({
            back: function() {
                var history = ChirpTools.Mvc.History._history;
                if (history[0]) {
                    ChirpTools.Mvc.History._restoreInitial(0);
                }
            },
            forward: function() {
                var history = ChirpTools.Mvc.History._history;
                if (history[0]) {
                    ChirpTools.Mvc.History._navigate(0);
                }
            },
            changeUrl: false
        });
    }
);
