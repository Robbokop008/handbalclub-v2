document.querySelectorAll('[data-admin-tabs]').forEach(function (wrap) {
  var btns = wrap.querySelectorAll('.admin-tab-btn');
  var panels = wrap.querySelectorAll('.admin-tab-panel');

  function activate(name) {
    btns.forEach(function (btn) { btn.classList.toggle('active', btn.dataset.tab === name); });
    panels.forEach(function (panel) { panel.hidden = panel.dataset.tabPanel !== name; });
  }

  btns.forEach(function (btn) {
    btn.addEventListener('click', function () { activate(btn.dataset.tab); });
  });

  activate(wrap.dataset.activeTab || (btns[0] && btns[0].dataset.tab));
});
