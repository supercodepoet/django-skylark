dojo.provide('RibtTools.TestRunner.SubjectStart.View');

dojo.require('RibtTools.Mvc.View');

dojo.declare('RibtTools.TestRunner.SubjectStart.View', RibtTools.Mvc.View, {
    constructor: function(domNode) {
        this._log('Loading tests');
    },

    _log: function(message) {
        dojo.place('<li>' + message + '</li>', this.log, 'last');
    },

    showTestCount: function(testCount) {
        this._log(testCount + ' available');
    } 
});
