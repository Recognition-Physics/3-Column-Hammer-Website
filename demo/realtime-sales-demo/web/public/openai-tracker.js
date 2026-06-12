/**
 * OpenAI Ads conversion tracker (browser side).
 *
 * Sends two kinds of events to our own backend at POST /api/track, which
 * forwards them server-side to the OpenAI Ads Conversions API:
 *   1. "page_view"       - when the page loads
 *   2. "form_submission" - when any <form> is submitted (lead + call-me modals)
 *
 * No secrets here: the Conversions API key lives only on the server.
 * To exclude a form from tracking, add the data-no-track attribute to it.
 */
(function () {
  var ENDPOINT = "/api/track";

  function send(payload) {
    payload.source_url = window.location.href;
    var body = JSON.stringify(payload);
    // sendBeacon survives page navigation (important for form submits)
    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "application/json" }));
    } else {
      fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
        keepalive: true,
      }).catch(function () {});
    }
  }

  // 1. Page view
  send({ event: "page_view" });

  // 2. Form submissions (capture phase, so dynamically-added modal forms
  //    are caught even when their handlers call preventDefault)
  document.addEventListener(
    "submit",
    function (e) {
      var form = e.target;
      if (!form || !form.tagName || form.tagName !== "FORM") return;
      if (form.hasAttribute("data-no-track")) return;

      var email = "";
      var emailInput =
        form.querySelector('input[type="email"]') ||
        form.querySelector('input[name*="email" i]');
      if (emailInput && emailInput.value) email = emailInput.value;

      send({
        event: "form_submission",
        form_id: form.id || form.getAttribute("name") || "unnamed_form",
        email: email,
      });
    },
    true
  );
})();
