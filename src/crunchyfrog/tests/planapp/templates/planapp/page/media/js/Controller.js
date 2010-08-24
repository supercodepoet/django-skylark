// Controller
dojo.require('dojox.timing');
dojo.require('dojo.cookie');
dojo.require('PlanApp.Page.View');

dojo.provide('PlanApp.Page.Controller');

dojo.declare('PlanApp.Page.Controller', null {
    constructor: function(domNode) {
        this.view = new PlanApp.Page.View(domNode);
    }
});
