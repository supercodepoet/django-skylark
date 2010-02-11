dojo.provide('RibtTools.TestRunner.SubjectStart.Controller');

dojo.require('RibtTools.Mvc.Controller');

dojo.declare('RibtTools.TestRunner.SubjectStart.Controller', RibtTools.Mvc.Controller, {
    constructor: function(domNode) {
        this.view = new RibtTools.TestRunner.SubjectStart.View(domNode);

        this.channel = RibtTools.TestRunner.Channel;

        dojo.subscribe(RibtTools.TestRunner.Events.TestCount, this, this.handleTestCount);

        this.channel.publish(RibtTools.TestRunner.Events.SubjectFrame.Ready);
    },

    handleTestCount: function(testCount) {
        this.testCount = {
            total: testCount
        };

        this.view.showTestCount(testCount);
    },
});
