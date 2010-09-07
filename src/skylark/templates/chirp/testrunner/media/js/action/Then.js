dojo.provide('ChirpTools.TestRunner.Action.Then');

dojo.require('ChirpTools.TestRunner.Action.Base');

dojo.declare('ChirpTools.TestRunner.Action.Then', ChirpTools.TestRunner.Action.Base, {
    _callback: undefined,

    constructor: function(callback) {
        this._callback = callback;
    },

    /**
     *
     */
    tick: function() {
        this._callback();
        this.finished = true;
    }
});
