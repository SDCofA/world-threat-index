const WTI = {
  data: window.WTI_DATA || null,

  getIndex(obj) {
    const v = Number(obj?.index ?? obj?.main_index);
    return Number.isFinite(v) ? v : 0;
  },

  statusClass(status) {
    const s = (status || 'STABLE').toUpperCase();
    if (s.includes('CRITICAL')) return 'critical';
    if (s.includes('ELEVATED')) return 'elevated';
    return 'stable';
  },

  colorForIndex(index) {
    if (index > 7) return '#cf5b4e';
    if (index > 4) return '#d8a13f';
    return '#6fae7e';
  },

  escapeHtml(v) {
    return String(v ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  formatDateTime(value) {
    const date = value ? new Date(value) : null;
    return date && !Number.isNaN(date.getTime()) ? date.toLocaleString() : '--';
  },

  renderEarlyWarning() {
    const warning = this.data?.early_warning;
    const componentsEl = document.getElementById('early-warning-components');
    if (!warning || !componentsEl) return;
    const score = Number(warning.score);
    document.getElementById('early-warning-score').textContent = Number.isFinite(score) ? score.toFixed(1) : '--';
    document.getElementById('early-warning-level').textContent = warning.level || '--';
    document.getElementById('early-warning-confidence').textContent = warning.confidence
      ? `${warning.confidence} · ${Number(warning.confidence_score || 0).toFixed(0)}% coverage`
      : '--';
    document.getElementById('early-warning-horizon').textContent = warning.horizon || '0–7 days';
    document.getElementById('early-warning-issued').textContent = this.formatDateTime(warning.issued_at);

    const detail = component => {
      if (component.id === 'narrative_pressure') {
        return `${Number(component.precursor_event_count) || 0} precursor events · ${Number(component.independent_sources) || 0} domains`;
      }
      if (component.id === 'cross_market_dislocation') {
        const indicators = (component.indicators || []).filter(item => item.available);
        return indicators.length
          ? indicators.map(item => `${item.label}: z ${Number(item.anomaly_z).toFixed(1)}`).join(' · ')
          : 'Market series unavailable';
      }
      return `${Number(component.rising_entities) || 0}/${Number(component.entities_compared) || 0} entities rising`;
    };

    componentsEl.innerHTML = (warning.components || []).map(component => `
      <article class="early-warning-component ${component.available ? '' : 'unavailable'}">
        <div><span>${this.escapeHtml(component.label)}</span><strong>${Number(component.score || 0).toFixed(1)}</strong></div>
        <div class="early-warning-bar"><i style="width:${Math.max(0, Math.min(100, Number(component.score) || 0))}%"></i></div>
        <p>${this.escapeHtml(component.available ? detail(component) : 'Component unavailable; excluded from aggregate')}</p>
      </article>
    `).join('');

    const alerts = warning.alerts || [];
    document.getElementById('early-warning-alerts').innerHTML = alerts.length
      ? alerts.map(alert => `<div><strong>${this.escapeHtml(alert.level)} · ${this.escapeHtml(alert.title)}</strong><span>${this.escapeHtml(alert.why)}</span></div>`).join('')
      : '<div><strong>ROUTINE</strong><span>No component is above the alert threshold.</span></div>';
    const health = warning.data_health || {};
    document.getElementById('early-warning-health').innerHTML = `
      <span>${Number(health.events_considered) || 0} events</span>
      <span>${Number(health.independent_sources) || 0} domains</span>
      <span>${Number(health.market_series_available) || 0}/3 market series</span>
      <span>${Number(health.available_components) || 0}/3 components</span>
    `;
  },

  init() {
    if (!this.data) return;
    const meta = this.data.meta || {};
    const pill = document.getElementById('status-pill');
    pill.textContent = meta.status || 'STABLE';
    pill.className = `status-pill ${this.statusClass(meta.status)}`;
    document.getElementById('main-index').textContent = this.getIndex(meta).toFixed(2);
    document.getElementById('status-text').textContent = meta.status || '--';
    document.getElementById('countries-active').textContent =
      `ACTIVE: ${meta.countries_active || 0} / ${meta.countries_total || 0}`;
    document.getElementById('coverage-text').textContent =
      `${Math.round((meta.coverage_ratio || 0) * 100)}%`;
    const last = meta.generated_at ? new Date(meta.generated_at) : null;
    document.getElementById('last-update').textContent =
      last && !Number.isNaN(last.getTime()) ? last.toLocaleString() : '--';
    this.renderEarlyWarning();
  },
};

document.addEventListener('DOMContentLoaded', () => WTI.init());
