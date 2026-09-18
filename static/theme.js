(() => {
  const addStylesheet = (path) => {
    if (!document.querySelector(`link[href="${path}"]`)) {
      const styles = document.createElement('link');
      styles.rel = 'stylesheet';
      styles.href = path;
      document.head.appendChild(styles);
    }
  };
  addStylesheet('/static/theme.css');
  addStylesheet('/static/fixes.css');
  addStylesheet('/static/layout-fixes.css');
  addStylesheet('/static/edit.css');
  addStylesheet('/static/alignment.css');
  const dateField = document.querySelector('input[name="occurred_on"]');
  if (dateField) dateField.max = new Date().toISOString().slice(0, 10);

  const shell = document.querySelector('.app-shell');
  if (shell) {
    const menuButton = document.createElement('button');
    menuButton.className = 'menu-toggle';
    menuButton.type = 'button';
    menuButton.textContent = 'Menu';
    menuButton.setAttribute('aria-label', 'Open navigation menu');
    document.body.appendChild(menuButton);
    menuButton.addEventListener('click', () => {
      const open = shell.classList.toggle('menu-open');
      menuButton.textContent = open ? 'Close' : 'Menu';
      menuButton.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    });
    shell.querySelectorAll('nav a').forEach((link) => link.addEventListener('click', () => shell.classList.remove('menu-open')));
  }

  document.querySelectorAll('nav a').forEach((link) => {
    if (link.textContent.trim() === 'Activity') link.href = '/activity';
    if (link.textContent.trim() === 'Planning') link.href = '/planning';
  });
  const key = 'lumen-theme';
  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll('.theme-toggle').forEach((button) => {
      const isDark = theme === 'dark';
      button.querySelector('.theme-icon').textContent = isDark ? 'Light' : 'Dark';
      button.querySelector('.theme-label').textContent = isDark ? 'Light mode' : 'Dark mode';
      button.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    });
  };
  applyTheme(localStorage.getItem(key) || 'light');
  document.querySelectorAll('.theme-toggle').forEach((button) => button.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(key, next);
    applyTheme(next);
  }));
})();
