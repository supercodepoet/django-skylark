dojo.provide('ChirpTools.Mvc.Dom');

dojo.setObject('ChirpTools.Mvc.Dom', {
    eventMap: [
        'onfocus',
        'onfocusin',
        'onfocusout',
        'onblur',
        'onload',
        'onunload',
        'onabort',
        'onerror',
        'onselect',
        'onchange',
        'onsubmit',
        'onreset',
        'onresize',
        'onscroll',
        'onclick',
        'ondblclick',
        'onmousedown',
        'onmouseenter',
        'onmouseleave',
        'onmousemove',
        'onmouseover',
        'onmouseout',
        'onmouseup',
        'onmousewheel',
        'onwheel',
        'ontextinput',
        'onkeydown',
        'onkeypress',
        'onkeyup',
        'oncompositionstart',
        'oncompositionupdate',
        'oncompositionend'],
        
    containsEvent: function(eventName) {
        eventName = eventName.toLowerCase();
        return dojo.indexOf(ChirpTools.Mvc.Dom.eventMap, eventName) > -1
    }
});
