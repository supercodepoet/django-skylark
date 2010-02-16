dojo.provide('RibtTools.TestRunner.Action.When');

dojo.declare('RibtTools.TestRunner.Action.When', RibtTools.TestRunner.Action.Base, {
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
