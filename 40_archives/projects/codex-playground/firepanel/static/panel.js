const panel = document.querySelector('.panel');
if (panel) {
  const csrf = panel.dataset.csrf;
  const feedback = document.getElementById('feedback');
  const fullscreenButton = document.getElementById('fullscreen-button');
  const refreshButton = document.getElementById('refresh-button');
  const updatedAt = document.getElementById('updated-at');
  const pcConnection = document.getElementById('pc-connection');
  const todoistList = document.getElementById('todoist-list');
  const todoistHeading = document.getElementById('todoist-heading');
  const todoistCount = document.getElementById('todoist-count');
  const todoistUpdated = document.getElementById('todoist-updated');
  let lastDetailsUpdate = '';

  function updateClock() {
    const now = new Date();
    document.getElementById('today').textContent = now.toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric', weekday: 'short' });
    document.getElementById('clock').textContent = now.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
  }

  function setMeter(key, percent) {
    const amount = Number.isFinite(Number(percent)) ? Math.max(0, Math.min(100, Number(percent))) : 0;
    document.getElementById(`${key}-bar`).style.width = `${amount}%`;
    document.getElementById(`${key}-meter`).setAttribute('aria-valuenow', String(Math.round(amount)));
  }

  function setDrive(letter, usage) {
    const key = letter.toLowerCase();
    const value = document.getElementById(`${key}-value`);
    if (!usage || !usage.total) {
      value.textContent = '未接続';
      document.getElementById(`${key}-percent`).textContent = '--%';
      setMeter(key, 0);
      return;
    }
    value.textContent = `${Math.round(usage.used / 1e9)} / ${Math.round(usage.total / 1e9)} GB`;
    document.getElementById(`${key}-percent`).textContent = `${Math.round(usage.percent)}%`;
    setMeter(key, usage.percent);
  }

  function updateFullscreenButton() {
    const active = Boolean(document.fullscreenElement);
    panel.classList.toggle('is-fullscreen', active);
    fullscreenButton.querySelector('.app-label').textContent = active ? '全画面を終了' : '全画面';
    fullscreenButton.setAttribute('aria-pressed', String(active));
  }

  fullscreenButton.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        if (!document.documentElement.requestFullscreen) {
          throw new Error('fullscreen unavailable');
        }
        await document.documentElement.requestFullscreen();
      }
      feedback.textContent = '';
    } catch {
      fullscreenButton.querySelector('.app-label').textContent = '全画面に失敗';
      feedback.textContent = '全画面表示に切り替えられませんでした。';
    }
  });
  document.addEventListener('fullscreenchange', updateFullscreenButton);
  updateFullscreenButton();

  async function refreshStatus(details = false) {
    const started = performance.now();
    try {
      const response = await fetch(details ? '/api/status?details=1' : '/api/status', { cache: 'no-store' });
      if (response.status === 401) {
        window.location.href = '/login';
        return;
      }
      if (!response.ok) throw new Error('status unavailable');
      const data = await response.json();
      for (const [key, value] of [['cpu', data.cpu], ['memory', data.memory]]) {
        const percent = Math.max(0, Math.min(100, Number(value)));
        document.getElementById(`${key}-value`).textContent = `${percent}%`;
        setMeter(key, percent);
      }
      if (details) {
        document.getElementById('latency-value').textContent = `${Math.max(1, Math.round(performance.now() - started))} ms`;
        setDrive('C', data.drives && data.drives.C);
        setDrive('E', data.drives && data.drives.E);
        const updated = new Date();
        const date = updated.toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' });
        const time = updated.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
        lastDetailsUpdate = `容量・応答の最終更新 ${date} ${time}`;
      }
      updatedAt.textContent = lastDetailsUpdate || 'PCに接続中';
      pcConnection.textContent = '接続中';
    } catch {
      updatedAt.textContent = 'PC情報を取得できません';
      pcConnection.textContent = '未接続';
      if (details) feedback.textContent = 'PC情報を更新できませんでした。';
    }
  }

  function showTodoistMessage(message) {
    todoistList.replaceChildren();
    const item = document.createElement('li');
    item.className = 'todoist-message';
    item.textContent = message;
    todoistList.append(item);
  }

  async function refreshTodoist(manual = false) {
    try {
      const response = await fetch(manual ? '/api/todoist?refresh=1' : '/api/todoist', { cache: 'no-store' });
      if (response.status === 401) {
        window.location.href = '/login';
        return;
      }
      if (!response.ok) throw new Error('Todoist unavailable');
      const data = await response.json();
      todoistHeading.textContent = data.scope === 'upcoming' ? '次のTodoist' : '今日のTodoist';
      todoistCount.textContent = data.tasks.length
        ? (data.scope === 'upcoming' ? `${data.tasks.length}件` : `残り ${data.tasks.length}件`)
        : '';
      if (data.state === 'unconfigured') {
        showTodoistMessage('設定画面でカレンダーURLを登録してください。');
      } else if (data.state === 'error') {
        showTodoistMessage('Todoistを取得できませんでした。');
      } else if (!data.tasks.length) {
        showTodoistMessage('表示するタスクはありません。');
      } else {
        todoistList.replaceChildren();
        for (const task of data.tasks.slice(0, 5)) {
          const item = document.createElement('li');
          item.className = 'todoist-item';
          const when = document.createElement('span');
          when.className = 'todoist-when';
          when.textContent = task.when;
          const title = document.createElement('span');
          title.className = 'todoist-title';
          title.textContent = task.title;
          item.append(when, title);
          todoistList.append(item);
        }
      }
      todoistUpdated.textContent = data.updated_at
        ? `${data.state === 'stale' ? '取得失敗・前回の情報' : 'Todoist更新'} ${new Date(data.updated_at).toLocaleString('ja-JP', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })}`
        : '';
    } catch {
      todoistUpdated.textContent = 'Todoistに接続できません';
    }
  }

  async function pollTodoist() {
    await refreshTodoist();
    window.setTimeout(pollTodoist, 300000);
  }

  async function pollStatus() {
    await refreshStatus();
    window.setTimeout(pollStatus, 2500);
  }

  refreshButton.addEventListener('click', async () => {
    refreshButton.disabled = true;
    feedback.textContent = '';
    await refreshStatus(true);
    await refreshTodoist(true);
    refreshButton.disabled = false;
  });

  for (const button of document.querySelectorAll('.app-button[data-slot]:not(:disabled)')) {
    button.addEventListener('click', async () => {
      button.disabled = true;
      feedback.textContent = '起動しています…';
      try {
        const response = await fetch(`/api/launch/${button.dataset.slot}`, {
          method: 'POST',
          headers: { 'X-FirePanel-CSRF': csrf },
        });
        if (response.status === 401) {
          window.location.href = '/login';
          return;
        }
        const result = await response.json();
        feedback.textContent = result.message || result.error || '操作できませんでした。';
      } catch {
        feedback.textContent = 'PCに接続できませんでした。';
      } finally {
        button.disabled = false;
      }
    });
  }

  updateClock();
  window.setInterval(updateClock, 30000);
  refreshStatus(true).then(() => window.setTimeout(pollStatus, 2500));
  pollTodoist();
}
