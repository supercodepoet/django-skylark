dojo.provide("Whizzo.Goodies.List.Controller");

dojo.declare("Whizzo.Goodies.List.Controller", RibtTools.Mvc.Controller, {
    favorite: '',

    constructor: function(domNode) {
        this.view = new Whizzo.Goodies.List.View(domNode);
    }
});
