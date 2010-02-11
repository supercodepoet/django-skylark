//Command to run to build with this profile
//action=clean,release dojodir=./release-1.4.1 profileFile=./standard.profile.js releaseDir=../crunchyfrog/templates/ribt/media version=1.4.1 optimize=none copyTests=false

dependencies = {
	//Strip all console.* calls except console.warn and console.error. This is basically a work-around
	//for trac issue: http://bugs.dojotoolkit.org/ticket/6849 where Safari 3's console.debug seems
	//to be flaky to set up (apparently fixed in a webkit nightly).
	//But in general for a build, console.warn/error should be the only things to survive anyway.
	stripConsole: "normal",

	layers: [
		{
			name: "dojox_for_ribt.js",
			dependencies: [
				"dojox.dtl",
				"dojox.dtl.Context",
				"dojox.dtl.tag.logic",
				"dojox.dtl.tag.loop",
				"dojox.dtl.tag.date",
				"dojox.dtl.tag.loader",
				"dojox.dtl.tag.misc",
				"dojox.dtl.ext-dojo.NodeList",
				"dojox.timing",
                "dojox.timing.Sequence.js",
                "dojox.timing.Streamer.js",
                "dojox.timing.ThreadPool.js",
                "dojox.timing.doLater.js",
				"dojox.uuid",
                "dojox.uuid.Uuid.js",
                "dojox.uuid.generateRandomUuid.js",
                "dojox.uuid.generateTimeBasedUuid.js"
			]
        }
	]
}
