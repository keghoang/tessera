// Tessera Dashboard. The job's shots, who holds each one, what is in progress now, and the last change.
// Reads data/<name>.json (default: sample). Address: index.html#<name>/<shots|assets>
(async function () {
  const name = (location.hash || "#sample").slice(1).split("/")[0].replace(/[^A-Za-z0-9_-]/g, "") || "sample";
  const data = await fetch("data/" + name + ".json").then((r) => r.json());
  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  };
  const row = (...kids) => { const r = el("div", "r"); r.append(...kids); return r; };
  const end = (e) => { e.classList.add("end"); return e; };
  const ms = (d) => new Date(d.replace(" ", "T")).getTime();
  const now = ms(data.now);
  const ago = (d) => {
    const m = Math.max(0, Math.round((now - ms(d)) / 60000));
    if (m < 1) return "now";
    if (m < 60) return m + " min";
    if (m < 1440) return Math.round(m / 60) + " h";
    return Math.round(m / 1440) + " d";
  };
  const ver = (v) => "v" + String(v.version).padStart(3, "0");
  const store = (k, v) => { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { /* private window */ } return null; };

  const kinds = [...new Set(data.structure.map((g) => g.kind))];
  const kindOf = {};
  data.structure.forEach((g) => g.items.forEach((s) => { kindOf[s] = g.kind; }));
  // address: #<name>/<shots|assets>/<compact|standard|full>/<shot>:<task>  (the last two are optional)
  const parts = location.hash.split("/").map(decodeURIComponent);
  const fromHash = (parts[1] || "").toLowerCase();
  const MODES = ["compact", "standard", "full"];
  const state = {
    person: "all", q: "", sel: (parts[3] || "").replace(":", "/"),
    kind: kinds.find((k) => k.toLowerCase() === fromHash) || kinds[0],
    mode: MODES.includes(parts[2]) ? parts[2] : MODES.includes(store("tessera-mode")) ? store("tessera-mode") : "standard",
  };
  const address = () => history.replaceState(null, "", "#" + [name, state.kind.toLowerCase(), state.mode].concat(state.sel ? [state.sel.replace("/", ":")] : []).join("/"));
  const LABEL = { working: "working", waiting: "waiting", farm: "on the farm", idle: "idle" };

  // One colour per person, never repeated within a job. Eight hues spread over the part of the wheel
  // the states don't use (amber = waiting, teal = working, blue = on the farm); after eight people the
  // next eight take the hues in between at another lightness, and so on.
  const SLOT = [0, 4, 2, 6, 1, 5, 3, 7];
  const TIER = [[72, 62], [58, 78], [62, 45]];             // saturation, lightness
  const colourOf = (person) => {
    const i = data.people.indexOf(person);
    if (i < 0) return "";
    const round = Math.floor(i / 8);
    const at = ((SLOT[i % 8] + (round % 2) * 0.5) * 31.25 + round * 3.7) % 250;  // 250 degrees are free
    const hue = at < 95 ? 60 + at : (230 + (at - 95)) % 360;                      // 60-155, then 230-25
    const [s, l] = TIER[round % 3];
    return "hsl(" + hue.toFixed(1) + " " + s + "% " + l + "%)";
  };
  // Who. A person is a round pill with their name. An agent is an actor of its own: a squared,
  // outlined pill with a marker that reads "Kien's Claude", in its owner's colour.
  const short = (agent) => (agent === "Claude Code" ? "Claude" : agent);   // shown name only
  const actor = (person, agent) => {
    const s = el("span", "person" + (agent ? " agent" : ""));
    const c = colourOf(person);
    if (c) s.style.setProperty("--p", c);
    if (agent) s.append(el("i", "mark"), el("span", "", person + "'s " + short(agent)));
    else s.textContent = person;
    return s;
  };
  const agentOf = (v) => (v.made_by === "agent" ? v.agent || "agent" : "");
  const stateLabel = (l) => el("span", "st " + l.state, LABEL[l.state] || l.state);
  const since = (l) => ago(l.state === "working" ? l.since : l.updated);

  $("job").textContent = data.job;
  $("sample").hidden = !data.sample;
  $("collected").textContent = "read " + data.collected;

  // latest version and live session per shot/task
  const latest = {}, live = {};
  data.versions.forEach((v) => { latest[v.shot + "/" + v.task] = v; });
  data.live.forEach((s) => { live[s.shot + "/" + s.task] = s; });

  // ---- the panel: everything about one cell ----
  function drawPanel() {
    const p = $("panel");
    p.textContent = "";
    $("main").classList.toggle("open", !!state.sel);
    p.hidden = !state.sel;
    if (!state.sel) return;
    const [shot, task] = state.sel.split("/");
    const v = latest[state.sel], l = live[state.sel];
    const head = el("div", "phead");
    const x = el("button", "x", "Close");
    x.type = "button";
    x.addEventListener("click", () => { state.sel = ""; draw(); });
    head.append(el("h3", "", shot + " · " + task), x);
    p.append(head);
    const sec = (title, ...kids) => { const s = el("div", "sec"); s.append(el("h4", "", title), ...kids); p.append(s); };
    if (l) sec("Now", row(stateLabel(l), actor(l.person, l.agent), end(el("span", "t3", since(l)))), el("div", "t1", l.doing));
    if (v) {
      const kids = [row(el("span", "v", ver(v)), actor(v.artist, agentOf(v)), end(el("span", "t3", ago(v.date))))];
      if (v.request) kids.push(el("div", "t2 ask", v.request));
      if (v.changes.length) { const ul = el("ul", "chg"); v.changes.forEach((c) => ul.append(el("li", "", c))); kids.push(ul); }
      else kids.push(el("div", "t3", v.has_trail === false ? "No .trail next to this version" : "No change note"));
      sec("Latest version", ...kids);
      if ((v.history || []).length) {
        sec("Earlier", ...v.history.map((h) => row(el("span", "v", ver(h)), h.artist ? actor(h.artist, agentOf(h)) : el("span", "t3", "unknown"), end(el("span", "t3", ago(h.date))))));
      }
    }
  }

  // ---- the grid ----
  function draw() {
    const mine = (person) => state.person === "all" || person === state.person;
    document.body.dataset.mode = state.mode;
    address();

    const groups = $("groups");
    groups.textContent = "";
    data.structure.filter((g) => g.kind === state.kind).forEach((g) => {
      const items = g.items.filter((s) => !state.q || s.toLowerCase().includes(state.q))
        .filter((s) => state.person === "all" || g.tasks.some((t) => {
          const v = latest[s + "/" + t], l = live[s + "/" + t];
          return (v && v.artist === state.person) || (l && l.person === state.person);
        }));
      if (!items.length) return;
      const sec = el("section", "seq");
      const title = el("div", "seqhead");
      title.append(el("h2", "", g.name), el("span", "count", String(items.length)));
      const busy = items.reduce((n, s) => n + g.tasks.filter((t) => live[s + "/" + t] && live[s + "/" + t].state !== "idle").length, 0);
      if (busy) title.append(el("span", "chip agent", busy + " active"));
      sec.append(title);
      const wrap = el("div", "tablewrap");
      const table = el("table", "grid");
      const head = el("tr");
      head.append(el("th", "seqname", state.kind === "Assets" ? "Asset" : "Shot"));
      g.tasks.forEach((t) => head.append(el("th", "", t)));
      const thead = el("thead");
      thead.append(head);
      const body = el("tbody");
      items.forEach((shot) => {
        const tr = el("tr");
        const first = el("td", "shot");
        first.append(el("span", "mono strong", shot));
        tr.append(first);
        g.tasks.forEach((t) => {
          const key = shot + "/" + t;
          const v = latest[key], l = live[key];
          const on = l && l.state !== "idle";
          const td = el("td", "cell" + (on ? " live " + l.state : ""));
          if (!v && !l) { td.append(el("span", "none", "–")); tr.append(td); return; }
          if ((v && !mine(v.artist)) && !(l && mine(l.person))) td.classList.add("dim");
          if (key === state.sel) td.classList.add("sel");
          // line one: the version, who holds the cell now, then its live state or its age
          const who = l ? actor(l.person, l.agent) : actor(v.artist, agentOf(v));
          const right = l ? end(el("span", "st " + l.state, LABEL[l.state] + " · " + since(l))) : end(el("span", "t3", ago(v.date)));
          td.append(row(v ? el("span", "v", ver(v)) : el("span", "v none", "v–"), who, right));
          // line two, by display mode: the live task line (standard, full) or the last change (full)
          const more = l ? l.doing : v.changes[0];
          if (more) td.append(el("div", "more " + (l ? "t1 livetext" : "t2 note"), more));
          td.tabIndex = 0;
          td.setAttribute("role", "button");
          td.setAttribute("aria-label", shot + " " + t + ", details");
          const open = () => { state.sel = state.sel === key ? "" : key; draw(); };
          td.addEventListener("click", open);
          td.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
          tr.append(td);
        });
        body.append(tr);
      });
      table.append(thead, body);
      wrap.append(table);
      sec.append(wrap);
      groups.append(sec);
    });
    if (!groups.children.length) groups.append(el("p", "muted", "Nothing matches."));
    drawPanel();

    // last changes, newest first
    const chg = $("changes");
    chg.textContent = "";
    data.versions.filter((v) => kindOf[v.shot] === state.kind && mine(v.artist) && (!state.q || v.shot.toLowerCase().includes(state.q)))
      .sort((a, b) => (a.date < b.date ? 1 : -1)).slice(0, 8).forEach((v) => {
        const li = el("li", "change");
        const what = el("div", "what");
        const head = el("div", "head");
        head.append(el("span", "mono strong", v.file.replace(/\.[a-z]+$/, "")), actor(v.artist, agentOf(v)));
        what.append(head);
        if (v.changes.length) what.append(el("div", "muted", v.changes.join(" · ")));
        li.append(what, el("span", "when", ago(v.date)));
        chg.append(li);
      });

    // team: each person, then each of their agents as a row of its own
    const team = $("team");
    team.textContent = "";
    const byDate = (x, y) => (x.date < y.date ? 1 : -1);
    const trow = (cls, nameCell, chips, saves) => {
      const tr = el("tr", cls);
      const nm = el("td");
      nm.append(nameCell);
      const on = el("td", "chips");
      chips.forEach((c) => on.append(c));
      tr.append(nm, on, el("td", "num muted", saves.length ? ago(saves[0].date) : ""));
      team.append(tr);
    };
    data.people.forEach((p) => {
      const sel = p === state.person ? "sel" : "";
      const own = data.versions.filter((v) => v.artist === p && !agentOf(v)).sort(byDate);
      trow(sel, actor(p), own.length ? [el("span", "chip", own[0].shot + " " + own[0].task)] : [], own);
      const agents = [...new Set(data.versions.filter((v) => v.artist === p && agentOf(v)).map(agentOf)
        .concat(data.live.filter((s) => s.person === p).map((s) => s.agent)))].sort();
      agents.forEach((a) => {
        const running = data.live.filter((s) => s.person === p && s.agent === a);
        const saves = data.versions.filter((v) => v.artist === p && agentOf(v) === a).sort(byDate);
        const tone = { working: "agent", waiting: "warn", farm: "info", idle: "" };
        const chips = running.length
          ? running.map((s) => el("span", "chip " + tone[s.state], s.shot + " " + s.task + " · " + LABEL[s.state]))
          : saves.length ? [el("span", "chip", saves[0].shot + " " + saves[0].task)] : [];
        trow((sel + " sub").trim(), actor(p, a), chips, saves);
      });
    });
  }

  // ---- controls ----
  const seg = (host, options, current, pick) => {
    options.forEach(([value, label, swatch]) => {
      const b = el("button", "");
      b.type = "button";
      b.dataset.v = value;
      b.setAttribute("aria-pressed", String(value === current));
      if (swatch) { const sw = el("span", "person swatch"); sw.style.setProperty("--p", swatch); b.append(sw); }
      b.append(document.createTextNode(label));
      host.append(b);
    });
    host.addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      host.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      pick(b.dataset.v);
      draw();
    });
  };
  // tabs: one per kind in the job (Shots, Assets), with how many items each holds
  kinds.forEach((k) => {
    const b = el("button", "tab");
    b.type = "button";
    b.setAttribute("role", "tab");
    b.dataset.k = k;
    b.setAttribute("aria-selected", String(k === state.kind));
    const n = data.structure.filter((g) => g.kind === k).reduce((a, g) => a + g.items.length, 0);
    b.append(el("span", "", k), el("span", "count", String(n)));
    $("tabs").append(b);
  });
  $("tabs").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    state.kind = b.dataset.k;
    state.sel = "";
    $("tabs").querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", String(x === b)));
    draw();
  });
  // sessions now, whole job
  [["working", "agent"], ["waiting", "warn"], ["farm", "info"], ["idle", ""]].forEach(([s, tone]) => {
    const n = data.live.filter((l) => l.state === s).length;
    if (n) $("summary").append(el("span", "chip " + tone, n + " " + LABEL[s]));
  });
  seg($("f-person"), [["all", "Everyone"]].concat(data.people.map((p) => [p, p, colourOf(p)])), "all", (v) => { state.person = v; });
  seg($("f-mode"), [["compact", "Compact"], ["standard", "Standard"], ["full", "Full"]], state.mode, (v) => { state.mode = v; store("tessera-mode", v); });
  $("q").addEventListener("input", (e) => { state.q = e.target.value.trim().toLowerCase(); draw(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && state.sel) { state.sel = ""; draw(); } });
  draw();
})();
