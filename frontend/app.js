const API_URL = (window.MONITORING_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_KEY = window.MONITORING_API_KEY || '';
const REFRESH_INTERVAL_MS = 60_000;
const $ = (selector) => document.querySelector(selector);
let activeAlerts = [];

async function fetchJson(path, options = {}) {
	const response = await fetch(`${API_URL}${path}`, {
		...options,
		headers: { 'X-API-Key': API_KEY, ...(options.headers || {}) },
	});
	if (!response.ok) throw new Error(String(response.status));
	return response.json();
}

function escapeHtml(value) {
	return String(value ?? '').replace(/[&<>"']/g, (character) => ({
		'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
	})[character]);
}

function formatTime(value) {
	if (!value) return '—';
	const date = new Date(value);
	return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
}

function formatValue(value) {
	if (value === null || value === undefined || value === '') return '—';
	const number = Number(value);
	return Number.isFinite(number) ? number.toLocaleString([], { maximumFractionDigits: 2 }) : escapeHtml(value);
}

function setServiceStatus(name, state, detail) {
	const status = $(`#${name}-status`);
	const indicator = $(`#${name}-indicator`);
	status.textContent = state;
	indicator.dataset.state = state.toLowerCase();
	$(`#${name}-detail`).textContent = detail;
}

function setOverallStatus(state, label) {
	$('#overall-status').dataset.state = state;
	$('#overall-status-text').textContent = label;
}

function updateAlertCounts(alerts) {
	$('#alert-count').textContent = alerts.length;
	$('#critical-count').textContent = alerts.filter((alert) => alert.severity === 'critical').length;
	$('#warning-count').textContent = alerts.filter((alert) => alert.severity === 'warning').length;
	$('#alert-total-badge').textContent = alerts.length;
}

function renderAlerts(alerts) {
	activeAlerts = Array.isArray(alerts) ? alerts : [];
	updateAlertCounts(activeAlerts);
	const severityFilter = $('#severity-filter').value;
	const visibleAlerts = severityFilter === 'all'
		? activeAlerts
		: activeAlerts.filter((alert) => alert.severity === severityFilter);
	const rows = $('#alerts');
	const emptyState = $('#empty-state');
	const table = $('#alerts-table-wrap');

	if (visibleAlerts.length === 0) {
		table.hidden = true;
		emptyState.hidden = false;
		emptyState.classList.add('is-clear');
		emptyState.classList.remove('is-error');
		emptyState.textContent = activeAlerts.length === 0
			? 'No active alerts — your alert inbox is clear.'
			: `No ${severityFilter} alerts match this filter.`;
		return;
	}

	emptyState.hidden = true;
	emptyState.classList.remove('is-clear', 'is-error');
	table.hidden = false;
	rows.innerHTML = visibleAlerts.map((alert) => {
		const severity = ['critical', 'warning', 'info'].includes(alert.severity) ? alert.severity : 'info';
		const targetName = alert.server_name || alert.instance_name || '—';
		const targetDetails = [alert.instance_name, alert.database_name].filter(Boolean).map(escapeHtml).join(' / ');
		const action = alert.status === 'open'
			? `<button class="button compact" type="button" data-alert-id="${escapeHtml(alert.alert_event_key)}">Acknowledge</button>`
			: '<span class="acknowledged">Acknowledged</span>';

		return `<tr>
			<td><span class="severity ${severity}">${severity}</span></td>
			<td><strong>${escapeHtml(alert.alert_name)}</strong><small>${escapeHtml(alert.message)}</small></td>
			<td><strong>${escapeHtml(targetName)}</strong><small>${targetDetails || 'SQL Server instance'}</small></td>
			<td>${escapeHtml(alert.metric_code || '—')}</td>
			<td><strong>${formatValue(alert.current_value)}</strong><small>Limit: ${formatValue(alert.threshold_value)}</small></td>
			<td><strong>${formatTime(alert.last_seen_at)}</strong><small>${Number(alert.occurrence_count) || 0} occurrence${Number(alert.occurrence_count) === 1 ? '' : 's'}</small></td>
			<td>${action}</td>
		</tr>`;
	}).join('');

	rows.querySelectorAll('[data-alert-id]').forEach((button) => {
		button.addEventListener('click', () => acknowledgeAlert(button));
	});
}

async function acknowledgeAlert(button) {
	button.disabled = true;
	button.textContent = 'Saving…';
	try {
		const response = await fetch(`${API_URL}/api/v1/alerts/${encodeURIComponent(button.dataset.alertId)}/acknowledge`, {
			method: 'POST',
			headers: { 'X-API-Key': API_KEY },
		});
		if (!response.ok) throw new Error(String(response.status));
		await refresh();
	} catch (error) {
		button.disabled = false;
		button.textContent = 'Retry';
		button.title = error.message === '403' ? 'The configured API key was rejected.' : 'Could not acknowledge this alert.';
	}
}

async function refresh() {
	const refreshButton = $('#refresh');
	refreshButton.disabled = true;
	refreshButton.setAttribute('aria-busy', 'true');
	setOverallStatus('checking', 'Checking services');

	const [healthResult, alertsResult] = await Promise.allSettled([
		fetchJson('/readyz'),
		fetchJson('/api/v1/alerts/active'),
	]);
	const apiOnline = healthResult.status === 'fulfilled';
	const databaseOnline = apiOnline && healthResult.value.database === 'UP';
	const alertsOnline = alertsResult.status === 'fulfilled';

	setServiceStatus('api', apiOnline ? 'Online' : 'Offline', apiOnline ? 'Health endpoint responding' : 'Could not reach the API');
	setServiceStatus(
		'database',
		!apiOnline ? 'Unknown' : databaseOnline ? 'Online' : 'Degraded',
		!apiOnline ? 'Waiting for API health' : databaseOnline ? 'PostgreSQL connection healthy' : 'PostgreSQL is not ready',
	);

	if (alertsOnline) {
		renderAlerts(alertsResult.value);
	} else {
		$('#alert-count').textContent = '—';
		$('#critical-count').textContent = '—';
		$('#warning-count').textContent = '—';
		$('#alert-total-badge').textContent = '—';
		$('#alerts-table-wrap').hidden = true;
		$('#empty-state').hidden = false;
		$('#empty-state').classList.remove('is-clear');
		$('#empty-state').classList.add('is-error');
		$('#empty-state').textContent = alertsResult.reason.message === '403'
			? 'The frontend API key was rejected. Check the frontend API configuration.'
			: 'Alert data is temporarily unavailable. Try refreshing in a moment.';
	}

	const overallState = !apiOnline ? 'offline' : (!databaseOnline || !alertsOnline ? 'degraded' : 'online');
	const overallLabel = overallState === 'online' ? 'All systems operational' : overallState === 'degraded' ? 'Service degraded' : 'API unavailable';
	setOverallStatus(overallState, overallLabel);
	$('#last-updated').textContent = `Today, ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
	refreshButton.disabled = false;
	refreshButton.removeAttribute('aria-busy');
}

$('#refresh').addEventListener('click', refresh);
$('#severity-filter').addEventListener('change', () => renderAlerts(activeAlerts));
refresh();
window.setInterval(refresh, REFRESH_INTERVAL_MS);
