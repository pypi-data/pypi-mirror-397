"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["273"], {
77048(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__rspack_default_export)
});
/* import */ var _jupyterlab_application__rspack_import_0 = __webpack_require__(11158);
/* import */ var _jupyterlab_application__rspack_import_0_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__rspack_import_0);
/* import */ var _jupyterlab_coreutils__rspack_import_1 = __webpack_require__(3744);
/* import */ var _jupyterlab_coreutils__rspack_import_1_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__rspack_import_1);
/* import */ var _jupyterlab_terminal__rspack_import_2 = __webpack_require__(68678);
/* import */ var _jupyterlab_terminal__rspack_import_2_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_terminal__rspack_import_2);
/* import */ var _jupyter_notebook_application__rspack_import_3 = __webpack_require__(41440);
/* import */ var _jupyter_notebook_application__rspack_import_3_default = /*#__PURE__*/__webpack_require__.n(_jupyter_notebook_application__rspack_import_3);
/* import */ var _lumino_algorithm__rspack_import_4 = __webpack_require__(86554);
/* import */ var _lumino_algorithm__rspack_import_4_default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__rspack_import_4);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.





/**
 * A plugin to open terminals in a new tab
 */
const opener = {
    id: '@jupyter-notebook/terminal-extension:opener',
    description: 'A plugin to open terminals in a new tab.',
    requires: [_jupyterlab_application__rspack_import_0.IRouter, _jupyterlab_terminal__rspack_import_2.ITerminalTracker],
    autoStart: true,
    activate: (app, router, tracker) => {
        const { commands } = app;
        const terminalPattern = new RegExp('/terminals/(.*)');
        const command = 'router:terminal';
        commands.addCommand(command, {
            execute: (args) => {
                const parsed = args;
                const matches = parsed.path.match(terminalPattern);
                if (!matches) {
                    return;
                }
                const [, name] = matches;
                if (!name) {
                    return;
                }
                tracker.widgetAdded.connect((send, terminal) => {
                    terminal.content.setOption('closeOnExit', false);
                });
                commands.execute('terminal:open', { name });
            },
        });
        router.register({ command, pattern: terminalPattern });
    },
};
/**
 * Open terminals in a new tab.
 */
const redirect = {
    id: '@jupyter-notebook/terminal-extension:redirect',
    description: 'Open terminals in a new tab.',
    requires: [_jupyterlab_terminal__rspack_import_2.ITerminalTracker],
    optional: [_jupyter_notebook_application__rspack_import_3.INotebookPathOpener],
    autoStart: true,
    activate: (app, tracker, notebookPathOpener) => {
        const baseUrl = _jupyterlab_coreutils__rspack_import_1.PageConfig.getBaseUrl();
        const opener = notebookPathOpener !== null && notebookPathOpener !== void 0 ? notebookPathOpener : _jupyter_notebook_application__rspack_import_3.defaultNotebookPathOpener;
        tracker.widgetAdded.connect((send, terminal) => {
            const widget = (0,_lumino_algorithm__rspack_import_4.find)(app.shell.widgets('main'), (w) => w.id === terminal.id);
            if (widget) {
                // bail if the terminal is already added to the main area
                return;
            }
            const name = terminal.content.session.name;
            opener.open({
                prefix: _jupyterlab_coreutils__rspack_import_1.URLExt.join(baseUrl, 'terminals'),
                path: name,
                target: '_blank',
            });
            // dispose the widget since it is not used on this page
            terminal.dispose();
        });
    },
};
/**
 * Export the plugins as default.
 */
const plugins = [opener, redirect];
/* export default */ const __rspack_default_export = (plugins);


},

}]);
//# sourceMappingURL=273.0665a7a9d14fc600.js.map?v=0665a7a9d14fc600