"use strict";
(self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] = self["webpackChunk_JUPYTERLAB_CORE_OUTPUT"] || []).push([["5062"], {
71984(__unused_rspack_module, __webpack_exports__, __webpack_require__) {
__webpack_require__.d(__webpack_exports__, {
  spreadsheet: () => (spreadsheet)
});
const spreadsheet = {
  name: "spreadsheet",

  startState: function () {
    return {
      stringType: null,
      stack: []
    };
  },
  token: function (stream, state) {
    if (!stream) return;

    //check for state changes
    if (state.stack.length === 0) {
      //strings
      if ((stream.peek() == '"') || (stream.peek() == "'")) {
        state.stringType = stream.peek();
        stream.next(); // Skip quote
        state.stack.unshift("string");
      }
    }

    //return state
    //stack has
    switch (state.stack[0]) {
    case "string":
      while (state.stack[0] === "string" && !stream.eol()) {
        if (stream.peek() === state.stringType) {
          stream.next(); // Skip quote
          state.stack.shift(); // Clear flag
        } else if (stream.peek() === "\\") {
          stream.next();
          stream.next();
        } else {
          stream.match(/^.[^\\\"\']*/);
        }
      }
      return "string";

    case "characterClass":
      while (state.stack[0] === "characterClass" && !stream.eol()) {
        if (!(stream.match(/^[^\]\\]+/) || stream.match(/^\\./)))
          state.stack.shift();
      }
      return "operator";
    }

    var peek = stream.peek();

    //no stack
    switch (peek) {
    case "[":
      stream.next();
      state.stack.unshift("characterClass");
      return "bracket";
    case ":":
      stream.next();
      return "operator";
    case "\\":
      if (stream.match(/\\[a-z]+/)) return "string.special";
      else {
        stream.next();
        return "atom";
      }
    case ".":
    case ",":
    case ";":
    case "*":
    case "-":
    case "+":
    case "^":
    case "<":
    case "/":
    case "=":
      stream.next();
      return "atom";
    case "$":
      stream.next();
      return "builtin";
    }

    if (stream.match(/\d+/)) {
      if (stream.match(/^\w+/)) return "error";
      return "number";
    } else if (stream.match(/^[a-zA-Z_]\w*/)) {
      if (stream.match(/(?=[\(.])/, false)) return "keyword";
      return "variable";
    } else if (["[", "]", "(", ")", "{", "}"].indexOf(peek) != -1) {
      stream.next();
      return "bracket";
    } else if (!stream.eatSpace()) {
      stream.next();
    }
    return null;
  }
};


},

}]);
//# sourceMappingURL=5062.df4873e7086d7e42.js.map?v=df4873e7086d7e42