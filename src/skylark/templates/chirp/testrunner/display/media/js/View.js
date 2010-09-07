dojo.provide('ChirpTools.TestRunner.Display.View');

dojo.require('ChirpTools.Mvc.View');
dojo.require('ChirpTools.TestRunner.Events');

dojo.declare('ChirpTools.TestRunner.Display.View', ChirpTools.Mvc.View, {
    /**
     * The portion at the top of the page that let's you see what tests are
     * running and the current status
     */
    testRunnerNode: undefined,

    /**
     * The iframe that contains the page being tested
     */
    subjectNode: undefined,

    /**
     * The iframe itself
     */
    subjectFrame: undefined,

    /**
     * Sets the size of the frame where the subject of all our tests will occur
     */
    setSubjectSize: function() {
        var fullHeight = document.documentElement.clientHeight;
        var testRunnerPosition = dojo.position(this.testRunner);
        dojo.style(this.subjectFrame, 'height', (fullHeight - testRunnerPosition.h) + 'px');
    },

    /**
     * Show the test runner and the subject frame
     */
    showAll: function() {
        dojo.style(this.testRunner, 'display', 'block');
        dojo.style(this.subject, 'display', 'block');
    },

    /**
     * Shows the test entry points we are preparing to test
     *
     * @param teps Array of test entry points
     */
    showTestEntryPoints: function(teps) {
        dojo.forEach(teps, function(tep) {
            node = dojo.create('li', {
                innerHTML: tep.name,
                chirpBindGroup: 'testEntryPoint'
            }, this.testEntryPointList, 'last');
            play = dojo.create('a', {
                innerHTML: 'Run',
                chirpBindGroup: 'testEntryPointRun',
                href: '#'
            }, node, 'first');
            tep.setNode(node);
            node._tep = tep;
        }, this);

        this._bind(this.domNode);
    },

    /**
     * All tests are done, show the results
     *
     * @params results An array of results from all the tests for all test entry points
     */
    displayResults: function(results) {
        dojo.forEach(results, dojo.hitch(this, function(result) {
            if (result.failures.length > 0) {
                dojo.style(result.testEntryPoint.node, 'color', '#FF0000');
            }
        }));
    },

    /**
     * When the run button is clicked
     */
    runOnClick: function(event) {
        this.publish(ChirpTools.TestRunner.Events.Display.RunClick);
    },

    /**
     * When just one test is being ran
     */
    testEntryPointRunOnClick: function(event) {
        var tep = event.currentTarget.parentNode._tep;

        this.publish(ChirpTools.TestRunner.Events.Display.RunOneClick, [ tep ]);
    }
});
