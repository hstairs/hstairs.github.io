// Optional enhancement: the complete bibliography is present in the HTML.
document.querySelectorAll('[data-publication-search]').forEach(input => {
  const panel = input.closest('section') || document;
  const entries = [...panel.querySelectorAll('.publication-list > li')];
  const status = panel.querySelector('[data-result-count]');
  const update = () => {
    const terms = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    entries.forEach(entry => {
      entry.hidden = !terms.every(term => entry.textContent.toLocaleLowerCase().includes(term));
      if (!entry.hidden) count++;
    });
    status.textContent = `${count} of ${entries.length} entries`;
  };
  input.addEventListener('input', update);
  input.parentElement.hidden = false;
  update();
});
