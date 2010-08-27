// This information is part of the RibtTools framework
if (!djConfig) {
    var djConfig = {
        parseOnLoad: false,
        debugAtAllCosts: {{ skylark_internals.settings.CRUNCHYFROG_DOJO_DEBUGATALLCOSTS|lower }},
        dojoIframeHistoryUrl: "{{ cache_url }}/addon/dojo/resources/iframe_history.html"
    }
}
