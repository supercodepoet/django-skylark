dojo.provide('ChirpTools.TestRunner.TestCaseCollector');

dojo.require('ChirpTools.Error');
dojo.require('ChirpTools.SyncTimer.Timer');
dojo.require('ChirpTools.TestRunner.Events');
dojo.require('ChirpTools.TestRunner.Logger');

/**
 * Functions within the subject, and collects test cases that should be
 * ran
 *
 * This object is a singleton, and gets created at the end
 */
dojo.declare('_ChirpTools.TestRunner.TestCaseCollector', null, {
    /**
     * How long between ticks
     */
    _interval: 50,
    
    /**
     * How long before we time out
     */
    _timeout: 35000,

    /**
     * Just the test names, as registered when the page loaded in
     */
    _testCaseNames: [],

    /**
     * Actual classes (not instances) of tests cases
     */
    _testCaseObjects: [],

    /**
     * If we are being ran with the test runner, we could have a test entry point available
     */
    _testEntryPoint: undefined,

    /**
     * Do we require that a test entry point be present before we continue?
     */
    _requireTestEntryPoint: false,

    /**
     * How long should we wait for a test entry point before failing?
     */
    _waitForTestEntryPoint: 500,

    /**
     * The collected logs from the test cases
     */
    _log: ChirpTools.TestRunner.Logger,

    /**
     * The assertions from the test cases
     */
    _assertions: [],

    /**
     * True if we detect we are being ran through a test runner
     */
    _withinTestRunner: function() {
        try {
            if (window.parent.ChirpTools.TestRunner.TestEntryPoints) {
                return true;
            }
        } catch (e) {
            // pass
        }

        return false;
    },

    /**
     * @constructor
     */
    constructor: function() {
        this._started = chirp.time();

        if (this._withinTestRunner()) {
            this._requireTestEntryPoint = true;
            dojo.subscribe(ChirpTools.TestRunner.Events.Running, this, function(testEntryPoint) {
                this._testEntryPoint = testEntryPoint;
            });
        }

        this._ready = true;
    },

    /**
     * Create the test case instances
     */
    kickoff: function() {
        // By this time, the add method has been called and provided with the names of
        // the test cases we wish to run
        if (this._testCaseNames.length == 0) {
            // We have no test cases to run
            return;
        }

        if (!this._requireTestEntryPoint) {
            // We don't require a test entry point, there is no reason to wait for
            // it.  Let's just start running the tests
            this._startTestCases();
            return;
        }

        if (this._requireTestEntryPoint) {
            // Because we are running within a test runner, we require a test entry point
            if (chirp.time() > (this._waitForTestEntryPoint + this._started)) {
                // We have ran out of time
                this._log.critical('Cannot run tests, we do not have a test entry point and there is an indication that one is required');
                return;
            }

            if (this._testEntryPoint) {
                // We have a test entry point now, we can continue
                this._startTestCases();
                return;
            }

            // We aren't timed out, we don't have the test entry point let's wait a bit
            // and call kickoff again
            setTimeout(dojo.hitch(this, this.kickoff), this._waitInterval);
        }
    },

    /**
     * Begins running the tests
     */
    _startTestCases: function(){
        try {
            // Take the names of the test cases, and create instances of them
            dojo.forEach(this._testCaseNames, function(testCaseName) {
                var cls = dojo.getObject(testCaseName);

                if(!dojo.isFunction(cls)){
                    throw new ChirpTools.Error("Could not load test case class '" + className);
                }

                this._testCaseObjects.push(new cls(this._testEntryPoint));
            }, this);
            
            // Create a new sync timer with the test cases within
            var st = new ChirpTools.SyncTimer.Timer(this._testCaseObjects);

            st.interval(this._interval);
            st.timeout(this._timeout);

            st.afterRun = dojo.hitch(this, this.afterRun);
            st.onStop = dojo.hitch(this, this.onStop);

            st.start();
        } catch (e) {
            debugger;
            this._log.info('Exception while collecting test cases: ' + e.message);
        }
    },

    /**
     * After each test case runs, we arrive here
     *
     * @param syncTimer Instance of ChirpTools.SyncTimer.Timer
     * @param unit The test action that just finished running
     */
    afterRun: function(syncTimer, unit) {
        this._assertions.push(unit.assert);

        // If the internal sync timer for the test has gone to a full stop
        // state, we need to stop this one too
        if (unit._syncTimer.fullStop()) {
            syncTimer.fullStop(true);
        }
    },

    /**
     * When all of the test cases finish, we provide the units that were ran
     * to the test entry point for later use displaying the results
     *
     * @param syncTimer Instance of ChirpTools.SyncTimer.Timer
     */
    onStop: function(syncTimer) {
        if (this._testEntryPoint) {
            this._testEntryPoint.collectedTestCases(syncTimer.getUnitsRan());
        }
    },

    /**
     * Add a string test case name to be tested
     *
     * @param testCaseName A string, representing a test case that can be instantiated
     */
    add: function(testCaseName) {
        this._testCaseNames.push(testCaseName);
    }
});

dojo.setObject('ChirpTools.TestRunner.TestCaseCollector',
    new _ChirpTools.TestRunner.TestCaseCollector);
