dojo.provide('ChirpTools.TestRunner.SubjectStart.Controller');

dojo.require('ChirpTools.TestRunner.Events');
dojo.require('ChirpTools.TestRunner.SubjectStart.View');
dojo.require('ChirpTools.Mvc.Controller');

dojo.declare('ChirpTools.TestRunner.SubjectStart.Controller', ChirpTools.Mvc.Controller, {
    constructor: function(domNode) {
        this.view = new ChirpTools.TestRunner.SubjectStart.View(domNode);

        dojo.subscribe(ChirpTools.TestRunner.Events.TestCount, this, this.handleTestCount);

        dojo.publish(ChirpTools.TestRunner.Events.SubjectFrame.Ready);
    },

    handleTestCount: function(testCount) {
        this.testCount = {
            total: testCount
        };

        this.view.showTestCount(testCount);
    },
});
