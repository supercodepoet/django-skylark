dojo.provide('ChirpTools.TestRunner.Action.Wait');

dojo.require('ChirpTools.TestRunner.Action.Base');

dojo.declare('ChirpTools.TestRunner.Action.Wait', ChirpTools.TestRunner.Action.Base, {
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
