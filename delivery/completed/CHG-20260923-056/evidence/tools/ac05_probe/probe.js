// The AC-05 / T-09 probe: runs inside the real WebView of the real Desktop
// binary, and reports through the product's own `log_js_error` command, which
// prints to the Desktop process's stdout as `[WEBVIEW] <message>`.
//
// Nothing here is a mock. Each line the driver asserts on is the page's own
// account of what the running application did:
//
//   Boot             -- did the page load under the Tauri protocol at all, and
//                       does the native IPC bridge exist?
//   PublicConfig     -- what does `get_public_config` answer? The driver pins
//                       it against the config file that launch was given.
//   CspFetchCloud    -- a real `fetch` to the Cloud origin the config names.
//   CspFetchLoopback -- the same fetch, same Cloud, by its other name
//                       (`localhost` instead of `127.0.0.1`). No config allows
//                       both, so this leg must be blocked in every launch: it is
//                       the control that keeps "blocked" from being read as
//                       "this launch is broken".
//   AgentStart       -- which spawn path ran (the returned label).
//   AgentHealth      -- does the Agent answer the native client, which means it
//                       was told the port the client calls and the token the
//                       client presents?
//
// The report is deliberately one line per fact and never includes a secret: the
// token is not known to the page and is never part of any payload.

(function () {
  "use strict";

  var invoke =
    window.__TAURI_INTERNALS__ && window.__TAURI_INTERNALS__.invoke;

  function report(tag, payload) {
    var message = "AC05 " + tag + " " + JSON.stringify(payload);
    if (!invoke) {
      return; // Nothing left to report with; the driver turns this into a HARD STOP.
    }
    try {
      invoke("log_js_error", { message: message, stack: "" });
    } catch (error) {
      /* the driver's timeout covers this */
    }
  }

  // Installed before anything else, so a violation is on the wire even if a
  // later step never returns.
  var violations = [];
  document.addEventListener("securitypolicyviolation", function (event) {
    violations.push({
      directive: event.violatedDirective,
      blocked: event.blockedURI,
      policy: event.originalPolicy,
    });
    report("Violation", {
      directive: event.violatedDirective,
      blocked: event.blockedURI,
    });
  });

  function settle() {
    // The violation event is dispatched around the promise rejection rather than
    // strictly before it, so the count is taken after the dust settles.
    return new Promise(function (resolve) {
      setTimeout(resolve, 150);
    });
  }

  function tryFetch(tag, url) {
    var seen = violations.length;
    return fetch(url, { mode: "no-cors", cache: "no-store" }).then(
      function () {
        return settle().then(function () {
          report(tag, {
            url: url,
            outcome: "resolved",
            error: "",
            violations: violations.slice(seen),
          });
        });
      },
      function (error) {
        return settle().then(function () {
          report(tag, {
            url: url,
            outcome: "rejected",
            error: String((error && error.name) || error),
            violations: violations.slice(seen),
          });
        });
      }
    );
  }

  function callCommand(tag, command, args) {
    return invoke(command, args || {}).then(
      function (value) {
        report(tag, { ok: true, value: value });
        return value;
      },
      function (error) {
        report(tag, { ok: false, error: String(error) });
        return null;
      }
    );
  }

  function waitForHealth(attempts) {
    var left = attempts;
    function attempt() {
      return invoke("local_agent_health", {}).then(
        function (body) {
          report("AgentHealth", { ok: true, attempt: attempts - left + 1, body: body });
          return true;
        },
        function (error) {
          left -= 1;
          if (left <= 0) {
            report("AgentHealth", {
              ok: false,
              attempt: attempts,
              error: String(error),
            });
            return false;
          }
          return new Promise(function (resolve) {
            setTimeout(resolve, 500);
          }).then(attempt);
        }
      );
    }
    return attempt();
  }

  function main() {
    report("Boot", {
      internals: !!invoke,
      href: window.location.href,
      origin: window.location.origin,
    });

    if (!invoke) {
      return;
    }

    return callCommand("PublicConfig", "get_public_config").then(function (config) {
      if (!config) {
        report("Done", { reason: "get_public_config failed" });
        return null;
      }

      // The Cloud origin first, then the same origin under its other name. The
      // order matters only for readability: each fetch reports its own delta.
      return tryFetch("CspFetchCloud", config.cloud_base_url + "/healthz")
        .then(function () {
          return tryFetch(
            "CspFetchLoopback",
            config.cloud_base_url.replace("127.0.0.1", "localhost") + "/healthz"
          );
        })
        .then(function () {
          return callCommand("AgentStart", "local_agent_start");
        })
        .then(function (label) {
          // No agent means nothing to ask: a launch whose spawn was refused must
          // report that fact, not ten seconds of connection errors.
          if (label === null) {
            report("Done", { violations: violations.length, agent: false });
            return null;
          }
          // A freshly spawned Agent needs a moment to bind; the product's Vue
          // layer polls the same command, at the same interval.
          return waitForHealth(20).then(function () {
            report("Done", { violations: violations.length, agent: true });
          });
        });
    });
  }

  window.addEventListener("error", function (event) {
    report("PageError", { message: String(event.message) });
  });

  main().catch(function (error) {
    report("ProbeFailed", { error: String(error) });
  });
})();
