dojo.provide('RibtTools.TestRunner.Action.Base');

dojo.declare('RibtTools.TestRunner.Action.Base', RibtTools.SyncTimer.Unit, {
    _interval: 50,
    _timeout: 5000,

    isTimeout: function() {
        if (this.timePassed() > this._timeout) {
            return true;
        }
        return false;
    },

    /**
     * Looks for an element on the page, return true if found
     */
    when: function(query) {
        if (dojo.query(query).length > 0) {
            return true;
        }
        return false;
    },

    run: function() {
        if (!this.tick) {
            throw new RibtToolsError('No tick method available on ' + this.declaredClass);
        }

        if (!this.finished) {
            this.tick();

            if (this.finished) {
                return;
            }
        }

        if (this.isTimeout()) {
            this.assert.fail('Timeout in ' + this.declaredClass);
            this.finished = true;
            return;
        }

        if (!this.finished) {
            setTimeout(dojo.hitch(this, this.run), this._interval);
        }
    }
});
