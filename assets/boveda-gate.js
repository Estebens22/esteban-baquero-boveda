/* Captura de comunidad de la Bóveda — híbrido localStorage + cookie + DB.
   Si ya está inscrito: saluda ("Hola X, chévere que volviste") y deja descargar.
   Si no: popup con nombre+correo (WhatsApp opcional) -> registra -> descarga o envío por correo. */
(function () {
  var API = "/api", KEY = "eb_lead";

  function getLead() { try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; } }
  function setLead(o) {
    try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {}
    document.cookie = "eb_lead=" + encodeURIComponent(o.email) + ";path=/;max-age=31536000;samesite=lax";
  }
  function recurso() {
    var h = document.querySelector("h1");
    return (h ? h.textContent : document.title).replace(/\.$/, "").trim();
  }
  function dl(href) { var a = document.createElement("a"); a.href = href; a.setAttribute("download", ""); document.body.appendChild(a); a.click(); a.remove(); }
  function toast(msg) {
    var t = document.getElementById("ebg-toast");
    if (!t) { t = document.createElement("div"); t.id = "ebg-toast"; document.body.appendChild(t); }
    t.innerHTML = msg; requestAnimationFrame(function () { t.classList.add("on"); });
    setTimeout(function () { t.classList.remove("on"); }, 4000);
  }

  function closeModal() { var o = document.getElementById("ebg-ov"); if (o) { o.classList.remove("on"); setTimeout(function () { o.remove(); }, 250); } }
  function openModal(href, mode) {
    var r = recurso();
    var ov = document.createElement("div"); ov.id = "ebg-ov";
    ov.innerHTML =
      '<div id="ebg-card" role="dialog" aria-modal="true" aria-label="Acceso a la Bóveda">' +
      '<div class="ebg-h"><button class="ebg-x" aria-label="Cerrar">&times;</button>' +
      '<span class="m">eb</span><h3>Llevate este recurso</h3><p>' + r + '</p></div><div class="ebg-bar"></div>' +
      '<div class="ebg-b">' +
      '<label>Nombre<input id="ebg-n" type="text" autocomplete="name" placeholder="¿Cómo te llamas?"></label>' +
      '<label>Correo<input id="ebg-e" type="email" autocomplete="email" placeholder="nombre@correo.com"></label>' +
      '<label>WhatsApp <span style="color:#8a909a;font-weight:400">(opcional, para la comunidad)</span><input id="ebg-w" type="text" autocomplete="tel" placeholder="+57…"></label>' +
      '<input id="ebg-hp" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0">' +
      '<label class="ebg-chk"><input id="ebg-o" type="checkbox"> Quiero recibir nuevos recursos y contenido de la Bóveda.</label>' +
      '<div class="ebg-err" id="ebg-err"></div>' +
      '<div class="ebg-row"><button id="ebg-go">Descargar</button><button id="ebg-mail">Enviármelo por correo</button></div>' +
      '<p style="font-size:12px;color:#8a909a;margin:12px 0 0">Tus datos solo se usan para darte acceso y, si aceptás, avisarte de nuevos recursos.</p>' +
      '</div></div>';
    document.body.appendChild(ov);
    requestAnimationFrame(function () { ov.classList.add("on"); });
    var n = ov.querySelector("#ebg-n"), e = ov.querySelector("#ebg-e"), w = ov.querySelector("#ebg-w"),
      o = ov.querySelector("#ebg-o"), hp = ov.querySelector("#ebg-hp"), err = ov.querySelector("#ebg-err");
    n.focus();
    ov.querySelector(".ebg-x").onclick = closeModal;
    ov.addEventListener("click", function (ev) { if (ev.target === ov) closeModal(); });
    document.addEventListener("keydown", function esc(ev) { if (ev.key === "Escape") { closeModal(); document.removeEventListener("keydown", esc); } });

    function submit(byMail) {
      var name = n.value.trim(), email = e.value.trim();
      if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = "Poné tu nombre y un correo válido."; return; }
      var payload = { name: name, email: email, whatsapp: w.value.trim(), optin: o.checked, hp: hp.value, resource: r, url: href };
      ov.querySelector("#ebg-go").disabled = true; ov.querySelector("#ebg-mail").disabled = true;
      fetch(API + "/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
        .then(function (res) { return res.json(); })
        .then(function (d) {
          if (!d.ok) { err.textContent = d.error === "demasiado rápido" ? "Esperá unos segundos y reintentá." : "Algo falló, reintentá."; ov.querySelector("#ebg-go").disabled = false; ov.querySelector("#ebg-mail").disabled = false; return; }
          setLead({ email: email, nombre: name });
          closeModal();
          if (byMail) { toast("📩 Te lo mandé al correo, <b>" + name + "</b>."); }
          else { toast("¡Listo, <b>" + name + "</b>! Descargando… 🚀"); dl(href); }
        })
        .catch(function () { err.textContent = "Sin conexión, reintentá."; ov.querySelector("#ebg-go").disabled = false; ov.querySelector("#ebg-mail").disabled = false; });
    }
    ov.querySelector("#ebg-go").onclick = function () { submit(false); };
    ov.querySelector("#ebg-mail").onclick = function () { submit(true); };
  }

  // Interceptar descargas de kits
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest('a[download], a[href$=".zip"]');
    if (!a) return;
    var lead = getLead();
    if (lead && lead.email) {
      // ya inscrito: registra el recurso (silencioso), saluda y deja bajar
      fetch(API + "/lead", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: lead.nombre || "Amigo", email: lead.email, resource: recurso(), url: location.href }), keepalive: true }).catch(function () {});
      toast("¡Hola <b>" + (lead.nombre || "") + "</b>, chévere que volviste! 👋 Descargando…");
      return; // no preventDefault: deja el download normal
    }
    ev.preventDefault();
    openModal(a.href);
  }, true);

  // Al cargar: si hay email local, confirmá con la DB (fuente de verdad) y actualizá el nombre
  var l = getLead();
  if (l && l.email) {
    fetch(API + "/lead/check?email=" + encodeURIComponent(l.email))
      .then(function (r) { return r.json(); })
      .then(function (d) { if (d && d.enrolled && d.nombre) { l.nombre = d.nombre; setLead(l); } })
      .catch(function () {});
  }
})();
