dojo.provide('ChirpTools.TestRunner.SubjectStart.View');

dojo.require('ChirpTools.Mvc.View');

dojo.declare('ChirpTools.TestRunner.SubjectStart.View', ChirpTools.Mvc.View, {
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
