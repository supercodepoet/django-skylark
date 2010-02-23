dojo.provide('RibtTools.TestRunner.Action.Wait');

dojo.require('RibtTools.TestRunner.Action.Base');

dojo.declare('RibtTools.TestRunner.Action.Wait', RibtTools.TestRunner.Action.Base, {
    _ms: undefined,

    constructor: function(ms) {
        this._ms = ms;
    },

    /**
     *
     */
    tick: function() {
        if (this._timerRunning) { return; }

        setTimeout(dojo.hitch(this, function() {
            this.finished = true;
        }), this._ms);

        this._timerRunning = true;
    }
});
