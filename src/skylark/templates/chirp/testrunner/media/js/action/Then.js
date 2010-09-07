dojo.provide('RibtTools.TestRunner.Action.Then');

dojo.require('RibtTools.TestRunner.Action.Base');

dojo.declare('RibtTools.TestRunner.Action.Then', RibtTools.TestRunner.Action.Base, {
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
