dojo.provide('ChirpTools.SyncTimer.UnitFunction');

dojo.require('ChirpTools.SyncTimer.Unit')

/**
 * A single function that runs immediately, this is a wrapper to make that
 * function into a SyncTimer Unit
 */
dojo.declare('ChirpTools.SyncTimer.UnitFunction', ChirpTools.SyncTimer.Unit, {
    _synctimer_unitfunction_func: undefined,

    _synctimer_unitfunction_scope: undefined,

    constructor: function(func) {
        this._synctimer_unitfunction_func = func;

        if (arguments.length == 2) {
            // We have a scope too
            this._synctimer_unitfunction_scope = arguments[1];
        }
    },

    run: function() {
        if (this._synctimer_unitfunction_scope) {
            this._synctimer_unitfunction_func.call(
                this._synctimer_unitfunction_scope);
        } else {
            this._synctimer_unitfunction_func();
        }
        this.finished = true;
    }
});
