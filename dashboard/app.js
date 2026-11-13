// Tessera Dashboard. The job's shots, who is on each, what is in progress now, and the last change.
// Reads data/<name>.json (default: sample).
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
  const kinds = [...new Set(data.structure.map((g) => g.kind))];
  const kindOf = {};
  data.structure.forEach((g) => g.items.forEach((s) => { kindOf[s] = g.kind; }));
  const fromHash = (location.hash.split("/")[1] || "").toLowerCase();
  const state = { person: "all", q: "", kind: kinds.find((k) => k.toLowerCase() === fromHash) || kinds[0] };
  const TONE = { working: "agent", waiting: "warn", farm: "info", idle: "" };
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
  const pill = (person) => {
    const s = el("span", "person", person);
    const c = colourOf(person);
    if (c) s.style.setProperty("--p", c);
    return s;
  };
  // Who did it. A person is a round pill with their name. An agent is its own actor: a squared pill
  // with a marker, the agent's name, then whose agent it is, in that person's colour.
  const actor = (person, agent) => {
    if (!agent) return pill(person);
    const s = el("span", "person agent");
    const c = colourOf(person);
    if (c) s.style.setProperty("--p", c);
    s.append(el("i", "mark"), el("span", "", agent), el("span", "owner", person));
    s.title = person + "'s agent: " + agent;
    return s;
  };
  const agentOf = (v) => (v.made_by === "agent" ? v.agent || "agent" : "");

  $("job").textContent = data.job;
  $("sample").hidden = !data.sample;
  $("collected").textContent = "read " + data.collected;

  // latest version and live session per shot/task
  const latest = {}, live = {};
  data.versions.forEach((v) => { latest[v.shot + "/" + v.task] = v; });
  data.live.forEach((s) => { live[s.shot + "/" + s.task] = s; });

  function draw() {
    const mine = (person) => state.person === "all" || person === state.person;

    // the job's structure: one block per sequence or asset category, every shot listed
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
          const v = latest[shot + "/" + t], l = live[shot + "/" + t];
          const td = el("td", "cell" + (l && l.state !== "idle" ? " live " + (TONE[l.state] || "agent") : ""));
          if (!v && !l) { td.append(el("span", "none", "–")); tr.append(td); return; }
          const dim = (v && !mine(v.artist)) && !(l && mine(l.person));
          if (dim) td.classList.add("dim");
          if (v) {
            const l1 = el("div", "l1");
            l1.append(el("span", "mono ver", ver(v)), actor(v.artist, agentOf(v)), el("span", "age", ago(v.date)));
            td.append(l1);
          }
          if (l) {
            const now1 = el("div", "l2 now");
            const chip = { waiting: ["warn", "waiting on " + l.person], farm: ["info", "on the farm"], idle: ["", "idle"] }[l.state] || ["agent", "working"];
            now1.append(el("span", "chip " + chip[0], chip[1]), actor(l.person, l.agent), el("span", "muted", ago(l.state === "working" ? l.since : l.updated)));
            td.append(now1, el("div", "l2 doing-line", l.doing));
          } else if (v.changes[0]) {
            td.append(el("div", "l2 muted", v.changes[0]));
          }
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
    const row = (cls, nameCell, chips, saves) => {
      const tr = el("tr", cls);
      const name = el("td");
      name.append(nameCell);
      const on = el("td", "chips");
      chips.forEach((c) => on.append(c));
      tr.append(name, on, el("td", "num muted", saves.length ? ago(saves[0].date) : ""));
      team.append(tr);
    };
    data.people.forEach((p) => {
      const sel = p === state.person ? "sel" : "";
      const own = data.versions.filter((v) => v.artist === p && !agentOf(v)).sort(byDate);
      row(sel, pill(p), own.length ? [el("span", "chip", own[0].shot + " " + own[0].task)] : [], own);
      const agents = [...new Set(data.versions.filter((v) => v.artist === p && agentOf(v)).map(agentOf)
        .concat(data.live.filter((s) => s.person === p).map((s) => s.agent)))].sort();
      agents.forEach((a) => {
        const running = data.live.filter((s) => s.person === p && s.agent === a);
        const saves = data.versions.filter((v) => v.artist === p && agentOf(v) === a).sort(byDate);
        const chips = running.length
          ? running.map((s) => el("span", "chip " + (TONE[s.state] ?? "agent"), s.shot + " " + s.task + " · " + (s.state === "farm" ? "on the farm" : s.state)))
          : saves.length ? [el("span", "chip", saves[0].shot + " " + saves[0].task)] : [];
        row((sel + " sub").trim(), actor(p, a), chips, saves);
      });
    });
  }

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
    $("tabs").querySelectorAll("button").forEach((x) => x.setAttribute("aria-selected", String(x === b)));
    history.replaceState(null, "", "#" + name + "/" + state.kind.toLowerCase());
    draw();
  });
  // sessions now, whole job
  [["working", "working"], ["waiting", "waiting"], ["farm", "on the farm"], ["idle", "idle"]].forEach(([s, label]) => {
    const n = data.live.filter((l) => l.state === s).length;
    if (n) $("summary").append(el("span", "chip " + TONE[s], n + " " + label));
  });

  ["all"].concat(data.people).forEach((p, i) => {
    const b = el("button", "", p === "all" ? "Everyone" : "");
    if (p !== "all") { const sw = pill(""); sw.classList.add("swatch"); sw.style.setProperty("--p", colourOf(p)); b.append(sw, document.createTextNode(p)); }
    b.type = "button";
    b.dataset.v = p;
    b.setAttribute("aria-pressed", String(i === 0));
    $("f-person").append(b);
  });
  $("f-person").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    $("f-person").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    state.person = b.dataset.v;
    draw();
  });
  $("q").addEventListener("input", (e) => { state.q = e.target.value.trim().toLowerCase(); draw(); });
  draw();
})();
