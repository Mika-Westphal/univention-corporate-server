/*
 * Copyright 2014 Univention GmbH
 *
 * http://www.univention.de/
 *
 * All rights reserved.
 *
 * The source code of this program is made available
 * under the terms of the GNU Affero General Public License version 3
 * (GNU AGPL V3) as published by the Free Software Foundation.
 *
 * Binary versions of this program provided by Univention to you as
 * well as other copyrighted, protected or trademarked materials like
 * Logos, graphics, fonts, specific documentations and configurations,
 * cryptographic keys etc. are subject to a license agreement between
 * you and Univention and not subject to the GNU AGPL V3.
 *
 * In the case you use this program under the terms of the GNU AGPL V3,
 * the program is provided in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public
 * License with the Debian GNU/Linux or Univention distribution in file
 * /usr/share/common-licenses/AGPL-3; if not, see
 * <http://www.gnu.org/licenses/>.
 */
/*global define*/

define([
	"dojo/_base/declare",
	"dojo/_base/lang",
	"dojo/_base/array",
	"dojo/dom-class",
	"dojo/on",
	"dojo/topic",
	"dojo/Deferred",
	"dojo/when",
	"dojox/html/styles",
	"dijit/form/RadioButton",
	"umc/dialog",
	"umc/widgets/ProgressBar",
	"umc/tools",
	"umc/widgets/Page",
	"umc/widgets/Form",
	"umc/widgets/ExpandingTitlePane",
	"umc/widgets/Module",
	"umc/widgets/Text",
	"umc/widgets/TextBox",
	"umc/widgets/PasswordBox",
	"umc/widgets/CheckBox",
	"umc/widgets/Wizard",
	"./RadioButtons",
	"umc/i18n!umc/modules/adconnector"
], function(declare, lang, array, domClass, on, topic, Deferred, when, styles, RadioButton, dialog, ProgressBar, tools, Page, Form, ExpandingTitlePane, Module, Text, TextBox, PasswordBox, CheckBox, Wizard, RadioButtons, _) {
	var modulePath = require.toUrl('umc/modules/adconnector');
	styles.insertCssRule('.umc-adconnector-page > form > div', 'background-repeat: no-repeat; background-position: 10px 0px; padding-left: 200px; min-height: 200px;');
	styles.insertCssRule('.umc-adconnector-page .umcLabelPaneCheckBox', 'display: block !important;');
	array.forEach(['start', 'credentials', 'config', 'info', 'syncconfig', 'syncconfig-left', 'syncconfig-right', 'syncconfig-left-right', 'msi', 'finished'], function(ipage) {
		var conf = {
			name: ipage,
			path: modulePath
		};
		styles.insertCssRule(
			lang.replace('.umc-adconnector-page-{name} > form > div', conf),
			lang.replace('background-image: url({path}/{name}.png)', conf)
		);
	});

	//TODO: to be merged into SetupWizard ???
//	var ADConnectorWizard = declare("umc.modules._adconnector.Wizard", [Wizard], {
//		pages: null,
//
//		variables: null,
//
//		addNotification: dialog.notify,
//
//		constructor: function() {
//			this.pages = [{
//				name: 'fqdn',
//				helpText: '<p>' + _("This wizard configures a synchronized parallel operation of UCS next to a native Active Directory domain.") + " "
//					+ _('If on the other hand the replacement of a native Active Directory domain is desired, Univention AD Takeover should be used instead.') + '</p><p>'
//					+ _('Please enter the fully qualified hostname of the Active Directory server.') + '</p><p>'
//					+ _('The hostname must be resolvable by the UCS server. A DNS entry can be configured in the DNS module, or a static host record can be configured through the Univention Configuration Registry module, e.g.') + '</p>'
//					+ '<p>hosts/static/192.168.0.10=w2k8-ad.example.com</p>',
//				headerText: _('UCS Active Directory Connector configuration'),
//				widgets: [{
//					name: 'LDAP_Host',
//					type: TextBox,
//					required: true,
//					regExp: '.+',
//					invalidMessage: _('The hostname of the Active Directory server is required'),
//					label: _('Active Directory Server')
//				}, {
//					name: 'guess',
//					type: CheckBox,
//					label: _('Automatic determination of the LDAP configuration')
//				}],
//				layout: ['LDAP_Host', 'guess']
//			}, {
//				name: 'ldap',
//				helpText: _('LDAP und kerberos configuration of the Active Directory server needs to be specified for the synchronisation'),
//				headerText: _('LDAP and Kerberos'),
//				widgets: [{
//					name: 'LDAP_Base',
//					type: TextBox,
//					required: true,
//					sizeClass: 'OneAndAHalf',
//					label: _('LDAP base')
//				}, {
//					name: 'LDAP_BindDN',
//					required: true,
//					type: TextBox,
//					sizeClass: 'OneAndAHalf',
//					label: _('LDAP DN of the synchronisation user')
//				}, {
//					name: 'LDAP_Password',
//					type: PasswordBox,
//					label: _('Password of the synchronisation user')
//				}, {
//					name: 'KerberosDomain',
//					type: TextBox,
//					label: _('Kerberos domain')
//				}],
//				layout: ['LDAP_Base', 'LDAP_BindDN', 'LDAP_Password', 'KerberosDomain']
//			}, {
//				name: 'sync',
//				helpText: _('UCS Active Directory Connector supports three types of synchronisation.'),
//				headerText: _('Synchronisation mode'),
//				widgets: [{
//					name: 'MappingSyncMode',
//					type: ComboBox,
//					staticValues: [
//						{
//							id: 'sync',
//							label: 'AD <-> UCS'
//						},{
//							id: 'read',
//							label: 'AD -> UCS'
//						}, {
//							id: 'write',
//							label: 'UCS -> AD'
//						}],
//					label: _('Synchronisation mode')
//				}, {
//					name: 'MappingGroupLanguage',
//					label: _('System language of Active Directory server'),
//					type: ComboBox,
//					staticValues: [
//						{
//							id: 'de',
//							label: _('German')
//						}, {
//							id: 'en',
//							label: _('English')
//						}]
//				}],
//				layout: ['MappingSyncMode', 'MappingGroupLanguage']
//			}, {
//				name: 'extended',
//				helpText: _('The following settings control the internal behaviour of the UCS Active Directory connector. For all attributes reasonable default values are provided.'),
//				headerText: _('Extended settings'),
//				widgets: [{
//					name: 'PollSleep',
//					type: TextBox,
//					sizeClass: 'OneThird',
//					label: _('Poll Interval (seconds)')
//				}, {
//					name: 'RetryRejected',
//					label: _('Retry interval for rejected objects'),
//					type: TextBox,
//					sizeClass: 'OneThird'
//				}, {
//					name: 'DebugLevel',
//					label: _('Debug level of Active Directory Connector'),
//					type: TextBox,
//					sizeClass: 'OneThird'
//				}, {
//					name: 'DebugFunction',
//					label: _('Add debug output for functions'),
//					type: CheckBox,
//					sizeClass: 'OneThird'
//				}],
//				layout: ['PollSleep', 'RetryRejected', 'DebugLevel', 'DebugFunction']
//			}];
//
//		},
//
//		next: function(/*String*/ currentID) {
//			if (!currentID) {
//				tools.forIn(this.variables, lang.hitch(this, function(option, value) {
//					var w = this.getWidget(null, option);
//					if (w) {
//						w.set('value', value);
//					}
//				}));
//				// of no LDAP_base is set activate the automatic determination
//				if (!this.variables.LDAP_base) {
//					this.getWidget('fqdn', 'guess').set('value', true);
//				}
//			} else if (currentID == 'fqdn') {
//				var nameWidget = this.getWidget('LDAP_Host');
//				if (!nameWidget.isValid()) {
//					nameWidget.focus();
//					return null;
//				}
//
//				var guess = this.getWidget('fqdn', 'guess');
//				if (guess.get('value')) {
//					this.standby(true);
//					var server = this.getWidget('fqdn', 'LDAP_Host');
//					tools.umcpCommand('adconnector/guess', { 'LDAP_Host' : server.get('value') }).then(lang.hitch(this, function(response) {
//						if (response.result.LDAP_Base) {
//							this.getWidget('ldap', 'LDAP_Base').set('value', response.result.LDAP_Base);
//							this.getWidget('ldap', 'LDAP_BindDN').set('value', 'cn=Administrator,cn=users,' + response.result.LDAP_Base);
//							this.getWidget('ldap', 'KerberosDomain').set('value', tools.explodeDn(response.result.LDAP_Base, true).join('.'));
//						} else {
//							this.addNotification(response.result.message);
//						}
//						this.standby(false);
//					}));
//				}
//			} else if (currentID == 'ldap') {
//				var valid = true;
//				array.forEach(['LDAP_Base', 'LDAP_BindDN', 'LDAP_Password'], lang.hitch(this, function(widgetName) {
//					if (!this.getWidget(widgetName).isValid()) {
//						this.getWidget(widgetName).focus();
//						valid = false;
//						return false;
//					}
//				}));
//				if (!valid) {
//					return null;
//				}
//
//				var password = this.getWidget('ldap', 'LDAP_Password');
//				if (!this.variables.passwordExists && !password.get('value')) {
//					dialog.alert(_('The password for the synchronisation account is required!'));
//					return currentID;
//				}
//			}
//
//			return this.inherited(arguments);
//		},
//
//		onFinished: function(values) {
//			this.standby(true);
//			tools.umcpCommand('adconnector/save', values).then(lang.hitch(this, function(response) {
//				if (!response.result.success) {
//					dialog.alert(response.result.message);
//				} else {
//					this.addNotification(response.result.message);
//				}
//				this.standby(false);
//			}));
//		}
//	});

	var _Wizard = declare("umc.modules.adconnector.SetupWizard", [ Wizard ], {
		autoValidate: true,
		autoFocus: true,

		constructor: function() {
			this.pages = [{
				'class': 'umc-adconnector-page-start umc-adconnector-page',
				name: 'start',
				headerText: _('Active Directory Connector'),
				widgets: [{
					type: Text,
					name: 'help',
					content: _('<p>This wizards guides the configuration of the connection with an existing Active Directory domain.</p><p>There are two possible ways:</p>')
				}, {
					type: RadioButtons,
					name: 'syncmode',
					staticValues: [{
						id: 'admember',
						label: _('Configure UCS as part of the Active Directory domain (recommended).')
					}, {
						id: 'adconnector',
						label: _('Synchronisation of account data between an Active Directory and a UCS domain.')
					}]
				}, {
					type: Text,
					name: 'help2',
					content: _('<p>Use the recommended first option if Active Directory will be the principal domain. Domain users can directly access applications that are installed on UCS.</p><p>Use the second option for more complex szenarios which necessitate that Active Directory and UCS domains exist in parallel.</p>')
				}]
			}, {
				'class': 'umc-adconnector-page-credentials umc-adconnector-page',
				name: 'credentials',
				headerText: _('Active Directory domain credentials'),
				widgets: [{
					type: Text,
					'class': 'umcPageHelpText',
					name: 'help',
					content: _('To proceed with the configuration of the connection, enter Active Directory domain information:')
				}, {
					type: TextBox,
					name: 'ad_server_ip',
					required: true,
					label: _('Address of Active Directory domain controller')
				}, {
					type: TextBox,
					name: 'username',
					required: true,
					label: _('Active Directory account'),
					value: 'Administrator'
				}, {
					type: PasswordBox,
					name: 'password',
					required: true,
					label: _('Active Directory password')
				}]
			}, {
				'class': 'umc-adconnector-page-info umc-adconnector-page',
				name: 'ssl-admember',
				headerText: _('Security settings'),
				widgets: [{
					type: Text,
					'class': 'umcPageHelpText',
					name: 'info',
					content: _('<p>An encrypted connection to the Active Directory domain could not be established. This has as consequence that authentication data is submitted in plaintext.</p><p>To enable an encrypted connection, a certification authority needs to be configured on the Active Directory server. All necessary steps are described in the <a href="http://docs.univention.de/manual-3.2.html#ad-connector:ad-zertifikat" target="_blank">UCS manual</a>.</p><p>After the certification authority has been set up, press <i>Next</i> to proceed.</p>')
				}]
			}, {
				'class': 'umc-adconnector-page-info umc-adconnector-page',
				name: 'confirm-admember',
				headerText: _('Configuration of UCS as part of Active Directory domain'),
				widgets: [{
					type: Text,
					name: 'help',
					content: '<p>' + _('Please confirm to start the join process of this UCS system into the following Active Directory domain:') + '</p>'
				}, {
					type: Text,
					name: 'info',
					content: ''
				}]
			}, {
				'class': 'umc-adconnector-page-finished umc-adconnector-page',
				name: 'finished-admember',
				headerText: _('Completion of Active Directory Connector'),
				widgets: [{
					type: Text,
					name: 'help',
					content: _('<p>Congratulations, Univention Corporate Server has been successfully configured to be part of a Active Directory domain.</p><p>The UCS server is now ready for usage, and domain account information are now available.</p>')
				}]
			}, {
				'class': 'umc-adconnector-page-syncconfig umc-adconnector-page',
				name: 'config-adconnector',
				headerText: _('Configuration of Active Directory domain synchronisation'),
				widgets: [{
					type: Text,
					'class': 'umcPageHelpText',
					name: 'help',
					content: _('Specify the synchronisation direction between the UCS domain and the given Active Directory domain.')
				}, {
					type: RadioButtons,
					name: 'syncmode',
					staticValues: [{
						id: 'syncAD2UCS',
						label: _('Unidirectional synchronisation of Active Directory to UCS.'),
					}, {
						id: 'syncUCS2AD',
						label: _('Unidirectional synchronisation of UCS to Active Directory.'),
					}, {
						id: 'syncBidirectional',
						label: _('Bidirectional synchronisation of UCS and Active Directory.'),
					}],
					onChange: lang.hitch(this, function(value) {
						var map2img = {
							'default': '',
							syncAD2UCS: '-right',
							syncUCS2AD: '-left',
							syncBidirectional: '-left-right'
						};
						var syncmode = this.getWidget('config-adconnector', 'syncmode').get('value');
						var page = this.getPage('config-adconnector');
						tools.forIn(map2img, lang.hitch(this, function(ikey, ival) {
							var cssClass = 'umc-adconnector-page-syncconfig' + ival;
							var useClass = syncmode == ikey;
							domClass.toggle(page.domNode, cssClass, useClass);
						}));
					})
				}]
			}, {
				'class': 'umc-adconnector-page-info umc-adconnector-page',
				name: 'info-adconnector',
				headerText: _('Active Directory domain information'),
				widgets: [{
					type: Text,
					name: 'help',
					content: _('<p>A Windows 2008 R2 Active Directory domain with the domainname <i>example.org</i> has been found. The server <i>admaster</i> (10.200.8.237) will be used as Active Directory domain controller.</p><p>The following domain accounts have been found:</p><ul><li>13 user accounts</li><li>9 groups</li></ul>')
				}]
			}, {
				'class': 'umc-adconnector-page-msi umc-adconnector-page',
				name: 'msi-adconnector',
				headerText: _('Installation of password service'),
				widgets: [{
					type: Text,
					name: 'help',
					content: _('<p>The MSI files are the installation files for the password service and can be started by double clicking on it. The package is installed in the <b>C:&#92;Windows&#92;UCS-AD-Connector</b> directory automatically. Additionally, the password service is integrated into the Windows environment as a system service, which means the service can be started automatically or manually.</p><ul><li><a>ucs-ad-connector.msi</a><br>Installation file for the password service for <b>32bit</b> Windows.<br>It can be started by double clicking on it.</li><li><a>ucs-ad-connector-64bit.msi</a><br>Installation file for the password service for <b>64bit</b> Windows.<br>It can be started by double clicking on it.</li><li><a>vcredist_x86.exe</a><br>Microsoft Visual C++ 2010 Redistributable Package (x86) - <b>Must</b> be installed on a <b>64bit</b> Windows.</li></ul><p>After installing the password service, click "Next" to initiate the synchronisation process.</p>')
				}]
			}, {
				'class': 'umc-adconnector-page-finished umc-adconnector-page',
				name: 'finished-adconnector',
				headerText: _('Completion of Active Directory Connector'),
				widgets: [{
					type: Text,
					name: 'help',
					content: _('<p>Congratulations, the synchronisation of Univention Corporate Server and Active Directory has been succesfully initiated.</p><p>The UCS server is now ready for usage, and domain account information are now available.</p>')
				}]
			}];
		},

		buildRendering: function() {
			this.inherited(arguments);
			var syncmodeWidget = this.getWidget('start', 'syncmode');
		},

		_isConnectorMode: function() {
			return this.getWidget('start', 'syncmode').get('value') == 'adconnector';
		},

		_isMemberMode: function() {
			return this.getWidget('start', 'syncmode').get('value') == 'admember';
		},

		_updateConfirmADMemberPage: function(info) {
			var fqdnParts = info.DC_DNS_Name.split(/\./g);
			info._hostname = fqdnParts.shift();
			var msg = '<ul>';
			array.forEach([
				[_('Active Directory domain'), info.Domain],
				[_('AD domain controller'), _('%(DC_DNS_Name)s (%(DC_IP)s)', info)],
				[_('SSL encryption'), info.ssl_supported ? _('Activated') : _('<b>Deactivated!</b>')],
				[_('LDAP base'), info.LDAP_Base]
			], function(ientry) {
				msg += '<li>' + ientry[0] + ': <i>' + ientry[1] + '</i></li>';
			});
			msg += '</ul>';
			msg += _('<p>Click "Next" to inititate the join process into the AD domain.</p>');
			this.getWidget('confirm-admember', 'info').set('content', msg);
		},

		_checkADDomain: function() {
			var vals = this.getPage('credentials')._form.get('value');
			return this.standbyDuring(tools.umcpCommand('adconnector/admember/check_domain', vals)).then(lang.hitch(this, function(response) {
				this._updateConfirmADMemberPage(response.result);
				return response.result
			}), function() {
				return null;
			});
		},

		_confirmUnsecureConnectionWithADDomain: function() {
			return dialog.confirm(_('<p>An encrypted connection to the Active Directory domain could still not be established.</p><p>Confirm if you want to procced with an unsecure connection.</p>'), [{
				name: 'cancel',
				label: _('Cancel')
			}, {
				name: 'confirm',
				'default': true,
				label: _('Continue without encryption')
			}], _('Security warning')).then(function(response) {
				return response == 'confirm';
			});
		},

		isPageVisible: function(pageName) {
			var isConnectorPage = pageName.indexOf('-adconnector') >= 0;
			if (isConnectorPage && !this._isConnectorMode()) {
				return false;
			}
			var isMemberPage = pageName.indexOf('-admember') >= 0;
			if (isMemberPage && !this._isMemberMode()) {
				return false;
			}
			return true;
		},

		next: function(pageName) {
			var nextPage = this.inherited(arguments);
			if (pageName == 'start' && !this._isMemberMode()) {
				//TODO: fallback for now
				dialog.alert(_('I can only configure the member mode for now!'));
				return pageName;
			}
			if (pageName == 'credentials') {
				if (this._isMemberMode()) {
					return this._checkADDomain().then(function(adDomainInfo) {
						// server error message is shown, stay on the same page
						if (!adDomainInfo) {
							return pageName;
						}
						// check for SSL support
						return adDomainInfo.ssl_supported ? 'confirm-admember' : 'ssl-admember';
					});
				}
			}
			if (pageName == 'ssl-admember') {
				// check again for SSL status
				return this._checkADDomain().then(lang.hitch(this, function(adDomainInfo) {
					// server error message is shown, stay on the same page
					if (!adDomainInfo) {
						return pageName;
					}
					if (!adDomainInfo.ssl_supported) {
						return this._confirmUnsecureConnectionWithADDomain().then(function(confirmed) {
							return confirmed ? nextPage : pageName;
						});
					}
					return nextPage;
				}));
			}

			//TODO: below here unused for now...
			if (pageName == 'confirm-admember') {
				return this._startUCSJoinInAD().then(function() {
					return nextPage;
				});
			}
			if (pageName == 'msi-adconnector') {
				return this._startADSync().then(function() {
					return nextPage;
				});
			}
			if ((pageName == 'credentials' && this._isMemberMode())
				|| (pageName == 'config-adconnector' && this._isConnectorMode())) {
				return this._queryDomainInfo().then(function() {
					return nextPage;
				});
			}
			return nextPage;
		},

		previous: function(pageName) {
			if (pageName.indexOf('Config') >= 0) {
				return 'credentials';
			}
			return this.inherited(arguments);
		},

		hasNext: function(pageName) {
			return pageName.indexOf('Finished') < 0;
		},

		hasPrevious: function(pageName) {
			return pageName.indexOf('Finished') < 0;
		},

		canCancel: function(pageName) {
			return pageName.indexOf('Finished') < 0;
		},

		_timeout: function(seconds, percentage, message) {
			var _deferred = new Deferred();
			setTimeout(lang.hitch(this, function() {
				this.progressBar.setInfo(null, message, percentage);
				_deferred.resolve()
			}), seconds * 1000);
			return _deferred;
		},

		_startUCSJoinInAD: function() {
			this.progressBar.reset(_('UCS join in Active Directory domain'));
			this.standby(true, this.progressBar);
			var self = this;
			return this._timeout(0, 0, _('Contacting Active Directory server')).then(function() {
				return self._timeout(1, 10, _('Authentification with credentials'));
			}).then(function() {
				return self._timeout(1, 20, _('Querying certificates'));
			}).then(function() {
				return self._timeout(2, 40, _('Preparing join'));
			}).then(function() {
				return self._timeout(2, 60, _('Joining the domain'));
			}).then(function() {
				return self._timeout(2, 80, _('Updating local system'));
			}).then(function() {
				return self._timeout(1, 100, _('Cleaning up'));
			}).then(function() {
				return self.standby(false);
			});
		},

		_startADSync: function() {
			this.progressBar.reset(_('Initiating synchronisation with Active Directory domain'));
			this.standby(true, this.progressBar);
			var self = this;
			return this._timeout(0, 0, _('Contacting Active Directory server')).then(function() {
				return self._timeout(1, 10, _('Authentification with credentials'));
			}).then(function() {
				return self._timeout(1, 20, _('Validating service configuration'));
			}).then(function() {
				return self._timeout(3, 40, _('Quering domain accounts'));
			}).then(function() {
				return self._timeout(2, 70, _('Starting synchronisation service'));
			}).then(function() {
				return self._timeout(1, 100, _('Cleaning up'));
			}).then(function() {
				return self.standby(false);
			});
		},

		_queryDomainInfo: function() {
			this.progressBar.reset(_('Querying Active Directory domain information'));
			this.standby(true, this.progressBar);
			this.progressBar._progressBar.set('value', Infinity);
			var self = this;
			return this._timeout(0, null, _('Contacting Active Directory server')).then(function() {
				return self._timeout(1, null, _('Querying domain information'));
			}).then(function() {
				return self._timeout(1, null, _('Querying user accounts'));
			}).then(function() {
				return self._timeout(1, null, _('Querying computer accounts'));
			}).then(function() {
				return self.standby(false);
			});
		}
	});

	return declare("umc.modules.adtakeover2", Module , {
		unique: true,

		buildRendering: function() {
			var progressBar = new ProgressBar({});
			this.inherited(arguments);

			this.wizard = new _Wizard({
				progressBar: progressBar
			});
			this.addChild(this.wizard);
			this.wizard.on('Finished', lang.hitch(this, function() {
				topic.publish('/umc/tabs/close', this);
			}));
			this.wizard.on('Cancel', lang.hitch(this, function() {
				topic.publish('/umc/tabs/close', this);
			}));
		}

	});
});
