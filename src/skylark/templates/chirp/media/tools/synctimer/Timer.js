dojo.provide('ChirpTools.SyncTimer.Timer');

dojo.require('dojox.timing');
dojo.require('ChirpTools.Error');
dojo.require('ChirpTools.SyncTimer.Unit');
dojo.require('ChirpTools.SyncTimer.UnitState');

dojo.declare('ChirpTools.SyncTimer.Timer', null, {
    // The amount of time between runs or ticks
    _interval: 50,

    // 20 second timeout for running this synctimer
    _timeout: 20000,

    // When was the start() method called
    _timeStarted: undefined,

    // When did the timer finish
    _timeFinished: undefined,

    // Did the timer time out?
    _timedOut: false,

    // The stack of things that are waiting to be ran
    _stack: [],

    // The current Unit instance that is running
    _running: undefined,

    // The stack of Units that have finished running
    _ran: [],

    // Setting this to try stops any additional actions from being performed
    _fullStop: false,

    // Callback that will be used when the timer finishes (either completes
    // all it's units or times out)
    onStop: undefined,

    // Callback that will receive an error object if an exception is caught from
    // any of the units
    onException: undefined,

    // Callback that will be called directly before the run method
    // is called on the unit
    beforeRun: undefined,

    // Callback that is called directly after the run method of a unit
    afterRun: undefined,

    /**
     * @constructor
     * @param stack Must be an array of things that can be ran()
     */
    constructor: function(stack) {
        if (!dojo.isArray(stack)) {
            throw new ChirpTools.Error('You must provide an array to the ChirpTools.SyncTimer.Timer constructor');
        }

        // Iterate through the stack, make sure each item is an instance of Unit
        dojo.forEach(stack, function(unit) {
            if (!unit.isInstanceOf || !unit.isInstanceOf(ChirpTools.SyncTimer.Unit)) {
                throw new ChirpTools.Error('Each instance in the stack must be an ChirpTools.SyncTimer.Unit');
            }
        });

        this._stack = stack;
    },

    /**
     * Set the interval
     *
     * @param ms Number of milliseconds to wait before runs
     */
    interval: function(ms) {
        this._interval = ms;
    },

    /**
     * Set the timeout
     *
     * @param ms Number of milliseconds to wait before this timer times out
     */
    timeout: function(ms) {
        this._timeout = ms;
    },

    /**
     * Tells the timer to put on the brakes completely, don't do anything else
     */
    fullStop: function() {
        if (arguments.length > 0) {
            this._fullStop = arguments[0];
        } else {
            return this._fullStop;
        }
    },

    /**
     * Gets the units that have been successfully ran
     */
    getUnitsRan: function() {
        return this._ran;
    },

    /**
     * Start running through the stack of units, running each one until they
     * report they have finished before moving on to the next one.
     *
     * This simulates synchronous events in Javascript
     *
     * It's up to the Unit instance to tell the SyncTimer when it's finished
     * (by settings it's internal attribute finished = true.
     */
    start: function() {
        this._internalTimer = new dojox.timing.Timer(this._interval);

        this._timeStarted = chirp.time();

        this._internalTimer.onTick = dojo.hitch(this, function() {
            if (this._fullStop) {
                this._internalTimer.stop();
                return;
            }

            // If we've been running to long, this timer needs to time out itself
            if (chirp.time() > (this._timeStarted + this._timeout)) {
                this._timedOut = true;
                if (this._running) {
                    this._running._synctimer_unit_state = ChirpTools.SyncTimer.UnitState.TIMEOUT;
                }
                this._internalTimer.stop();
                return;
            }

            if (this._running) {
                // If the running unit is finished, we'll push it to the _ran stack
                // and reset things for the next one
                if (this._running.finished) {
                    if (dojo.isFunction(this.afterRun)) {
                        this.afterRun(this, this._running);
                    }
                    this._ran.push(this._running);
                    this._running = undefined;
                    return
                }
                // At this point, we could pull the next unit off the stack and run
                // it, but this would make our timing a little bumpy.  So we return
                // and allow another tick on the interval
                return;
            }

            // If our stack is empty, we are done
            if (this._stack.length == 0) {
                this._internalTimer.stop();
                return;
            }

            // Ok, we are ready to run a unit
            this._running = this._stack.splice(0, 1)[0];
            try {
                if (dojo.isFunction(this.beforeRun)) {
                    this.beforeRun(this, this._running);
                }
                this._running.run();
            } catch(e) {
                if (dojo.isFunction(this.onException)) {
                    this.onException(e);
                    this.fullStop(true);
                }
            }
        });

        this._internalTimer.onStop = dojo.hitch(this, function() {
            this._timeFinished = chirp.time();

            if (this.onStop) {
                this.onStop(this);
            }
        });

        this._internalTimer.start();
    }
});
