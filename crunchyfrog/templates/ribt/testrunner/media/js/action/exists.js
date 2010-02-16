dojo.provide('RibtTools.TestRunner.Action.Exists');

dojo.declare('RibtTools.TestRunner.Action.Exists', RibtTools.TestRunner.Action.Base, {
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
