/*
	Copyright (c) 2004-2011, The Dojo Foundation All Rights Reserved.
	Available via Academic Free License >= 2.1 OR the modified BSD license.
	see: http://dojotoolkit.org/license for details
*/


if(!dojo._hasResource["dojox.grid.enhanced.plugins.Menu"]){ //_hasResource checks added by build. Do not use _hasResource directly in your code.
dojo._hasResource["dojox.grid.enhanced.plugins.Menu"] = true;
dojo.provide("dojox.grid.enhanced.plugins.Menu");

dojo.require("dojox.grid.enhanced._Plugin");

dojo.declare("dojox.grid.enhanced.plugins.Menu", dojox.grid.enhanced._Plugin, {
	// summary:
	//		 Provides context menu support, including header menu, row menu, cell menu and selected region menu
	// example:
	//		<div dojoType="dojox.grid.EnhancedGrid"
	//			plugins="{menus:{headerMenu:"headerMenuId", rowMenu:"rowMenuId", cellMenu:"cellMenuId",
	//							   selectedRegionMenu:"selectedRegionMenuId"}}" ...>
	//		</div>
	
	//name: String
	//		Plugin name
	name: "menus",

	//name: [const] Array
	//		menu types
	types: ['headerMenu', 'rowMenu', 'cellMenu', 'selectedRegionMenu'],
	
	constructor: function(){
		var g = this.grid;
		g.showMenu = dojo.hitch(g, this.showMenu);
		g._setRowMenuAttr = dojo.hitch(this, '_setRowMenuAttr');
		g._setCellMenuAttr = dojo.hitch(this, '_setCellMenuAttr');
		g._setSelectedRegionMenuAttr = dojo.hitch(this, '_setSelectedRegionMenuAttr');
	},
	onStartUp: function(){
		var type, option = this.option;
		for(type in option){
			if(dojo.indexOf(this.types, type) >= 0 && option[type]){
				this._initMenu(type, option[type]);
			}
		}
	},
	_initMenu: function(/*String*/menuType, /*String | Widget(dijit.Menu)*/menu){
		var g = this.grid;
		if(!g[menuType]){//in case already created in _Grid.postCreate()
			var m = this._getMenuWidget(menu);
			if(!m){return;}
			g.set(menuType, m);
			if(menuType != "headerMenu"){
				m._scheduleOpen = function(){return;};
			}
		}
	},
	_getMenuWidget: function(/*String|Widget(dijit.Menu)*/menu){
		// summary:
		//		Fetch the required menu widget(should already been created)
		return (menu instanceof dijit.Menu) ? menu : dijit.byId(menu);
	},
	_setRowMenuAttr: function(/*Widget(dijit.Menu)*/menu){
		// summary:
		//		Set row menu widget
		this._setMenuAttr(menu, 'rowMenu');
	},
	_setCellMenuAttr: function(/*Widget(dijit.Menu)*/menu){
		// summary:
		//		Set cell menu widget
		this._setMenuAttr(menu, 'cellMenu');
	},
	_setSelectedRegionMenuAttr: function(/*Widget(dijit.Menu)*/menu){
		// summary:
		//		Set row menu widget
		this._setMenuAttr(menu, 'selectedRegionMenu');
	},
	_setMenuAttr: function(/*Widget(dijit.Menu)*/menu, /*String*/menuType){
		// summary:
		//		Bind menus to Grid.
		var g = this.grid, n = g.domNode;
		if(!menu || !(menu instanceof dijit.Menu)){
			console.warn(menuType, " of Grid ", g.id, " is not existed!");
			return;
		}
		if(g[menuType]){
			g[menuType].unBindDomNode(n);
		}
		g[menuType] = menu;
		g[menuType].bindDomNode(n);
	},
	showMenu: function(/*Event*/e){
		// summary:
		//		Show appropriate context menu
		//		Fired from dojox.grid.enhanced._Events.onRowContextMenu, 'this' scope - Grid
		//		TODO: test Shift-F10
		var inSelectedRegion = (e.cellNode && dojo.hasClass(e.cellNode, 'dojoxGridRowSelected') ||
			e.rowNode && (dojo.hasClass(e.rowNode, 'dojoxGridRowSelected') || dojo.hasClass(e.rowNode, 'dojoxGridRowbarSelected')));
		
		if(inSelectedRegion && this.selectedRegionMenu){
			this.onSelectedRegionContextMenu(e);
			return;
		}
		
		var info = {target: e.target, coords: e.keyCode !== dojo.keys.F10 && "pageX" in e ? {x: e.pageX, y: e.pageY } : null};
		if(this.rowMenu && (this.selection.isSelected(e.rowIndex) || e.rowNode && dojo.hasClass(e.rowNode, 'dojoxGridRowbar'))){
			this.rowMenu._openMyself(info);
			dojo.stopEvent(e);
			return;
		}

		if(this.cellMenu){
			this.cellMenu._openMyself(info);
		}
		dojo.stopEvent(e);
	},
	destroy: function(){
		// summary:
		//		Destroy all resources.
		//		_Grid.destroy() will unbind headerMenu
		var g = this.grid;
		if(g.headerMenu){g.headerMenu.unBindDomNode(g.viewsHeaderNode);}
		if(g.rowMenu){g.rowMenu.unBindDomNode(g.domNode);}
		if(g.cellMenu){g.cellMenu.unBindDomNode(g.domNode);}
		if(g.selectedRegionMenu){g.selectedRegionMenu.destroy();}
		this.inherited(arguments);
	}
});

dojox.grid.EnhancedGrid.registerPlugin(dojox.grid.enhanced.plugins.Menu/*name:'menus'*/);

}
