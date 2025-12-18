"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["1682"], {
33081(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__rspack_default_export)
});
/* import */ var _jupyterlab_documentsearch__rspack_import_0 = __webpack_require__(14038);
/* import */ var _jupyterlab_documentsearch__rspack_import_0_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_documentsearch__rspack_import_0);
/* import */ var _jupyter_notebook_application__rspack_import_1 = __webpack_require__(41440);
/* import */ var _jupyter_notebook_application__rspack_import_1_default = /*#__PURE__*/__webpack_require__.n(_jupyter_notebook_application__rspack_import_1);


const SEARCHABLE_CLASS = 'jp-mod-searchable';
/**
 * A plugin to add document search functionalities.
 */
const notebookShellWidgetListener = {
    id: '@jupyter-notebook/documentsearch-extension:notebookShellWidgetListener',
    requires: [_jupyter_notebook_application__rspack_import_1.INotebookShell, _jupyterlab_documentsearch__rspack_import_0.ISearchProviderRegistry],
    autoStart: true,
    description: 'A plugin to add document search functionalities',
    activate: (app, notebookShell, registry) => {
        // If a given widget is searchable, apply the searchable class.
        // If it's not searchable, remove the class.
        const transformWidgetSearchability = (widget) => {
            if (!widget) {
                return;
            }
            if (registry.hasProvider(widget)) {
                widget.addClass(SEARCHABLE_CLASS);
            }
            else {
                widget.removeClass(SEARCHABLE_CLASS);
            }
        };
        // Update searchability of the active widget when the registry
        // changes, in case a provider for the current widget was added
        // or removed
        registry.changed.connect(() => transformWidgetSearchability(notebookShell.currentWidget));
        // Apply the searchable class only to the active widget if it is actually
        // searchable. Remove the searchable class from a widget when it's
        // no longer active.
        notebookShell.currentChanged.connect((_, args) => {
            if (notebookShell.currentWidget) {
                transformWidgetSearchability(notebookShell.currentWidget);
            }
        });
    },
};
/**
 * Export the plugins as default.
 */
const plugins = [notebookShellWidgetListener];
/* export default */ const __rspack_default_export = (plugins);


},

}]);
//# sourceMappingURL=1682.0740fba5e398ccef.js.map?v=0740fba5e398ccef