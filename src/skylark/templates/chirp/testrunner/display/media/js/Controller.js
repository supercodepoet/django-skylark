dojo.provide('ChirpTools.TestRunner.Display.Controller');

dojo.require('ChirpTools.Mvc.Controller');
dojo.require('ChirpTools.SyncTimer.Timer');
dojo.require('ChirpTools.TestRunner.Display.View');
dojo.require('ChirpTools.TestRunner.Events');
dojo.require('ChirpTools.TestRunner.Channel');

/**
 * Responsible for starting everything.  Creates the top bar and window where the
 * tests happen
 */
dojo.declare('ChirpTools.TestRunner.Display.Controller', ChirpTools.Mvc.Controller, {
    /**
     * Time to wait between running test entry points
     */
    _waitInterval: 250,

    /**
     * When do we timeout all running tests?
     */
    _timeout: 60000,

    /**
     * The number of tests we plan on running
     */
    testCount: 0,

    /**
     * The first page we navigate to after loading
     */
    initialUrl: '',

    /**
     * What URL do we POST to when we wish to de-instrument the site
     */
    urlDeinstrument: '',

    /**
     * Instances of test entry points
     */
    _testEntryPoints: [],

    /**
     * The currently running test entry point
     */
    _runningTestEntryPoint: undefined,

    /** 
     * The ran test entry points
     */
    _ranTestEntryPoints: [],

    /**
     * Has this been deinstrumented already?
     */
    _isDeinstrumented: false,

    /**
     * @constructor
     */ 
    constructor: function(domNode) {
        // Get our basic user-facing display setup
        this.view = new ChirpTools.TestRunner.Display.View(domNode);
        this.view.setSubjectSize();
        this.view.showAll();

        // The channel is how we communicate with the other frame
        this.channel = ChirpTools.TestRunner.Channel;
        this.channel.setSubject(this.view.subjectFrame);

        // We need to wait until the subject frame is ready before we talk to it
        dojo.subscribe(ChirpTools.TestRunner.Events.SubjectFrame.Ready, this, this.notifyTestCount);
        dojo.addOnUnload(this, this.deinstrumentSite);

        // Our entry points are interned in the page as the following object
        // We initialize our test entry points, creating new instances of the specififed item
        this.initTestEntryPoints(ChirpTools.TestRunner.TestEntryPoints.items);

        // Now that they exist, we want to show them in the top bar
        this.view.showTestEntryPoints(this._testEntryPoints);

        // Events from the test runners top section
        // These are the controls that adjust test execution
        this.subscribe(ChirpTools.TestRunner.Events.Display.RunClick, this, this.kickoffTestEntryPoints);
        this.subscribe(ChirpTools.TestRunner.Events.Display.RunOneClick, this, this.kickoffTestEntryPoints);

        // And finally, let's show something in the subject frame
        this.channel.navigate(this.initialUrl);
    },

    /**
     * Take the urls and names that we have interned in the page and create
     * actual TestEntryPoint instances
     *
     * @param data An array with urls and names of test entry points
     */ 
    initTestEntryPoints: function(data) {
        dojo.forEach(data, function(rawTep) {
            var tepInstance = new ChirpTools.TestRunner.Display.TestEntryPoint(
                rawTep.url, rawTep.name);

            tepInstance.channel(this.channel);

            this._testEntryPoints.push(tepInstance);
        }, this);
    },

    /**
     * When we are done testing, or when we leave the test runner, we need to
     * de-instrument (take it out of testing mode).  This URL will do that for us
     */
    deinstrumentSite: function() {
        if (this.isDeinstrumented) {
            // No need to do it twice
            return;
        }

        dojo.xhrPost({
            url: this.urlDeinstrument,
            sync: true
        });
        this.isDeinstrumented = true;
    },

    /**
     * Starts the process of navigating to each url and allowing the tests
     * to run
     */
    kickoffTestEntryPoints: function() {
        if (arguments.length > 1) {
            // If argument passed in, it will be just one TEP to run
            var toRun = [ arguments[0] ];
        } else {
            var toRun = this._testEntryPoints;
        }

        var st = new ChirpTools.SyncTimer.Timer(toRun);

        st.onStop = dojo.hitch(this, function(syncTimer) {
            var testEntryPoints = syncTimer.getUnitsRan();
            var results = [];

            var context = { 
                scope: this,
                results: results
            }

            dojo.forEach(testEntryPoints, dojo.hitch(context, function(tep) {
                var result = {
                    failures: this.scope._extractFailures(tep),
                    passes: this.scope._extractPasses(tep),
                    testEntryPoint: tep
                }
                this.results.push(result);
            }));

            this.view.displayResults(results);

            this.deinstrumentSite();
        });

        st.interval(this._waitInterval);
        st.timeout(this._timeout);

        st.start();
    },

    /**
     * Goes through the test entry point units (actions) and extracts
     * the assertions called type
     *
     * @param units Array
     * @param type Either '_failures' or '_passed'
     */
    _extractAssertions: function(units, type) {
        var context = {
            scope: this,
            assertions: []
        };

        dojo.forEach(units, dojo.hitch(context, function(unit) {
            if (unit.assert) {
                // We have assertions
                this.assertions = this.assertions.concat(unit.assert[type]);
            }
        }));

        return context.assertions;
    },

    /**
     * Extracts failures from the test entry point
     *
     * @param testEntryPoint
     */
    _extractFailures: function(testEntryPoint) {
        return this._extractAssertions(testEntryPoint.collectedTestCases(), '_failures');
    },

    /**
     * Extracts passes from the test entry point
     *
     * @param testEntryPoint
     */
    _extractPasses: function(testEntryPoint) {
        return this._extractAssertions(testEntryPoint.collectedTestCases(), '_passes');
    },

    /**
     * Notifies how many test entry points are available fro running
     */ 
    notifyTestCount: function() {
        this.channel.publish(ChirpTools.TestRunner.Events.TestCount, [ this.testCount ]);
    }
});
