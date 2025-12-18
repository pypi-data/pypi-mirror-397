"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["5395"], {
95328(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.d(__webpack_exports__, {
  K: () => (__name)
});
var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });




},
36222(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (layouts_default)
});
/* import */ var _chunks_mermaid_layout_elk_core_chunk_ZW26E7AF_mjs__rspack_import_0 = __webpack_require__(95328);


// src/layouts.ts
var loader = /* @__PURE__ */ (0,_chunks_mermaid_layout_elk_core_chunk_ZW26E7AF_mjs__rspack_import_0/* .__name */.K)(async () => await Promise.all(/* import() */ [__webpack_require__.e("7103"), __webpack_require__.e("2715"), __webpack_require__.e("8174")]).then(__webpack_require__.bind(__webpack_require__, 78173)), "loader");
var algos = ["elk.stress", "elk.force", "elk.mrtree", "elk.sporeOverlap"];
var layouts = [
  {
    name: "elk",
    loader,
    algorithm: "elk.layered"
  },
  ...algos.map((algo) => ({
    name: algo,
    loader,
    algorithm: algo
  }))
];
var layouts_default = layouts;



},

}]);
//# sourceMappingURL=5395.d2c2e1ea5807ed0a.js.map?v=d2c2e1ea5807ed0a