//Command to run to build with this profile
//action=clean,release dojodir=./release-1.4.1 profileFile=./standard.profile.js releaseDir=../skylark/templates/ribt/media version=1.4.1 optimize=none copyTests=false

dependencies = {
	layers: [
		{
			name: "../dojox/dtl.js",
			dependencies: [
				"dojox.dtl",
				"dojox.dtl.Context",
				"dojox.dtl.tag.logic",
				"dojox.dtl.tag.loop",
				"dojox.dtl.tag.date",
				"dojox.dtl.tag.loader",
				"dojox.dtl.tag.misc",
				"dojox.dtl.ext-dojo.NodeList"
			]
		}
	],
	prefixes: [
		[ "dojox", "../dojox" ],
	]
}
