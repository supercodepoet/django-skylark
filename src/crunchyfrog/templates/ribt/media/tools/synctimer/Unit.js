dojo.provide('RibtTools.SyncTimer.Unit');

dojo.require('RibtTools.Error');
dojo.require('RibtTools.SyncTimer.UnitState');

/**
 * Represents one unit of work for the sync timer.
 *
 * The sync timer will not continue until the unit says finished=true
 */
dojo.declare('RibtTools.SyncTimer.Unit', null, {
    // We always want this run to run
    '-chains-': {
        run: 'after'
    },

    constructor: function() {
        this._synctimer_unit_state = RibtTools.SyncTimer.UnitState.NOT_RUNNING;
        this._synctimer_timeStarted = undefined;
        this.finished = false;
    },

    /**
     *
     */
    run: function() {
        if (this._synctimer_timeStarted == undefined) {
            this._synctimer_timeStarted = ribt.time();
        }
        this._synctimer_unit_state = RibtTools.SyncTimer.UnitState.RUNNING;
    },

    /**
     *
     */
    timePassed: function() {
        if (!this._synctimer_timeStarted) {
            throw new RibtTools.Error('Unit run() method has not been called yet');
        }
        return ribt.time() - this._synctimer_timeStarted;
    }
});
