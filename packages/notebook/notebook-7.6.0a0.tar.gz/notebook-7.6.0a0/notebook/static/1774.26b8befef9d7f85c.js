"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["1774"], {
77965(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__rspack_default_export)
});
/* import */ var _jupyterlab_application__rspack_import_0 = __webpack_require__(11158);
/* import */ var _jupyterlab_application__rspack_import_0_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__rspack_import_0);
/* import */ var _jupyterlab_console__rspack_import_1 = __webpack_require__(75272);
/* import */ var _jupyterlab_console__rspack_import_1_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_console__rspack_import_1);
/* import */ var _jupyterlab_coreutils__rspack_import_2 = __webpack_require__(3744);
/* import */ var _jupyterlab_coreutils__rspack_import_2_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__rspack_import_2);
/* import */ var _jupyter_notebook_application__rspack_import_3 = __webpack_require__(41440);
/* import */ var _jupyter_notebook_application__rspack_import_3_default = /*#__PURE__*/__webpack_require__.n(_jupyter_notebook_application__rspack_import_3);
/* import */ var _lumino_algorithm__rspack_import_4 = __webpack_require__(86554);
/* import */ var _lumino_algorithm__rspack_import_4_default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__rspack_import_4);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.





/**
 * A plugin to open consoles in a new tab
 */
const opener = {
    id: '@jupyter-notebook/console-extension:opener',
    requires: [_jupyterlab_application__rspack_import_0.IRouter],
    autoStart: true,
    description: 'A plugin to open consoles in a new tab',
    activate: (app, router) => {
        const { commands } = app;
        const consolePattern = new RegExp('/consoles/(.*)');
        const command = 'router:console';
        commands.addCommand(command, {
            execute: (args) => {
                const parsed = args;
                const matches = parsed.path.match(consolePattern);
                if (!matches) {
                    return;
                }
                const [, match] = matches;
                if (!match) {
                    return;
                }
                const path = decodeURIComponent(match);
                commands.execute('console:create', { path });
            },
        });
        router.register({ command, pattern: consolePattern });
    },
};
/**
 * Open consoles in a new tab.
 */
const redirect = {
    id: '@jupyter-notebook/console-extension:redirect',
    requires: [_jupyterlab_console__rspack_import_1.IConsoleTracker],
    optional: [_jupyter_notebook_application__rspack_import_3.INotebookPathOpener],
    autoStart: true,
    description: 'Open consoles in a new tab',
    activate: (app, tracker, notebookPathOpener) => {
        const baseUrl = _jupyterlab_coreutils__rspack_import_2.PageConfig.getBaseUrl();
        const opener = notebookPathOpener !== null && notebookPathOpener !== void 0 ? notebookPathOpener : _jupyter_notebook_application__rspack_import_3.defaultNotebookPathOpener;
        tracker.widgetAdded.connect(async (send, console) => {
            const { sessionContext } = console;
            await sessionContext.ready;
            const widget = (0,_lumino_algorithm__rspack_import_4.find)(app.shell.widgets('main'), (w) => w.id === console.id);
            if (widget) {
                // bail if the console is already added to the main area
                return;
            }
            opener.open({
                prefix: _jupyterlab_coreutils__rspack_import_2.URLExt.join(baseUrl, 'consoles'),
                path: sessionContext.path,
                target: '_blank',
            });
            // the widget is not needed anymore
            console.dispose();
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
//# sourceMappingURL=1774.26b8befef9d7f85c.js.map?v=26b8befef9d7f85c