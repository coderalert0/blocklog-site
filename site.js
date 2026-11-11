// The support address is written here, not in the pages, so it isn't sitting in the source for scrapers. Every page reads
// fine without it.
(function () {
  var user = 'laddothis', domain = 'gmail.com';
  var mailto = 'ma' + 'ilto:' + user + '@' + domain + '?subject=Blocklog';
  document.querySelectorAll('.email').forEach(function (el) {
    var a = document.createElement('a');
    a.href = mailto;
    a.textContent = user + '@' + domain;
    el.replaceChildren(a);
  });
  document.querySelectorAll('a.mail').forEach(function (a) { a.href = mailto; });
})();
