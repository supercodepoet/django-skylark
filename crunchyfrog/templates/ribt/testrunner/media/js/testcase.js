dojo.provide('RibtTools.TestRunner.TestCase');

/**
 *
 */
dojo.setObject('RibtTools.TestRunner.TestCaseMvcInstances', {
    /**
     *
     */
    addMvcInstance: function(instance) {
        RibtTools.TestRunner.TestCaseMvcInstances.instances.push(instance);
    },

    instances: []
});

dojo.subscribe(RibtTools.Mvc.Events.New.Controller, RibtTools.TestRunner.TestCaseMvcInstances.addMvcInstance);
dojo.subscribe(RibtTools.Mvc.Events.New.View, RibtTools.TestRunner.TestCaseMvcInstances.addMvcInstance);

dojo.declare('RibtTools.TestRunner.TestCase', null, {
    // Between ticks of the timer, how long should we wait
    _waitInterval: 150,
    
    // How long should a test take before it times out
    _testTimeout: 10000,

    // How long should this entire set of tests run before giving up?
    _allTestsTimeout: 120000,

    // Get's set to true if during the test runs the timeout is reached
    _reachedAllTestsTimeout: false,
    
    // Holds all the TestCaseAssertion objects each test creates as it runs
    _testResults: {},

    // Holds the names of the tests that still need to be ran
    _testQueue: [],

    // The number of expected actions
    _expectedActions: 0,
    
    // The number of actions that have been currently ran
    _ranActions: 0,

    // A list of actions that need to be ran to complete the test
    _actions: [],

    // A shortcut to the list of available MVC Controllers and Views
    _mvcInstances: [],

    // Message that this test has generated while running
    _log: [],

    //Is there currently a test running?
    running: false,

    /**
     * Set up method, ran once before the tests start
     */
    setUp: function() {
        // Implement your own to do something useful
    },

    /**
     * Tear down ran at the very end
     */
    tearDown: function() {
        // Implement your own to do something useful
    },

    constructor: function() {
        this.setUp();

        this.reset();

        this._testResults = {};
        this._mvcInstances = RibtTools.TestRunner.TestCaseMvcInstances.instances;

        // Find our tests
        for (var member in this) {
            if (member.indexOf('test') == 0) {
                if (typeof this[member] != 'function') { continue; }
                this._testQueue.push(member);
            }
        }

        this.runTests();
        this.tearDown();
    },

    reset: function() {
        // We have no assertion object
        this.assert = undefined;
        // We are not running a test at the moment
        this.running = false;
        // Reset expected assertions for the next test
        this._expectedActions = 0;
        // There are no actions curently to run
        this._actions = [];
        // We have not ran any actions yet
        this._ranActions = 0;
    },


    getController: function(name) {
        if (typeof name == 'object') {
            throw new RibtToolsError('Cannot use an object to retrive an MVC instance, use the string version of the name instead');
        }

        var context = { scope: this, name: name, toReturn: [] };

        dojo.forEach(this._mvcInstances, function(instance) {
            if (this.name == instance.declaredClass) {
                // We have a winner
                this.toReturn.push(instance);
            }
        }, context);

        return context.toReturn;
    },

    runTests: function() {
        try {
            var timer = new dojox.timing.Timer(this._waitInterval);
            timer.started = ribt.time();
            timer.timeout = this._allTestsTimeout;

            var context = {
                scope: this,
                timer: timer
            };

            timer.onTick = dojo.hitch(context, function() {
                if (!this.scope.assert) {
                    this.scope.assert = new RibtTools.TestRunner.TestCaseAssertions();
                    this.scope.assert.testcase = this.scope;
                }

                if ((ribt.time() - this.timer.started) > this.timer.timeout) {
                    this._reachedAllTestsTimeout = true;
                    timer.stop();
                }

                if (this.scope.running) {
                    var ranActions = this.scope._ranActions;
                    var expectedActions = this.scope._expectedActions;
                    var actions = this.scope._actions;

                    if (expectedActions == ranActions) {
                        // We know we've accomplished all of our assertions
                        this.scope.log('Closing down ' + this.scope.running);
                        this.scope.done();
                    } else {
                        // Let's see if we need to run an action
                        if (actions.length + ranActions == expectedActions) {
                            // Yep, let's splice one off and spin it up
                            var actionPair = actions.splice(0, 1)[0];
                            this.scope.log('Running action ' + actionPair[0]);
                            actionPair[1].call(this.scope);
                        }
                    }

                    return;
                }

                // All tests are finished loading, nothing to do but stop our timer
                if (this.scope._testQueue.length == 0) {
                    timer.stop();
                    return;
                }

                var methodName = this.scope._testQueue.splice(0,1)[0];
                var test = this.scope[methodName];

                this.scope.running = methodName;
                this.scope.log('Running test: ' + this.scope.running);
                test.call(this.scope);
            });

            timer.onStop = dojo.hitch(this, function() {
                dojo.publish(RibtTools.TestRunner.Events.TestFinished, [
                    this._testResults,
                    this._log
                ]);
            });

            timer.start();
        } catch (e) {
            throw e
        }
    },

    log: function(message) {
        if (console.debug) {
            console.debug(message);
        }
        this._log.push(message);
    },

    done: function() {
        this._testResults[this.running] = this.assert;
        this.reset();
    },

    /**
     *
     */
    addAction: function(name, func) {
        // We are adding an action to perform
        this._expectedActions++;
        this._actions.push([name, func]);
    },

    /**
     *
     */
    when: function(query, succeed, failure) {
        var timer = new dojox.timing.Timer(this._waitInterval);
        timer.started = ribt.time();
        timer.timeout = arguments[3] || this._testTimeout;

        var context = {
            scope: this,
            succeed: succeed,
            failure: failure,
            timer: timer,
            query: query
        };

        timer.onTick = dojo.hitch(context, function() {
            if ((ribt.time() - this.timer.started) > this.timer.timeout) {
                this.failure.call(this.scope, []);
                timer.stop();
            }
            if (dojo.query(this.query).length > 0) {
                this.succeed.call(this.scope, []);
                timer.stop();
            }
        });

        timer.start();
    },

    /**
     *
     */
    then: function(callback) {
        this.addAction('next', function() {
            this._ranActions++;
            callback.call(this);
        });
    },

    /**
     * Make sure that an item exists
     */
    exists: function(query) {
        this.addAction(query + ' exists', function() {
            this.when(query,
            function() {
                this._ranActions++;
                this.assert.pass('Found query ' + query);
            },
            function() {
                this._ranActions++;
                this.assert.fail('Did not find ' + query);
            });
        });
    }
});

dojo.declare('RibtTools.TestRunner.TestCaseAssertions', null, {
    _failures: [],
    _passes: [],

    /**
     *
     */
    fail: function(message) {
        this.testcase.log('Fail ' + message);
        this._failures.push(message);
    },

    /**
     *
     */
    pass: function(message) {
        this.testcase.log('Pass ' + message);
        this._passes.push(message);
    }
});
