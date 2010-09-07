dojo.provide('ChirpTools.TestRunner.Action.When');

dojo.require('ChirpTools.TestRunner.Action.Base');

dojo.declare('ChirpTools.TestRunner.Action.When', ChirpTools.TestRunner.Action.Base, {
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
            this.finished = true;
        }
    }
});
