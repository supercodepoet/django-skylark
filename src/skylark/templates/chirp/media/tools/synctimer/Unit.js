dojo.provide('ChirpTools.SyncTimer.Unit');

dojo.require('ChirpTools.Error');
dojo.require('ChirpTools.SyncTimer.UnitState');

/**
 * Represents one unit of work for the sync timer.
 *
 * The sync timer will not continue until the unit says finished=true
 */
dojo.declare('ChirpTools.SyncTimer.Unit', null, {
    // We always want this run to run
    '-chains-': {
        run: 'after'
    },

    constructor: function() {
        this._synctimer_unit_state = ChirpTools.SyncTimer.UnitState.NOT_RUNNING;
        this._synctimer_timeStarted = undefined;
        this.finished = false;
    },

    /**
     *
     */
    run: function() {
        if (this._synctimer_timeStarted == undefined) {
            this._synctimer_timeStarted = chirp.time();
        }
        this._synctimer_unit_state = ChirpTools.SyncTimer.UnitState.RUNNING;
    },

    /**
     *
     */
    timePassed: function() {
        if (!this._synctimer_timeStarted) {
            throw new ChirpTools.Error('Unit run() method has not been called yet');
        }
        return chirp.time() - this._synctimer_timeStarted;
    }
});
