"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["1320"], {
44987(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.d(__webpack_exports__, {
  diff: () => (diff)
});
var TOKEN_NAMES = {
  '+': 'inserted',
  '-': 'deleted',
  '@': 'meta'
};

const diff = {
  name: "diff",
  token: function(stream) {
    var tw_pos = stream.string.search(/[\t ]+?$/);

    if (!stream.sol() || tw_pos === 0) {
      stream.skipToEnd();
      return ("error " + (
        TOKEN_NAMES[stream.string.charAt(0)] || '')).replace(/ $/, '');
    }

    var token_name = TOKEN_NAMES[stream.peek()] || stream.skipToEnd();

    if (tw_pos === -1) {
      stream.skipToEnd();
    } else {
      stream.pos = tw_pos;
    }

    return token_name;
  }
};



},

}]);
//# sourceMappingURL=1320.341192a76cdc0fec.js.map?v=341192a76cdc0fec