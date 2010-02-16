dojo.provide('RibtTools.SyncTimer');

dojo.require('dojox.timing');

dojo.declare('RibtTools.SyncTimer', null, {
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
            throw new RibtToolsError('You must provide an array to the RibtTools.SyncTimer constructor');
        }

        // Iterate through the stack, make sure each item is an instance of Unit
        dojo.forEach(stack, function(unit) {
            if (!unit.isInstanceOf || !unit.isInstanceOf(RibtTools.SyncTimer.Unit)) {
                throw new RibtToolsError('Each instance in the stack must be an RibtTools.SyncTimer.Unit');
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

        this._timeStarted = ribt.time();

        this._internalTimer.onTick = dojo.hitch(this, function() {
            if (this._fullStop) {
                this._internalTimer.stop();
                return;
            }

            // If we've been running to long, this timer needs to time out itself
            if (ribt.time() > (this._timeStarted + this._timeout)) {
                this._timedOut = true;
                if (this._running) {
                    this._running._synctimer_unit_state = RibtTools.SyncTimer.UnitState.TIMEOUT;
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
            this._timeFinished = ribt.time();

            if (this.onStop) {
                this.onStop(this);
            }
        });

        this._internalTimer.start();
    }
});

/**
 * States for the Units
 */
dojo.setObject('RibtTools.SyncTimer.UnitState', {
    NOT_RUNNING: 0,
    RUNNING: 1,
    TIMEOUT: 2
});

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
            throw new RibtToolsError('Unit run() method has not been called yet');
        }
        return ribt.time() - this._synctimer_timeStarted;
    }
});

/**
 * A single function that runs immediately, this is a wrapper to make that
 * function into a SyncTimer Unit
 */
dojo.declare('RibtTools.SyncTimer.UnitFunction', RibtTools.SyncTimer.Unit, {
    _synctimer_unitfunction_func: undefined,

    _synctimer_unitfunction_scope: undefined,

    constructor: function(func) {
        this._synctimer_unitfunction_func = func;

        if (arguments.length == 2) {
            // We have a scope too
            this._synctimer_unitfunction_scope = arguments[1];
        }
    },

    run: function() {
        if (this._synctimer_unitfunction_scope) {
            this._synctimer_unitfunction_func.call(
                this._synctimer_unitfunction_scope);
        } else {
            this._synctimer_unitfunction_func();
        }
        this.finished = true;
    }
});
