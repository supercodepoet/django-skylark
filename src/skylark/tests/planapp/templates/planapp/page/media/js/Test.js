// Controller
dojo.require('dojox.timing');
dojo.require('dojo.cookie');
dojo.require('PlanApp.Page.View');
dojo.require('ChirpTools.Mvc.Controller');

dojo.provide('PlanApp.Page.Controller');

dojo.declare('PlanApp.Page.Controller', ChirpTools.Mvc.Controller {
    constructor: function(domNode) {
        this.view = new PlanApp.Page.View(domNode);
    }
});
