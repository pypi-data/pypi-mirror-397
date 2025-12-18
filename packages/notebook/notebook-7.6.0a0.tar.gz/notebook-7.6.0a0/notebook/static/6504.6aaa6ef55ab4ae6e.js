"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["6504"], {
23547(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.d(__webpack_exports__, {
  diagram: () => (diagram)
});
/* import */ var _chunk_6MN3ZHY7_mjs__rspack_import_4 = __webpack_require__(95792);
/* import */ var _chunk_EXTU4WIE_mjs__rspack_import_0 = __webpack_require__(26859);
/* import */ var _chunk_ABZYJK2D_mjs__rspack_import_1 = __webpack_require__(21065);
/* import */ var _chunk_AGHRB4JF_mjs__rspack_import_2 = __webpack_require__(87724);
/* import */ var _mermaid_js_parser__rspack_import_3 = __webpack_require__(11150);





// src/diagrams/info/infoParser.ts

var parser = {
  parse: /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__rspack_import_2/* .__name */.K2)(async (input) => {
    const ast = await (0,_mermaid_js_parser__rspack_import_3/* .parse */.qg)("info", input);
    _chunk_AGHRB4JF_mjs__rspack_import_2/* .log.debug */.Rm.debug(ast);
  }, "parse")
};

// src/diagrams/info/infoDb.ts
var DEFAULT_INFO_DB = {
  version: _chunk_6MN3ZHY7_mjs__rspack_import_4/* .package_default.version */.n.version + ( true ? "" : 0)
};
var getVersion = /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__rspack_import_2/* .__name */.K2)(() => DEFAULT_INFO_DB.version, "getVersion");
var db = {
  getVersion
};

// src/diagrams/info/infoRenderer.ts
var draw = /* @__PURE__ */ (0,_chunk_AGHRB4JF_mjs__rspack_import_2/* .__name */.K2)((text, id, version) => {
  _chunk_AGHRB4JF_mjs__rspack_import_2/* .log.debug */.Rm.debug("rendering info diagram\n" + text);
  const svg = (0,_chunk_EXTU4WIE_mjs__rspack_import_0/* .selectSvgElement */.D)(id);
  (0,_chunk_ABZYJK2D_mjs__rspack_import_1/* .configureSvgSize */.a$)(svg, 100, 400, true);
  const group = svg.append("g");
  group.append("text").attr("x", 100).attr("y", 40).attr("class", "version").attr("font-size", 32).style("text-anchor", "middle").text(`v${version}`);
}, "draw");
var renderer = { draw };

// src/diagrams/info/infoDiagram.ts
var diagram = {
  parser,
  db,
  renderer
};



},

}]);
//# sourceMappingURL=6504.6aaa6ef55ab4ae6e.js.map?v=6aaa6ef55ab4ae6e