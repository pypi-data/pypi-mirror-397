"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["2320"], {
46051(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__rspack_default_export)
});
/* import */ var _jupyterlab_apputils__rspack_import_0 = __webpack_require__(3877);
/* import */ var _jupyterlab_apputils__rspack_import_0_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__rspack_import_0);
/* import */ var _jupyterlab_mainmenu__rspack_import_1 = __webpack_require__(12542);
/* import */ var _jupyterlab_mainmenu__rspack_import_1_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__rspack_import_1);
/* import */ var _jupyterlab_translation__rspack_import_2 = __webpack_require__(53816);
/* import */ var _jupyterlab_translation__rspack_import_2_default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__rspack_import_2);
/* import */ var _jupyter_notebook_ui_components__rspack_import_3 = __webpack_require__(31918);
/* import */ var _jupyter_notebook_ui_components__rspack_import_3_default = /*#__PURE__*/__webpack_require__.n(_jupyter_notebook_ui_components__rspack_import_3);
/* import */ var react__rspack_import_4 = __webpack_require__(38550);
/* import */ var react__rspack_import_4_default = /*#__PURE__*/__webpack_require__.n(react__rspack_import_4);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.





/**
 * A list of resources to show in the help menu.
 */
const RESOURCES = [
    {
        text: 'About Jupyter',
        url: 'https://jupyter.org',
    },
    {
        text: 'Markdown Reference',
        url: 'https://commonmark.org/help/',
    },
    {
        text: 'Documentation',
        url: 'https://jupyter-notebook.readthedocs.io/en/stable/',
    },
];
/**
 * The command IDs used by the help plugin.
 */
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.open = 'help:open';
    CommandIDs.about = 'help:about';
})(CommandIDs || (CommandIDs = {}));
/**
 * A plugin to open the about section with resources.
 */
const open = {
    id: '@jupyter-notebook/help-extension:open',
    autoStart: true,
    description: 'A plugin to open the about section with resources',
    activate: (app) => {
        const { commands } = app;
        commands.addCommand(CommandIDs.open, {
            label: (args) => args['text'],
            execute: (args) => {
                const url = args['url'];
                window.open(url);
            },
        });
    },
};
/**
 * Plugin to add a command to show an About Jupyter Notebook and Markdown Reference.
 */
const about = {
    id: '@jupyter-notebook/help-extension:about',
    autoStart: true,
    requires: [_jupyterlab_translation__rspack_import_2.ITranslator],
    optional: [_jupyterlab_mainmenu__rspack_import_1.IMainMenu, _jupyterlab_apputils__rspack_import_0.ICommandPalette],
    description: 'Plugin to add a command to show an About Jupyter Notebook and Markdown Reference',
    activate: (app, translator, menu, palette) => {
        const { commands } = app;
        const trans = translator.load('notebook');
        const category = trans.__('Help');
        commands.addCommand(CommandIDs.about, {
            label: trans.__('About %1', app.name),
            execute: () => {
                const title = (react__rspack_import_4.createElement(react__rspack_import_4.Fragment, null,
                    react__rspack_import_4.createElement("span", { className: "jp-AboutNotebook-header" },
                        react__rspack_import_4.createElement(_jupyter_notebook_ui_components__rspack_import_3.jupyterIcon.react, { width: "196px", height: "auto" }))));
                const notebookURL = 'https://github.com/jupyter/notebook';
                const contributorURL = 'https://github.com/jupyter/notebook/pulse';
                const aboutJupyter = trans.__('JUPYTER NOTEBOOK ON GITHUB');
                const contributorList = trans.__('CONTRIBUTOR LIST');
                const externalLinks = (react__rspack_import_4.createElement("span", null,
                    react__rspack_import_4.createElement("a", { href: notebookURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat jp-AboutNotebook-about-externalLinks" }, aboutJupyter),
                    react__rspack_import_4.createElement("a", { href: contributorURL, target: "_blank", rel: "noopener noreferrer", className: "jp-Button-flat jp-AboutNotebook-about-externalLinks" }, contributorList)));
                const version = trans.__('Version: %1', app.version);
                const copyright = trans.__('© 2021-2023 Jupyter Notebook Contributors');
                const body = (react__rspack_import_4.createElement(react__rspack_import_4.Fragment, null,
                    react__rspack_import_4.createElement("span", { className: "jp-AboutNotebook-version" }, version),
                    react__rspack_import_4.createElement("div", null, externalLinks),
                    react__rspack_import_4.createElement("span", { className: "jp-AboutNotebook-about-copyright" }, copyright)));
                const dialog = new _jupyterlab_apputils__rspack_import_0.Dialog({
                    title,
                    body,
                    buttons: [
                        _jupyterlab_apputils__rspack_import_0.Dialog.createButton({
                            label: trans.__('Dismiss'),
                            className: 'jp-AboutNotebook-about-button jp-mod-reject jp-mod-styled',
                        }),
                    ],
                });
                dialog.addClass('jp-AboutNotebook');
                void dialog.launch();
            },
        });
        if (palette) {
            palette.addItem({ command: CommandIDs.about, category });
        }
        const resourcesGroup = RESOURCES.map((args) => ({
            args,
            command: CommandIDs.open,
        }));
        if (menu) {
            menu.helpMenu.addGroup(resourcesGroup, 30);
        }
    },
};
const plugins = [open, about];
/* export default */ const __rspack_default_export = (plugins);


},

}]);
//# sourceMappingURL=2320.7b0b62dea3e94751.js.map?v=7b0b62dea3e94751