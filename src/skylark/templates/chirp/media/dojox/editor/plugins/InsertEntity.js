/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.editor.plugins.InsertEntity"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.editor.plugins.InsertEntity"] = true;
dojo.provide("dojox.editor.plugins.InsertEntity");
dojo.require("dijit.TooltipDialog");
dojo.require("dijit._editor._Plugin");
dojo.require("dijit.form.Button");
dojo.require("dojox.html.entities");
dojo.require("dojox.editor.plugins.EntityPalette");
dojo.require("dojo.i18n");
dojo.requireLocalization("dojox.editor.plugins", "InsertEntity", null, "ROOT,ar,ca,cs,da,de,el,es,fi,fr,he,hu,it,ja,kk,ko,nb,nl,pl,pt,pt-pt,ro,ru,sl,sv,th,tr,zh,zh-tw");


dojo.declare("dojox.editor.plugins.InsertEntity",dijit._editor._Plugin,{
	// summary:
	//		This plugin allows the user to select from standard Symbols (HTML Entities)
	//		to insert at the current cursor position.  It binds to the key pattern:
	//		ctrl-shift-s for opening the insert symbol dropdown.
	//
	// description:
	//		The commands provided by this plugin are:
	//		* insertEntity - inserts the selected HTML entity character

	// iconClassPrefix: [const] String
	//		The CSS class name for the button node is formed from `iconClassPrefix` and `command`
	iconClassPrefix: "dijitAdditionalEditorIcon",

	_initButton: function(){
		// summary:
		//		Over-ride for creation of the save button.
		this.dropDown = new dojox.editor.plugins.EntityPalette({showCode: this.showCode, showEntityName: this.showEntityName});
		this.connect(this.dropDown, "onChange", function(entity){
			this.button.closeDropDown();
			this.editor.focus();
			this.editor.execCommand("inserthtml",entity);
		});
		var strings = dojo.i18n.getLocalization("dojox.editor.plugins", "InsertEntity");
		this.button = new dijit.form.DropDownButton({
			label: strings["insertEntity"],
			showLabel: false,
			iconClass: this.iconClassPrefix + " " + this.iconClassPrefix + "InsertEntity",
			tabIndex: "-1",
			dropDown: this.dropDown
		});
	},

	updateState: function(){
		// summary:
		//		Over-ride for button state control for disabled to work.
		this.button.set("disabled", this.get("disabled"));
	},

	setEditor: function(editor){
		// summary:
		//		Over-ride for the setting of the editor.
		// editor: Object
		//		The editor to configure for this plugin to use.
		this.editor = editor;
		this._initButton();

		this.editor.addKeyHandler("s", true, true, dojo.hitch(this, function(){
			this.button.openDropDown();
			this.dropDown.focus();
		}));

		editor.contentPreFilters.push(this._preFilterEntities);
		editor.contentPostFilters.push(this._postFilterEntities);
	},

	_preFilterEntities: function(s/*String content passed in*/){
		// summary:
		//		A function to filter out entity characters into their UTF-8 character form
		//		displayed in the editor.  It gets registered with the preFilters
		//		of the editor.
		// tags:
		//		private.
		return dojox.html.entities.decode(s, dojox.html.entities.latin);
	},

	_postFilterEntities: function(s/*String content passed in*/){
		// summary:
		//		A function to filter out entity characters into encoded form so they
		//		are properly displayed in the editor.  It gets registered with the
		//		postFilters of the editor.
		// tags:
		//		private.
		return dojox.html.entities.encode(s, dojox.html.entities.latin);
	}
});

// Register this plugin.
dojo.subscribe(dijit._scopeName + ".Editor.getPlugin",null,function(o){
	if(o.plugin){ return; }
	var name = o.args.name? o.args.name.toLowerCase() : "";
	if(name === "insertentity"){
		o.plugin = new dojox.editor.plugins.InsertEntity({
			showCode: ("showCode" in o.args)?o.args.showCode:false,
			showEntityName: ("showEntityName" in o.args)?o.args.showEntityName:false
		});
	}
});

}
