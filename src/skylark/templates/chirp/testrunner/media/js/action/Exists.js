dojo.provide('ChirpTools.TestRunner.Action.Exists');

dojo.require('ChirpTools.TestRunner.Action.Base');

dojo.declare('ChirpTools.TestRunner.Action.Exists', ChirpTools.TestRunner.Action.Base, {
    /**
     * 
     */
    constructor: function(query) {
        this._query = query;
    },

    /**
     *
     */
    tick: function() {
        if (this.when(this._query)) {
            this.assert.pass('Found ' + this._query);
            this.finished = true;
        }
    }
});
