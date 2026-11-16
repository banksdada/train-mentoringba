/* "Ask the Lab" help box */
(function () {
  var EMAIL = "coach@mentoringba.org";
  var WHATSAPP = "https://wa.me/447723439379";
  var BOOKING = "https://tidycal.com/mentoringba/15-minutes-with-us";
  var NAME_KEY = "ba-lab-student-name-v1";

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k) || ""; localStorage.setItem(k, v); } catch (e) { return ""; } }

  var fab = document.createElement("button");
  fab.className = "ask-fab"; fab.type = "button";
  fab.setAttribute("aria-haspopup", "dialog"); fab.textContent = "Ask the Lab";

  var panel = document.createElement("section");
  panel.className = "ask-panel"; panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-labelledby", "ask-title");
  panel.innerHTML =
    '<div class="ask-head"><h2 id="ask-title">Ask the Lab</h2>' +
    '<button type="button" class="ask-close" aria-label="Close help box">&times;</button></div>' +
    '<form class="ask-body" novalidate>' +
    '<p class="ask-note">Ask about setup, what a prompt means, or whether your output looks right. I answer from this course only.</p>' +
    '<div class="ask-namebox"><label for="ask-name">Your name</label><input id="ask-name" autocomplete="given-name" maxlength="60"></div>' +
    '<div><label for="ask-q">Your question</label><textarea id="ask-q" maxlength="600"></textarea></div>' +
    '<button class="ask-send" type="submit">Ask</button>' +
    '<div class="ask-answer" role="status" aria-live="polite"></div>' +
    '<p class="ask-note">Your name and question are saved so your trainer can follow up and improve the course, and are processed by OpenAI to write the answer. Please don\'t include personal or sensitive details.</p>' +
    '</form>' +
    '<div class="ask-contact"><p>Need a person?</p><div>' +
    '<a href="mailto:' + EMAIL + '">Email</a>' +
    '<a href="' + WHATSAPP + '" target="_blank" rel="noopener">WhatsApp</a>' +
    '<a href="' + BOOKING + '" target="_blank" rel="noopener">Book 15 minutes</a></div></div>';

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  var form = panel.querySelector("form"), nameIn = panel.querySelector("#ask-name"),
      nameBox = panel.querySelector(".ask-namebox"), q = panel.querySelector("#ask-q"),
      send = panel.querySelector(".ask-send"), out = panel.querySelector(".ask-answer");

  function open() {
    panel.classList.add("open"); fab.style.display = "none";
    var saved = store(NAME_KEY);
    if (saved) { nameIn.value = saved; nameBox.style.display = "none"; q.focus(); } else { nameIn.focus(); }
  }
  function close() { panel.classList.remove("open"); fab.style.display = ""; fab.focus(); }

  fab.addEventListener("click", open);
  panel.querySelector(".ask-close").addEventListener("click", close);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("open")) close(); });

  function show(text, isErr) { out.textContent = text; out.className = "ask-answer show" + (isErr ? " err" : ""); }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = nameIn.value.trim(), question = q.value.trim();
    if (!name) { show("Please enter your name first.", true); nameBox.style.display = ""; nameIn.focus(); return; }
    if (!question) { show("Please type a question.", true); q.focus(); return; }
    store(NAME_KEY, name);
    send.disabled = true; send.textContent = "Thinking…"; show("One moment…");
    fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, question: question }) })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (res.ok) { show(res.d.answer, !res.d.answered); if (res.d.answered) q.value = ""; }
        else { show(typeof res.d.detail === "string" ? res.d.detail : "Please check your name and question and try again.", true); }
      })
      .catch(function () { show("Couldn't reach the help box. Please contact your trainer using the options below.", true); })
      .then(function () { send.disabled = false; send.textContent = "Ask"; });
  });
})();
