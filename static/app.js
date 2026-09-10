const pages = document.querySelectorAll('.page');
const navItems = document.querySelectorAll('.nav-item');
const breadcrumb = document.getElementById('breadcrumbCurrent');
const sidebar = document.getElementById('sidebar');

function showPage(pageName) {
  const target = document.getElementById(pageName) || document.getElementById('overview');
  pages.forEach((page) => page.classList.toggle('active-page', page === target));
  navItems.forEach((item) => item.classList.toggle('active', item.dataset.page === target.id));
  breadcrumb.textContent = target.querySelector('h1')?.textContent.replace('✦', '').trim() || 'Overview';
  window.location.hash = target.id;
  sidebar.classList.remove('open');
}

document.querySelectorAll('[data-navigate]').forEach((button) => {
  button.addEventListener('click', () => showPage(button.dataset.navigate));
});
navItems.forEach((item) => item.addEventListener('click', (event) => {
  event.preventDefault();
  showPage(item.dataset.page);
}));
document.getElementById('menuButton').addEventListener('click', () => sidebar.classList.toggle('open'));

const chartDefaults = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { backgroundColor: '#253c34', padding: 10, cornerRadius: 6 } }, scales: { x: { grid: { display: false }, ticks: { color: '#9aa59f', font: { size: 10 } } }, y: { border: { display: false }, grid: { color: '#edf1ed' }, ticks: { color: '#a1aba6', font: { size: 10 }, stepSize: 20 } } } };
new Chart(document.getElementById('overviewChart'), { type: 'line', data: { labels: ['Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon'], datasets: [{ label: 'Fresh', data: [68, 72, 61, 79, 74, 86, 82], borderColor: '#39a56a', backgroundColor: 'rgba(57,165,106,.08)', fill: true, tension: .4, pointRadius: 0, borderWidth: 2 }, { label: 'Acceptable', data: [26, 20, 27, 15, 21, 10, 14], borderColor: '#e9a449', tension: .4, pointRadius: 0, borderWidth: 2 }, { label: 'Spoiled', data: [8, 8, 12, 6, 5, 4, 4], borderColor: '#db6b5d', tension: .4, pointRadius: 0, borderWidth: 2 }] }, options: chartDefaults });
new Chart(document.getElementById('distributionChart'), { type: 'doughnut', data: { labels: ['Fresh', 'Acceptable', 'Spoiled'], datasets: [{ data: [66.7, 24.3, 9], backgroundColor: ['#39a56a', '#e9a449', '#db6b5d'], borderWidth: 0, hoverOffset: 3 }] }, options: { responsive: true, maintainAspectRatio: false, cutout: '78%', plugins: { legend: { display: false }, tooltip: { backgroundColor: '#253c34', padding: 10, cornerRadius: 6 } } } });

const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
imageInput.addEventListener('change', () => {
  const file = imageInput.files[0];
  if (!file) return;
  imagePreview.src = URL.createObjectURL(file);
  imagePreview.style.display = 'block';
  document.querySelector('.upload-zone .upload-visual').style.display = 'none';
  document.querySelector('.upload-zone strong').textContent = file.name;
});

document.getElementById('analysisForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const button = event.target.querySelector('button');
  button.disabled = true;
  button.innerHTML = '<span>◌</span> Analyzing sample...';
  try {
    const response = await fetch('/api/analyze', { method: 'POST', body: form });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Analysis failed');
    renderResult(result);
  } catch (error) {
    document.getElementById('resultPreview').innerHTML = '<div class="empty-result"><h2>Analysis unavailable</h2><p>Check that the Flask server is running and try again.</p></div>';
  } finally {
    button.disabled = false;
    button.innerHTML = '<span>✦</span> Analyze sample';
  }
});

function renderResult(result) {
  const color = result.quality === 'Fresh' ? 'var(--green)' : result.quality === 'Acceptable' ? 'var(--orange)' : 'var(--red)';
  const facts = Object.entries(result.parameters).map(([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`).join('');
  const image = result.image_url ? `<img class="result-image" src="${result.image_url}" alt="Uploaded meat sample">` : '';
  document.getElementById('resultPreview').innerHTML = `<div class="result-card">${image}<div class="result-top"><span class="quality-label">PREDICTED QUALITY</span><span class="status ${result.quality.toLowerCase()}-status">${result.quality}</span></div><div class="quality-result" style="color:${color}">${result.score}% Freshness</div><div class="score-track"><i style="width:${result.score}%;background:${color}"></i></div><div class="result-facts">${facts}<div><span>ML confidence</span><strong>${result.confidence}%</strong></div><div><span>Analyzed at</span><strong>${result.analyzed_at}</strong></div></div><div class="recommendation"><strong>Recommendation</strong><br>${result.recommendation}</div></div>`;
}

document.querySelectorAll('.toggle').forEach((toggle) => toggle.addEventListener('click', () => toggle.classList.toggle('on')));
document.getElementById('generateReport').addEventListener('click', (event) => { event.target.textContent = '✓ Report ready'; setTimeout(() => { event.target.innerHTML = '＋ Generate report'; }, 2200); });
showPage(window.location.hash.replace('#', '') || 'overview');
