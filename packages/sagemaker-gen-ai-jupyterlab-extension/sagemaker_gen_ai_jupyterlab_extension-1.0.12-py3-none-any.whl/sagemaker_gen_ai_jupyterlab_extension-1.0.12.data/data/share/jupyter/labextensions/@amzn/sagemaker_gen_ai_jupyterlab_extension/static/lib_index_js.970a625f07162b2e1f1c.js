"use strict";
(self["webpackChunk_amzn_sagemaker_gen_ai_jupyterlab_extension"] = self["webpackChunk_amzn_sagemaker_gen_ai_jupyterlab_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/acknowledgements.js":
/*!*********************************!*\
  !*** ./lib/acknowledgements.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   storeAcknowledgements: () => (/* binding */ storeAcknowledgements)
/* harmony export */ });
/**
 * @description stores user acknowledgements in local browser storage.
 * disclaimerAcknowledged: if true, user has acknowledged the Amazon Q Developer use disclaimer.
 * located at the bottom of the chat experience
 * chatPromptOptionAcknowledged: if true, user has closed the agentic chat intro
 * alert.
 */
const storeAcknowledgements = (command) => {
    if (command === 'disclaimerAcknowledged') {
        localStorage.setItem('disclaimerAcknowledged', 'true');
    }
    if (command === 'chatPromptOptionAcknowledged') {
        localStorage.setItem('chatPromptOptionAcknowledged', 'true');
    }
};


/***/ }),

/***/ "./lib/constants.js":
/*!**************************!*\
  !*** ./lib/constants.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DEFAULT_CURSOR_STATE: () => (/* binding */ DEFAULT_CURSOR_STATE),
/* harmony export */   FLARE_IFRAME_ID: () => (/* binding */ FLARE_IFRAME_ID),
/* harmony export */   QUICK_ACTIONS: () => (/* binding */ QUICK_ACTIONS),
/* harmony export */   TOGGLE_AI_CHAT_MESSAGE: () => (/* binding */ TOGGLE_AI_CHAT_MESSAGE),
/* harmony export */   WORKSPACE_ROOT_PATH: () => (/* binding */ WORKSPACE_ROOT_PATH)
/* harmony export */ });
const FLARE_IFRAME_ID = 'flare-iframe';
const TOGGLE_AI_CHAT_MESSAGE = 'MD_TOGGLE_AI_CHAT';
const WORKSPACE_ROOT_PATH = '/home/sagemaker-user';
const DEFAULT_CURSOR_STATE = { position: { line: 0, character: 0 } };
const QUICK_ACTIONS = {
    HELP: '/help',
    FIX: '/fix',
    EXPLAIN: '/explain',
    OPTIMIZE: '/optimize',
    REFACTOR: '/refactor'
};


/***/ }),

/***/ "./lib/contextMenu.js":
/*!****************************!*\
  !*** ./lib/contextMenu.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   registerContextMenuActions: () => (/* binding */ registerContextMenuActions)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _webview__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./webview */ "./lib/webview.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");



/**
 * This function adds a context menu item for Amazon Q and the related commands to
 * pass content to Q chat. These context menus are available in notebook views.
 */
const registerContextMenuActions = ({ app, notebookTracker, showFlareWidget }) => {
    const verbs = [
        'Explain',
        'Refactor',
        'Fix',
        'Optimize'
    ];
    // Register individual commands
    verbs.forEach(verb => {
        const commandId = `sagemaker-gen-ai:${verb.toLowerCase()}`;
        app.commands.addCommand(commandId, {
            label: `${verb}`,
            isEnabled: () => (verb === 'Fix' ? (0,_utils__WEBPACK_IMPORTED_MODULE_1__.hasError)(notebookTracker) : true),
            execute: () => {
                if (verb === 'Fix') {
                    const debuggingInfo = (0,_utils__WEBPACK_IMPORTED_MODULE_1__.interactiveDebuggingInfo)(notebookTracker);
                    if (debuggingInfo != null && debuggingInfo.cellId && debuggingInfo.instructionFile &&
                        debuggingInfo.cellId !== '' && debuggingInfo.instructionFile !== '') {
                        try {
                            app.commands.execute('sagemaker:diagnose-with-amazon-q', {
                                cellId: debuggingInfo.cellId,
                                instructionFile: debuggingInfo.instructionFile
                            });
                            return;
                        }
                        catch (error) {
                            // Swallow the error and continue with fallback logic
                            console.warn('Failed to execute sagemaker:diagnose-with-amazon-q, continuing with fallback logic', error);
                        }
                    }
                }
                const selection = (0,_utils__WEBPACK_IMPORTED_MODULE_1__.getSelectionOrCellContent)(notebookTracker, verb);
                if (selection) {
                    console.log(`${verb}:`, selection);
                    showFlareWidget();
                    (0,_webview__WEBPACK_IMPORTED_MODULE_2__.postToWebView)({
                        command: 'genericCommand',
                        params: {
                            genericCommand: verb,
                            selection,
                            triggerType: 'contextMenu'
                        }
                    });
                }
            }
        });
    });
    // Create submenu
    const submenu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Menu({ commands: app.commands });
    submenu.title.label = 'Amazon Q';
    // Add commands to the submenu
    verbs.forEach(verb => {
        submenu.addItem({
            command: `sagemaker-gen-ai:${verb.toLowerCase()}`
        });
    });
    const selectorsWhereQMenuIsRendered = ['.jp-CodeCell'];
    selectorsWhereQMenuIsRendered.forEach(selector => app.contextMenu.addItem({
        type: 'submenu',
        submenu: submenu,
        selector,
        rank: 0
    }));
};


/***/ }),

/***/ "./lib/featureFlags.js":
/*!*****************************!*\
  !*** ./lib/featureFlags.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   setChatFeatureFlags: () => (/* binding */ setChatFeatureFlags)
/* harmony export */ });
/* harmony import */ var _webview__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./webview */ "./lib/webview.js");

const setChatFeatureFlags = (featureFlags) => {
    const featureFlagParams = featureFlags.reduce((acc, flag) => {
        acc[flag] = true;
        return acc;
    }, {});
    (0,_webview__WEBPACK_IMPORTED_MODULE_0__.postToWebView)({
        command: 'chatOptions',
        params: featureFlagParams
    });
};


/***/ }),

/***/ "./lib/icons/QIconBlack.js":
/*!*********************************!*\
  !*** ./lib/icons/QIconBlack.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   QIconBlack: () => (/* binding */ QIconBlack)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);

const svgstr = `<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M227.84 52.985L142.93 3.975C133.63 -1.325 122.13 -1.325 112.92 3.975L28 52.985C18.7 58.385 13 68.285 13 78.985V177.005C13 187.705 18.7 197.605 28 203.015L112.92 252.025C122.12 257.325 133.62 257.325 142.93 252.025L227.85 203.015C237.15 197.715 242.85 187.715 242.85 177.005V78.985C242.85 68.285 237.15 58.385 227.85 52.975L227.84 52.985ZM222.84 171.205L149.53 128.895V118.895C149.53 116.795 148.43 114.795 146.53 113.695L130.93 104.695C129.03 103.595 126.83 103.595 124.93 104.695L109.33 113.695C107.43 114.795 106.33 116.795 106.33 118.895V136.895C106.33 138.995 107.43 140.995 109.33 142.095L124.93 151.095C126.83 152.195 129.03 152.195 130.93 151.095L139.53 146.095L212.74 188.405L132.92 234.515C129.82 236.315 126.02 236.315 122.92 234.515L38 185.505C34.9 183.705 33 180.405 33 176.805V78.785C33 75.185 34.9 71.885 38 70.085L122.92 21.275C126.02 19.475 129.82 19.475 132.92 21.275L217.84 70.285C220.94 72.085 222.84 75.385 222.84 78.985V171.205Z" fill="#616161"/>
</svg>`;
const QIconBlack = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'sagemaker_gen_ai_jupyterlab_extension:q-icon',
    svgstr
});


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   FlareWidget: () => (/* binding */ FlareWidget),
/* harmony export */   connectWebSocket: () => (/* binding */ connectWebSocket),
/* harmony export */   createFlarePanel: () => (/* binding */ createFlarePanel),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _webSocketHandler__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./webSocketHandler */ "./lib/webSocketHandler.js");
/* harmony import */ var _webview__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./webview */ "./lib/webview.js");
/* harmony import */ var _icons_QIconBlack__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./icons/QIconBlack */ "./lib/icons/QIconBlack.js");
/* harmony import */ var _contextMenu__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./contextMenu */ "./lib/contextMenu.js");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _featureFlags__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./featureFlags */ "./lib/featureFlags.js");
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./constants */ "./lib/constants.js");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _services_IngressPointService__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./services/IngressPointService */ "./lib/services/IngressPointService.js");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _observeSettingsChanges__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./observeSettingsChanges */ "./lib/observeSettingsChanges.js");















function connectWebSocket(endPoint = '', docManager) {
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__.ServerConnection.makeSettings();
    const wsUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.URLExt.join(settings.wsUrl, 'sagemaker_gen_ai_jupyterlab_extension', endPoint);
    const socket = new _webSocketHandler__WEBPACK_IMPORTED_MODULE_7__.WebSocketHandler({ url: wsUrl, docManager });
    return socket;
}
class FlareWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget {
    constructor() {
        super();
        console.log('Creating Q Widget');
        this.addClass('jp-FlareWidget');
        this.node.style.height = '100%';
        this.node.style.overflow = 'hidden';
        // Create container for the iframe
        const container = document.createElement('div');
        container.id = 'jp-FlareContainer';
        container.style.width = '100%';
        container.style.height = '100%';
        this.node.appendChild(container);
    }
    onAfterAttach() {
        console.log('Q Widget attached');
        this.loadContent();
    }
    async loadContent() {
        const container = document.getElementById('jp-FlareContainer');
        if (!container)
            return;
        try {
            // Create iframe to load test-client.html
            const iframe = document.createElement('iframe');
            iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups');
            const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__.ServerConnection.makeSettings();
            const baseUrl = settings.baseUrl;
            iframe.src = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.URLExt.join(baseUrl, 'sagemaker_gen_ai_jupyterlab_extension', 'static', 'client.html');
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.border = 'none';
            iframe.referrerPolicy = 'no-referrer';
            iframe.id = _constants__WEBPACK_IMPORTED_MODULE_8__.FLARE_IFRAME_ID;
            // Clear container and add iframe
            container.innerHTML = '';
            container.appendChild(iframe);
        }
        catch (error) {
            container.innerHTML = `<h2>Error Loading Amazon Q Chat</h2><p>${error}</p>`;
        }
    }
}
/**
 * Create a sidebar panel with the Flare widget
 */
function createFlarePanel() {
    console.log('Creating Q Panel');
    const panel = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Panel();
    panel.id = 'flare-panel';
    panel.title.icon = _icons_QIconBlack__WEBPACK_IMPORTED_MODULE_9__.QIconBlack;
    panel.title.caption = 'Amazon Q AI Assistant';
    panel.title.closable = true;
    const flareWidget = new FlareWidget();
    panel.addWidget(flareWidget);
    return panel;
}
const plugin = {
    id: '@amzn/sagemaker_gen_ai_jupyterlab_extension:plugin',
    autoStart: true,
    requires: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabShell, _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_5__.IDocumentManager, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4__.INotebookTracker, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__.ISettingRegistry],
    optional: [],
    activate: async (app, labShell, docManager, notebookTracker, settingRegistry) => {
        console.log('JupyterLab sagemaker_gen_ai_jupyterlab extension activated!', new Date().toISOString());
        const socket = connectWebSocket('ws', docManager);
        if (!socket) {
            console.error('Failed to initialize WebSocket connection. Extension functionality will be limited.');
            return;
        }
        let flarePanel = null;
        // Function to show FlareWidget
        const showFlareWidget = () => {
            try {
                if (!flarePanel) {
                    flarePanel = createFlarePanel();
                    if (!flarePanel) {
                        console.error('Failed to create Q panel');
                        return;
                    }
                    labShell.add(flarePanel, 'left', { rank: Infinity });
                }
                labShell.activateById(flarePanel.id);
            }
            catch (error) {
                console.error('Error showing Q widget:', error);
            }
        };
        try {
            (0,_contextMenu__WEBPACK_IMPORTED_MODULE_10__.registerContextMenuActions)({ app, notebookTracker, showFlareWidget });
        }
        catch (error) {
            console.error('Failed to register context menu actions:', error);
        }
        // update LSP server with settings changes
        (0,_observeSettingsChanges__WEBPACK_IMPORTED_MODULE_11__.observeSettingsChanges)({
            socket,
            settingRegistry,
            pluginId: plugin.id
        });
        setTimeout(() => {
            try {
                flarePanel = createFlarePanel();
                if (flarePanel) {
                    labShell.add(flarePanel, 'left', { rank: Infinity });
                    const ingressPointService = new _services_IngressPointService__WEBPACK_IMPORTED_MODULE_12__.IngressPointService(app, flarePanel);
                    ingressPointService.initialize();
                    (0,_webview__WEBPACK_IMPORTED_MODULE_13__.registerMessageListeners)(socket, window, notebookTracker, docManager, labShell);
                    (0,_featureFlags__WEBPACK_IMPORTED_MODULE_14__.setChatFeatureFlags)(['mcpServers']);
                }
                else {
                    console.error('Failed to create initial Q panel');
                }
            }
            catch (error) {
                console.error('Error during delayed initialization:', error);
            }
        }, 5000);
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/observeSettingsChanges.js":
/*!***************************************!*\
  !*** ./lib/observeSettingsChanges.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   observeSettingsChanges: () => (/* binding */ observeSettingsChanges)
/* harmony export */ });
// this function subscribes to changes to Q settings and passes changes to the LSP server in real-time.
const observeSettingsChanges = async ({ socket, settingRegistry, pluginId }) => {
    settingRegistry === null || settingRegistry === void 0 ? void 0 : settingRegistry.load(pluginId).then(settings => {
        settings === null || settings === void 0 ? void 0 : settings.changed.connect(() => {
            socket.sendNotification({
                command: 'workspace/didChangeConfiguration',
                params: {}
            });
        });
    });
};


/***/ }),

/***/ "./lib/services/IngressPointService.js":
/*!*********************************************!*\
  !*** ./lib/services/IngressPointService.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IngressPointService: () => (/* binding */ IngressPointService)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var wildcard_match__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! wildcard-match */ "webpack/sharing/consume/default/wildcard-match/wildcard-match");
/* harmony import */ var wildcard_match__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(wildcard_match__WEBPACK_IMPORTED_MODULE_1__);



class IngressPointService {
    constructor(app, chatPanel) {
        this.app = app;
        this.chatPanel = chatPanel;
        this.messageListener = async (event) => {
            if (!this.isMessageOriginValid(event))
                return;
            /**
             * When a Q toggle event is passed into the iframe from the parent,
             * this toggles visibility of the Q chat window.
             */
            if (event.data === _constants__WEBPACK_IMPORTED_MODULE_2__.TOGGLE_AI_CHAT_MESSAGE) {
                this.toggleQChat(this.app, this.chatPanel);
                return;
            }
        };
    }
    async initialize() {
        window.addEventListener('message', this.messageListener);
    }
    isMessageOriginValid(event) {
        const allowedDomainPatterns = [
            'https://**.v2.*.beta.app.*.aws.dev',
            'https://**.ui.*.aws.dev',
            'https://**.v2.*-gamma.*.on.aws',
            'https://**.datazone.*.on.aws',
            'https://**.sagemaker.*.on.aws',
            'https://**.sagemaker-gamma.*.on.aws',
        ];
        return allowedDomainPatterns.some((pattern) => wildcard_match__WEBPACK_IMPORTED_MODULE_1___default()(pattern)(event.origin));
    }
    toggleQChat(app, chatPanel) {
        const chatPanelId = chatPanel.id;
        if (!chatPanelId) {
            throw new Error("Chat widget not found.");
        }
        if (app.shell instanceof _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.LabShell) {
            const leftWidgets = Array.from(app.shell.widgets('left'));
            const rightWidgets = Array.from(app.shell.widgets('right'));
            // support finding widgets on left or right panel
            const widgets = [...leftWidgets, ...rightWidgets];
            const chatWidget = widgets.find((widget) => widget.id === chatPanelId);
            if (chatWidget) {
                if (chatWidget.isHidden) {
                    app.shell.activateById(chatPanelId);
                }
                else {
                    if (rightWidgets.find((widget) => widget.id === chatPanelId)) {
                        app.shell.collapseRight();
                    }
                    else {
                        app.shell.collapseLeft();
                    }
                }
            }
        }
    }
}


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   getActiveFileContext: () => (/* binding */ getActiveFileContext),
/* harmony export */   getErrorMessage: () => (/* binding */ getErrorMessage),
/* harmony export */   getSelectionOrCellContent: () => (/* binding */ getSelectionOrCellContent),
/* harmony export */   hasError: () => (/* binding */ hasError),
/* harmony export */   insertToCursorPosition: () => (/* binding */ insertToCursorPosition),
/* harmony export */   interactiveDebuggingInfo: () => (/* binding */ interactiveDebuggingInfo)
/* harmony export */ });
const CELL_MODEL_TYPE = {
    CODE: 'code'
};
const getActiveNotebookCell = (notebookTracker) => {
    const notebook = notebookTracker.currentWidget;
    return notebook ? notebook.content.activeCell : undefined;
};
const insertToCursorPosition = (notebookTracker, code) => {
    const activeCell = getActiveNotebookCell(notebookTracker);
    if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
        const editor = activeCell.editor;
        if (editor) {
            try {
                // Get the current cursor position
                const position = editor.getCursorPosition();
                // Get the current content
                const currentContent = editor.model.sharedModel.source;
                // Split the content at the cursor position
                const beforeCursor = currentContent.substring(0, editor.getOffsetAt(position));
                const afterCursor = currentContent.substring(editor.getOffsetAt(position));
                // Insert the new code at the cursor position
                const newContent = beforeCursor + code + afterCursor;
                // Update the editor content
                editor.model.sharedModel.source = newContent;
                // Move the cursor to the end of the inserted code
                const newPosition = editor.getPositionAt(beforeCursor.length + code.length);
                if (newPosition) {
                    editor.setCursorPosition(newPosition);
                }
            }
            catch (error) {
                console.error('Error inserting the code:', error);
            }
        }
    }
};
// Helper function to get error message text
const getErrorMessage = (notebookTracker) => {
    var _a;
    const activeCell = getActiveNotebookCell(notebookTracker);
    if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
        const outputs = activeCell.model.outputs;
        if (outputs) {
            for (let i = 0; i < outputs.length; i++) {
                const output = outputs.get(i);
                if (output.type === 'error') {
                    return `ErrorType: ${output._raw.ename}; ErrorValue: ${output._raw.evalue}; Trace: ${(_a = output._raw.traceback) === null || _a === void 0 ? void 0 : _a.toString()}`;
                }
            }
        }
    }
    return '';
};
// Helper function to check for errors in cell output
const hasError = (notebookTracker) => {
    const activeCell = getActiveNotebookCell(notebookTracker);
    if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
        const outputs = activeCell.model.outputs;
        if (outputs) {
            for (let i = 0; i < outputs.length; i++) {
                const output = outputs.get(i);
                if (output.type === 'error') {
                    return true;
                }
            }
        }
    }
    return false;
};
const interactiveDebuggingInfo = (notebookTracker) => {
    const activeCell = getActiveNotebookCell(notebookTracker);
    if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
        const outputs = activeCell.model.outputs;
        if (outputs) {
            for (let i = 0; i < outputs.length; i++) {
                const output = outputs.get(i);
                if (output.type === 'display_data' && output.data['application/sagemaker-interactive-debugging']) {
                    const debuggingData = output.data['application/sagemaker-interactive-debugging'];
                    return {
                        instructionFile: debuggingData.instruction_file || "",
                        cellId: activeCell.model.id || "",
                        sessionType: debuggingData.session_type || "",
                        debuggingInfoFolder: debuggingData.debugging_info_folder || "",
                        magicCommand: debuggingData.magic_command || ""
                    };
                }
            }
        }
    }
    // Return null if no debugging info is found
    return null;
};
// Helper function to get selection or cell content
const getSelectionOrCellContent = (notebookTracker, verb) => {
    var _a;
    // For Fix verb, return error message + cell content
    if (verb === 'Fix' && hasError(notebookTracker)) {
        const notebook = notebookTracker.currentWidget;
        const cellContent = ((_a = notebook === null || notebook === void 0 ? void 0 : notebook.content.activeCell) === null || _a === void 0 ? void 0 : _a.model.type) === CELL_MODEL_TYPE.CODE
            ? notebook.content.activeCell.model.sharedModel.getSource()
            : '';
        const errorMessage = getErrorMessage(notebookTracker);
        return `Code:\n${cellContent}\n\nError:\n${errorMessage}`;
    }
    // For other verbs, use normal selection logic
    const activeCell = getActiveNotebookCell(notebookTracker);
    if (activeCell && activeCell.model.type === CELL_MODEL_TYPE.CODE) {
        const editor = activeCell.editor;
        if (editor) {
            const selection = editor.getSelection();
            if (selection.start.line !== selection.end.line ||
                selection.start.column !== selection.end.column) {
                const selectedText = editor.model.sharedModel
                    .getSource()
                    .substring(editor.getOffsetAt(selection.start), editor.getOffsetAt(selection.end));
                if (selectedText.trim()) {
                    return selectedText;
                }
            }
        }
        return activeCell.model.sharedModel.getSource();
    }
    return '';
};
const getActiveFileContext = ({ docManager, labShell }) => {
    const currentWidget = labShell.currentWidget;
    if (!currentWidget) {
        return undefined;
    }
    const context = docManager.contextForWidget(currentWidget);
    if (!context || !context.path) {
        return undefined;
    }
    return {
        path: context.path
    };
};


/***/ }),

/***/ "./lib/webSocketHandler.js":
/*!*********************************!*\
  !*** ./lib/webSocketHandler.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   WebSocketHandler: () => (/* binding */ WebSocketHandler)
/* harmony export */ });
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! uuid */ "webpack/sharing/consume/default/uuid/uuid");
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(uuid__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _webview__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./webview */ "./lib/webview.js");


class WebSocketHandler {
    sendErrorToWebview(title, message, tabId) {
        const errorPayload = {
            command: 'errorMessage',
            params: {
                title,
                message,
                tabId
            }
        };
        (0,_webview__WEBPACK_IMPORTED_MODULE_1__.postToWebView)(errorPayload);
    }
    constructor({ url, docManager, reconnectInterval = 1000, timeout = 600000 }) {
        this.pendingRequests = new Map();
        this.url = url;
        this.reconnectInterval = reconnectInterval;
        this.timeout = timeout;
        this.docManager = docManager;
        this.setupSocket();
    }
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            this.sendNotification({ command: 'ping', params: {} });
        }, 20 * 1000);
    }
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = undefined;
        }
    }
    filterContextCommands(commands) {
        if (!commands) {
            return [];
        }
        const workingCommands = ['Folders', 'Files'];
        return commands
            .filter(contextCommand => workingCommands.includes(contextCommand.command))
            .map(contextCommand => {
            if (!contextCommand.children) {
                return contextCommand;
            }
            return {
                ...contextCommand,
                children: contextCommand.children.map(child => ({
                    ...child,
                    commands: child.commands.filter(c => { var _a, _b, _c; return !(((_a = c === null || c === void 0 ? void 0 : c.command) === null || _a === void 0 ? void 0 : _a.startsWith('.')) || ((_c = (_b = c === null || c === void 0 ? void 0 : c.route) === null || _b === void 0 ? void 0 : _b[1]) === null || _c === void 0 ? void 0 : _c.startsWith('.'))); })
                }))
            };
        });
    }
    setupSocket(maxAttempts = 3) {
        var _a;
        if (((_a = this.socket) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN) {
            return Promise.resolve(true);
        }
        if (this.connectionPromise) {
            return this.connectionPromise;
        }
        this.connectionPromise = new Promise(resolve => {
            let attempts = 0;
            const tryConnect = () => {
                if (attempts >= maxAttempts) {
                    this.connectionPromise = undefined;
                    resolve(false);
                    return;
                }
                attempts++;
                console.log(`Attempting to connect, attempt #${attempts}`);
                const newSocket = new WebSocket(this.url);
                newSocket.onopen = () => {
                    console.log('WebSocket connection established');
                    this.socket = newSocket;
                    this.socket.onmessage = this.onMessage.bind(this);
                    this.startHeartbeat();
                    this.socket.onerror = error => console.error('WebSocket error:', error);
                    this.socket.onclose = event => {
                        console.log('WebSocket connection closed:', event.code, event.reason);
                        this.stopHeartbeat();
                        this.connectionPromise = undefined;
                        this.setupSocket(5);
                    };
                    this.connectionPromise = undefined;
                    resolve(true);
                };
                newSocket.onerror = () => {
                    const delay = this.reconnectInterval * Math.pow(2, attempts - 1);
                    setTimeout(tryConnect, delay);
                };
            };
            tryConnect();
        });
        return this.connectionPromise;
    }
    onMessage(event) {
        if (event.origin && !event.origin.startsWith('wss://')) {
            console.warn(`Rejected message from insecure websocket connection: ${event.origin}`);
            return;
        }
        // Only allow messages from the same origin
        if (event.origin &&
            event.origin.replace('wss://', '') !==
                window.location.origin.replace('https://', '')) {
            console.warn(`Rejected message from unauthorized origin: ${event.origin}`);
            return;
        }
        try {
            const message = JSON.parse(event.data);
            const id = message.id;
            console.log('WebSocket message received:', message);
            if (id) {
                const handler = this.pendingRequests.get(id);
                if (handler) {
                    handler(message);
                }
                else {
                    console.warn(`No handler found for message with id: ${id}`);
                }
            }
            else {
                this.handleInboundEvent(message);
            }
        }
        catch (error) {
            console.error('Error processing message:', error);
            const message = JSON.parse(event.data);
            this.sendErrorToWebview('Message Processing Error', 'Failed to process message, please refresh browser and try again.', message.tabId);
        }
    }
    handleInboundEvent(message) {
        try {
            const command = message.command;
            console.log('Handling inbound event:', { command });
            switch (command) {
                case 'aws/chat/sendChatPrompt':
                case 'aws/chat/buttonClick':
                case 'aws/chat/sendPinnedContext':
                case 'aws/chat/openTab':
                case 'aws/chat/sendChatUpdate':
                case 'aws/chat/chatOptionsUpdate':
                    (0,_webview__WEBPACK_IMPORTED_MODULE_1__.postToWebView)(message);
                    break;
                case 'aws/chat/sendContextCommands': {
                    const contextCommandParams = message.params;
                    const filteredContextCommandGroups = contextCommandParams.contextCommandGroups.map(contextCommandGroup => ({
                        ...contextCommandGroup,
                        commands: this.filterContextCommands(contextCommandGroup === null || contextCommandGroup === void 0 ? void 0 : contextCommandGroup.commands)
                    }));
                    (0,_webview__WEBPACK_IMPORTED_MODULE_1__.postToWebView)({
                        ...message,
                        params: {
                            ...message.params,
                            contextCommandGroups: filteredContextCommandGroups
                        }
                    });
                    break;
                }
                case 'aws/openFileDiff':
                    // TODO: Add diff visual
                    this.docManager.openOrReveal(message.params.originalFileUri.replace('home/sagemaker-user/', ''));
                    break;
                case 'ping':
                    console.log('Received ping');
                    break;
                default:
                    console.log(`Unhandled inbound command: ${command}`);
            }
        }
        catch (error) {
            console.error('Error handling event:', error);
            this.sendErrorToWebview('Event Handling Error', 'Failed to handle inbound event, please refresh browser and try again.', message.tabId);
        }
    }
    async sendRequest(message) {
        const isConnected = await this.setupSocket();
        if (!isConnected) {
            this.sendErrorToWebview('Connection Error', 'WebSocket is not connected, please refresh your page.', message.tabId);
            return Promise.reject(new Error('WebSocket is not connected'));
        }
        const id = (0,uuid__WEBPACK_IMPORTED_MODULE_0__.v4)();
        console.log(`Sending request with id: ${id}, command: ${message.command}`);
        return new Promise((resolve, reject) => {
            const timeoutId = setTimeout(() => {
                this.pendingRequests.delete(id);
                console.error(`Request timed out: ${message.command} (id: ${id})`);
                this.sendErrorToWebview('Request Timeout', `Request timed out: ${message.command}`, message.tabId);
                reject(new Error(`Request timed out: ${message.command}`));
            }, this.timeout);
            this.pendingRequests.set(id, response => {
                clearTimeout(timeoutId);
                this.pendingRequests.delete(id);
                if (response.error) {
                    if (response.error
                        .toLowerCase()
                        .includes('you are not subscribed to amazon q developer')) {
                        this.sendErrorToWebview('No active subscription', response.error, message.tabId);
                    }
                    else if (response.error.includes('Something went wrong')) {
                        this.sendErrorToWebview('Internal Server Error', response.error, message.tabId);
                    }
                    else {
                        this.sendErrorToWebview('Response Error', response.error, message.tabId);
                    }
                    reject(new Error(response.error));
                }
                else {
                    console.log(`Received response for id: ${id}`);
                    resolve(response);
                }
            });
            try {
                const payload = { ...message, id };
                console.log('Sending payload:', payload);
                this.socket.send(JSON.stringify(payload));
            }
            catch (error) {
                clearTimeout(timeoutId);
                this.pendingRequests.delete(id);
                this.sendErrorToWebview('Message Sending Error', 'Failed to send message, please refresh browser and try again.', message.tabId);
                reject(error);
            }
        });
    }
    async sendNotification(message) {
        const isConnected = await this.setupSocket();
        if (isConnected) {
            console.log(`Sending notification: ${message.command}`);
            this.socket.send(JSON.stringify(message));
            return true;
        }
        return false;
    }
}


/***/ }),

/***/ "./lib/webview.js":
/*!************************!*\
  !*** ./lib/webview.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   postToWebView: () => (/* binding */ postToWebView),
/* harmony export */   registerMessageListeners: () => (/* binding */ registerMessageListeners)
/* harmony export */ });
/* harmony import */ var _acknowledgements__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./acknowledgements */ "./lib/acknowledgements.js");
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./constants */ "./lib/constants.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");



const postToWebView = (payload) => {
    const chatFrame = document.getElementById(_constants__WEBPACK_IMPORTED_MODULE_0__.FLARE_IFRAME_ID);
    if (!chatFrame || !chatFrame.contentWindow) {
        throw new Error('Q Chat UI not mounted');
    }
    chatFrame.contentWindow.postMessage(payload, window.location.origin);
};
// Outbound commands
function registerMessageListeners(socket, container, notebookTracker, docManager, labShell) {
    container.addEventListener('message', async (event) => {
        var _a;
        const message = event.data;
        const command = message.command;
        const tabId = (_a = message.params) === null || _a === void 0 ? void 0 : _a.tabId;
        switch (command) {
            case 'aws/chat/sendChatPrompt':
                try {
                    const activeFileContext = (0,_utils__WEBPACK_IMPORTED_MODULE_1__.getActiveFileContext)({
                        docManager,
                        labShell
                    });
                    const response = await socket.sendRequest({
                        ...message,
                        tabId,
                        params: {
                            ...message.params,
                            textDocument: activeFileContext
                                ? {
                                    uri: `file://${_constants__WEBPACK_IMPORTED_MODULE_0__.WORKSPACE_ROOT_PATH}/${activeFileContext === null || activeFileContext === void 0 ? void 0 : activeFileContext.path}`
                                }
                                : undefined,
                            cursorState: [_constants__WEBPACK_IMPORTED_MODULE_0__.DEFAULT_CURSOR_STATE]
                        }
                    });
                    postToWebView(response);
                }
                catch (error) {
                    console.error(error);
                }
                break;
            case 'aws/chat/buttonClick':
            case 'aws/chat/listMcpServers':
            case 'aws/chat/mcpServerClick':
            case 'aws/chat/listConversations':
            case 'aws/chat/listRules':
            case 'aws/chat/conversationClick':
                try {
                    const response = await socket.sendRequest({
                        ...message,
                        tabId
                    });
                    postToWebView(response);
                }
                catch (error) {
                    console.error(error);
                }
                break;
            case 'aws/chat/ready':
                {
                    socket.sendNotification(message);
                    const chatOptionsEvent = {
                        command: 'chatOptions',
                        params: {
                            mcpServers: true,
                            history: true
                        }
                    };
                    postToWebView(chatOptionsEvent);
                    // Temporary fix for MCP Servers not refreshing on ChatUI mount bug
                    const refreshMCPListEvent = {
                        command: 'aws/chat/mcpServerClick',
                        params: {
                            id: 'refresh-mcp-list'
                        }
                    };
                    window.postMessage(refreshMCPListEvent, '*');
                }
                break;
            case 'aws/chat/sendChatQuickAction':
                try {
                    const response = await socket.sendRequest({
                        ...message,
                        tabId
                    });
                    const quickAction = message.params.quickAction;
                    if (quickAction === _constants__WEBPACK_IMPORTED_MODULE_0__.QUICK_ACTIONS.HELP) {
                        postToWebView({
                            ...response,
                            command: 'aws/chat/sendChatPrompt'
                        });
                        return;
                    }
                    if (typeof quickAction === 'string' &&
                        [
                            _constants__WEBPACK_IMPORTED_MODULE_0__.QUICK_ACTIONS.FIX,
                            _constants__WEBPACK_IMPORTED_MODULE_0__.QUICK_ACTIONS.EXPLAIN,
                            _constants__WEBPACK_IMPORTED_MODULE_0__.QUICK_ACTIONS.OPTIMIZE,
                            _constants__WEBPACK_IMPORTED_MODULE_0__.QUICK_ACTIONS.REFACTOR
                        ].includes(quickAction)) {
                        const command = quickAction.slice(1); // removes leading slash
                        postToWebView({
                            command: 'genericCommand',
                            params: {
                                genericCommand: command,
                                selection: message.params.prompt ||
                                    (0,_utils__WEBPACK_IMPORTED_MODULE_1__.getSelectionOrCellContent)(notebookTracker, command === 'fix' ? 'Fix' : undefined),
                                triggerType: 'contextMenu'
                            }
                        });
                    }
                }
                catch (error) {
                    console.error(error);
                }
                break;
            case 'aws/chat/tabAdd':
            case 'aws/chat/tabChange':
            case 'aws/chat/tabRemove':
            case 'aws/chat/pinnedContextAdd':
            case 'aws/chat/pinnedContextRemove':
            case 'aws/chat/createPrompt':
            case 'aws/chat/fileClick':
            case 'stopChatResponse':
            case 'aws/chat/openTab':
            case 'aws/chat/promptInputOptionChange':
                socket.sendNotification(message);
                break;
            case 'chatPromptOptionAcknowledged':
            case 'disclaimerAcknowledged':
                (0,_acknowledgements__WEBPACK_IMPORTED_MODULE_2__.storeAcknowledgements)(command);
                break;
            case 'aws/chat/linkClick':
            case 'aws/chat/infoLinkClick':
                // post a message to the iframe parent (SMUS app shell)
                // app shell will be responsible for opening the link
                const openLinkMessage = {
                    type: 'openLink',
                    url: message.params.link
                };
                window.parent.postMessage(openLinkMessage, '*');
                break;
            case 'insertToCursorPosition': {
                if (notebookTracker && message.params) {
                    const code = message.params.code;
                    if (code) {
                        (0,_utils__WEBPACK_IMPORTED_MODULE_1__.insertToCursorPosition)(notebookTracker, code);
                    }
                }
                break;
            }
            default:
                // Uncomment the following for debugging/development purposes
                // console.log(`Unhandled outbound command: ${command}`);
                break;
        }
    });
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.970a625f07162b2e1f1c.js.map