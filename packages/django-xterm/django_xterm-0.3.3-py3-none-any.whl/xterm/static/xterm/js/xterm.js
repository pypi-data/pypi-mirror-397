"use strict";

(function () {
  // vrt. https://github.com/Om3rr/pyxtermjs/master/pyxtermjs/index.html

  function fitToScreen (websocket, term, fit){
    if (websocket && term && fit) {
      fit.fit();
      websocket.send(JSON.stringify({cols: term.cols, rows: term.rows}))
    }
  }
  function debounce(func, wait_ms) {
    let timeout
    return function(...args) {
      const context = this
      clearTimeout(timeout)
      timeout = setTimeout(function () { func.apply(context, args); }, wait_ms)
    }
  }

  fitToScreen = debounce(fitToScreen, 50);

  function XtermJS (url, asetukset, uuid) {
    Object.assign(this, {url, asetukset, uuid});

    this._term = null;
    this._kantoaalto = new Kantoaalto(url, {
      kattelydata: JSON.stringify({csrfmiddlewaretoken: poimiCsrf()}),
    });
    this._fit = null;
  }

  Object.assign(XtermJS.prototype, {
    /*
     * Palautetaan sitoumus, joka täyttyy, kun WebSocket-yhteys on avattu.
     */
    avaa: function () {
      return new Promise(function (resolve, reject) {
        websocket = new WebSocket(this.url);
        websocket.onopen = function () {
          resolve(websocket);
          setTimeout(
            fitToScreen.bind(null, websocket, this._term, this._fit),
            0
          );
        };
        websocket.onclose = function (e) {
          if (e.code > 1001) {
            // Muu kuin normaali katkaisu.
            if (uuid != undefined)
              avaa(uuid);
            term.write(`\r\n\x1B[31mYhteys katkesi (${e.code})!\x1B[0m`)
          }
        };
        websocket.onmessage = function (e) {
          term.write(e.data)
        };
      });
    },

    // _websocketAvattu: function (e) {
    //   resolve(this._websocket);
    //   setTimeout(
    //     fitToScreen.bind(null, websocket, this._term, this._fit),
    //     0
    //   );
    // }
  });

  let term = null;
  let websocket = null;
  let fit = null;

  window.addEventListener(
    "resize",
    fitToScreen.bind(null, websocket, term, fit),
    {passive: true}
  );

  window.avaaXterm = function (url, asetukset, uuid) {
    return new Promise(function (resolve, reject) {
      if (term)
        term.dispose();
      if (websocket)
        websocket.close(1000);  // Normaali katkaisu.

      term = new Terminal(asetukset);
      fit = new FitAddon.FitAddon();
      term.loadAddon(fit);
      term.loadAddon(new WebLinksAddon.WebLinksAddon());
      term.loadAddon(new SearchAddon.SearchAddon());
      term.open(document.getElementById('xterm'));
      fit.fit()
      term.onData(function (data) {
        websocket.send(new Blob(data.split()));
      });

      websocket = new WebSocket(url);
      websocket.onopen = function () {
        resolve(websocket);
        setTimeout(fitToScreen.bind(null, websocket, term, fit), 0);
      };
      websocket.onclose = function (e) {
        if (e.code > 1001) {
          // Muu kuin normaali katkaisu.
          if (uuid)
            ;
          else
            term.write(`\r\n\x1B[31mYhteys katkesi (${e.code})!\x1B[0m`)
        }
      };
      websocket.onmessage = function (e) {
        term.write(e.data)
      };
    });
  };
})();
