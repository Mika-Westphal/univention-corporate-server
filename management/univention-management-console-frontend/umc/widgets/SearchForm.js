/*global dojo dijit dojox umc console */

dojo.provide("umc.widgets.SearchForm");

dojo.require("dijit.form.Form");
dojo.require("umc.tools");
dojo.require("umc.i18n");

dojo.declare("umc.widgets.SearchForm", [ umc.widgets.Form, umc.i18n.Mixin ], {
	// summary:
	//		Encapsulates a complete search form with standard search and cancel
	//		buttons. This builds on top of umc.widget.Form.

	i18nClass: 'umc.app',

	postMixInProperties: function() {
		this.inherited(arguments);

		// in case no buttons are defined, define the standard buttons: 'submit' and 'reset'
		if (!this.buttons) {
			this.buttons = [{
				name: 'reset',
				label: this._( 'Reset' ),
				align: 'right'
				//callback: dojo.hitch(this, 'onReset')
			}, {
				name: 'submit',
				label: this._( 'Search' ),
				align: 'right',
				callback: dojo.hitch(this, function(values) {
					this.onSearch(values);
				})
			}];
		}

		// layout the buttons in the same row as the form (if there is only one row)
		console.log('#layout: ' + this.layout);
		if (dojo.isArray(this.layout)) {
			var layout = this.layout;
			if (1 == layout.length) {
				layout = layout[0];
				if (!dojo.isArray(layout)) {
					layout = [ layout ];
				}
				this.layout[0] = layout;
			}
			layout.push('submit', 'reset');
		}
		console.log('#layout: ' + this.layout);
	},

	onSearch: function(values) {
		// event stub
	},

	onReset: function() {
		// event stub
	}

});







