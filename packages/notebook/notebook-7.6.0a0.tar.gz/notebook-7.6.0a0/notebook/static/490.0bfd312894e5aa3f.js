"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["490"], {
52913(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__rspack_default_export)
});
/* import */ var _jupyterlab_coreutils__rspack_import_0 = __webpack_require__(3744);
/* import */ var _jupyterlab_coreutils__rspack_import_0_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__rspack_import_0);
/* import */ var _jupyterlab_docmanager__rspack_import_1 = __webpack_require__(31430);
/* import */ var _jupyterlab_docmanager__rspack_import_1_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__rspack_import_1);
/* import */ var _jupyter_notebook_application__rspack_import_2 = __webpack_require__(41440);
/* import */ var _jupyter_notebook_application__rspack_import_2_default = /*#__PURE__*/__webpack_require__.n(_jupyter_notebook_application__rspack_import_2);
/* import */ var _lumino_signaling__rspack_import_3 = __webpack_require__(16324);
/* import */ var _lumino_signaling__rspack_import_3_default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__rspack_import_3);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.




/**
 * A plugin to open documents in a new browser tab.
 *
 */
const opener = {
    id: '@jupyter-notebook/docmanager-extension:opener',
    autoStart: true,
    optional: [_jupyter_notebook_application__rspack_import_2.INotebookPathOpener, _jupyter_notebook_application__rspack_import_2.INotebookShell],
    provides: _jupyterlab_docmanager__rspack_import_1.IDocumentWidgetOpener,
    description: 'Open documents in a new browser tab',
    activate: (app, notebookPathOpener, notebookShell) => {
        const baseUrl = _jupyterlab_coreutils__rspack_import_0.PageConfig.getBaseUrl();
        const docRegistry = app.docRegistry;
        const pathOpener = notebookPathOpener !== null && notebookPathOpener !== void 0 ? notebookPathOpener : _jupyter_notebook_application__rspack_import_2.defaultNotebookPathOpener;
        let id = 0;
        return new (class {
            constructor() {
                this._opened = new _lumino_signaling__rspack_import_3.Signal(this);
            }
            async open(widget, options) {
                var _a, _b, _c;
                const widgetName = (_a = options === null || options === void 0 ? void 0 : options.type) !== null && _a !== void 0 ? _a : '';
                const ref = options === null || options === void 0 ? void 0 : options.ref;
                // check if there is an setting override and if it would add the widget in the main area
                const userLayoutArea = (_c = (_b = notebookShell === null || notebookShell === void 0 ? void 0 : notebookShell.userLayout) === null || _b === void 0 ? void 0 : _b[widgetName]) === null || _c === void 0 ? void 0 : _c.area;
                if (ref !== '_noref' && userLayoutArea === undefined) {
                    const path = widget.context.path;
                    const ext = _jupyterlab_coreutils__rspack_import_0.PathExt.extname(path);
                    let route = 'edit';
                    if ((widgetName === 'default' && ext === '.ipynb') ||
                        widgetName.includes('Notebook')) {
                        // make sure to save the notebook before opening it in a new tab
                        // so the kernel info is saved (if created from the New dropdown)
                        if (widget.context.sessionContext.kernelPreference.name) {
                            await widget.context.save();
                        }
                        route = 'notebooks';
                    }
                    // append ?factory only if it's not the default
                    const defaultFactory = docRegistry.defaultWidgetFactory(path);
                    let searchParams = undefined;
                    if (widgetName !== defaultFactory.name) {
                        searchParams = new URLSearchParams({
                            factory: widgetName,
                        });
                    }
                    pathOpener.open({
                        prefix: _jupyterlab_coreutils__rspack_import_0.URLExt.join(baseUrl, route),
                        path,
                        searchParams,
                    });
                    // dispose the widget since it is not used on this page
                    widget.dispose();
                    return;
                }
                // otherwise open the document on the current page
                if (!widget.id) {
                    widget.id = `document-manager-${++id}`;
                }
                widget.title.dataset = {
                    type: 'document-title',
                    ...widget.title.dataset,
                };
                if (!widget.isAttached) {
                    app.shell.add(widget, 'main', options || {});
                }
                app.shell.activateById(widget.id);
                this._opened.emit(widget);
            }
            get opened() {
                return this._opened;
            }
        })();
    },
};
/**
 * Export the plugins as default.
 */
const plugins = [opener];
/* export default */ const __rspack_default_export = (plugins);


},

}]);
//# sourceMappingURL=490.0bfd312894e5aa3f.js.map?v=0bfd312894e5aa3f