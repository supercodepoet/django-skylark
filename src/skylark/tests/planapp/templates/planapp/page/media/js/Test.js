// Controller
dojo.require('dojox.timing');
dojo.require('dojo.cookie');
dojo.require('PlanApp.Page.View');
dojo.require('RibtTools.Mvc.Controller');

dojo.provide('PlanApp.Page.Controller');

dojo.declare('PlanApp.Page.Controller', RibtTools.Mvc.Controller {
    constructor: function(domNode) {
        this.view = new PlanApp.Page.View(domNode);
    }
});
