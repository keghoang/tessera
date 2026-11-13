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
  const who = (person, agent) => {
    const s = el("span", "who");
    s.append(el("i", "dot" + (agent ? " agent" : "")), el("span", "", person));
    if (agent) s.append(el("span", "muted", "via " + agent));
    return s;
  };

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
            l1.append(el("i", "dot" + (v.made_by === "agent" ? " agent" : "")), el("span", "mono ver", ver(v)), el("span", "by", v.artist), el("span", "age", ago(v.date)));
            td.append(l1);
          }
          if (l) {
            const now1 = el("div", "l2 now");
            const chip = { waiting: ["warn", "waiting on " + l.person], farm: ["info", "on the farm · " + ago(l.updated)],
              idle: ["", "idle · " + ago(l.updated)] }[l.state] || ["agent", l.agent + " · " + ago(l.since)];
            now1.append(el("span", "chip " + chip[0], chip[1]), document.createTextNode(" " + l.doing));
            td.append(now1);
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
        head.append(el("span", "mono strong", v.file.replace(/\.[a-z]+$/, "")), who(v.artist, v.made_by === "agent" ? v.agent : ""));
        what.append(head);
        if (v.changes.length) what.append(el("div", "muted", v.changes.join(" · ")));
        li.append(what, el("span", "when", ago(v.date)));
        chg.append(li);
      });

    // team: what each person has running and when they last saved
    const team = $("team");
    team.textContent = "";
    data.people.forEach((p) => {
      const running = data.live.filter((s) => s.person === p);
      const saves = data.versions.filter((v) => v.artist === p).sort((a, b) => (a.date < b.date ? 1 : -1));
      const tr = el("tr", p === state.person ? "sel" : "");
      const on = el("td", "chips");
      if (running.length) running.forEach((s) => on.append(el("span", "chip " + (TONE[s.state] ?? "agent"), s.shot + " " + s.task + (s.state === "working" ? "" : " · " + s.state))));
      else if (saves.length) on.append(el("span", "chip", saves[0].shot + " " + saves[0].task));
      tr.append(el("td", "", p), on, el("td", "num muted", saves.length ? ago(saves[0].date) : ""));
      team.append(tr);
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
    const b = el("button", "", p === "all" ? "Everyone" : p);
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
