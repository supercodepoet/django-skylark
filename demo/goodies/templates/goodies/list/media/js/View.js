dojo.provide("Whizzo.Goodies.List.View");

dojo.declare("Whizzo.Goodies.List.View", RibtTools.Mvc.View, {
    constructor: function(domNode) {
        $(domNode).tabs();
    },

    tellUsAboutFrogsOnClick: function(event) {
        alert('You like ' + $(this.numberFrogsEaten).val() + ' frogs');
    },
});
