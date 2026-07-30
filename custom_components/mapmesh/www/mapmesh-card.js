class MapMeshCard extends HTMLElement {
  static getStubConfig() {
    return { entity: "sensor.example_profile" };
  }

  static getConfigElement() {
    const el = document.createElement("div");
    el.innerHTML = `
      <div class="card-config">
        <label>Entity</label>
        <input class="entity" type="text" placeholder="sensor.mapmesh_profile">
      </div>
    `;
    el.querySelector(".entity").addEventListener("change", (ev) => {
      const config = { entity: ev.target.value };
      const event = new Event("config-changed", { bubbles: true, composed: true });
      event.detail = { config };
      el.dispatchEvent(event);
    });
    return el;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("Entity must be specified");
    }
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 5;
  }

  _formatNumber(value) {
    if (value === null || value === undefined || value === "") return "—";
    return Number(value).toLocaleString();
  }

  _badgeProgress(badge) {
    if (!badge.value || !badge.next) return null;
    return Math.min(100, Math.round((badge.value / badge.next) * 100));
  }

  _render() {
    if (!this._config || !this._hass) return;

    const state = this._hass.states[this._config.entity];
    if (!state) {
      this.innerHTML = `<ha-card header="MapMe"><div class="content error">Entity not found</div></ha-card>`;
      return;
    }

    if (state.state === "unavailable") {
      this.innerHTML = `<ha-card header="MapMe"><div class="content error">Unavailable</div></ha-card>`;
      return;
    }

    const attrs = state.attributes || {};
    const name = attrs.name || state.attributes.friendly_name || "MapMe";
    const hardware = attrs.hardware || "";
    const rank = attrs.rank;
    const points = state.state;
    const stats = [
      { label: "Samples", value: attrs.total_samples },
      { label: "Unique hexes", value: attrs.unique_hexes },
      { label: "Pioneer hexes", value: attrs.pioneer_hexes },
      { label: "Active days", value: attrs.active_days },
      { label: "Repeaters", value: attrs.unique_repeaters },
      { label: "RX hexes", value: attrs.rx_hexes },
      { label: "Days since first", value: attrs.days_since_first },
      { label: "Road trip peak", value: attrs.road_trip_peak },
      { label: "Grinder peak", value: attrs.grinder_peak },
    ];

    const badges = Array.isArray(attrs.badges) ? attrs.badges : [];

    this.innerHTML = `
      <ha-card>
        <div class="mapmesh-card">
          <div class="header">
            <div class="title-block">
              <div class="name">${name}</div>
              ${hardware ? `<div class="hardware">${hardware}</div>` : ""}
            </div>
            <div class="headline-stats">
              <div class="stat-pill"><span class="label">Rank</span><span class="value">#${this._formatNumber(rank)}</span></div>
              <div class="stat-pill"><span class="label">Points</span><span class="value">${this._formatNumber(points)}</span></div>
            </div>
          </div>
          <div class="stats-grid">
            ${stats
              .map(
                (item) => `
              <div class="stat">
                <div class="stat-label">${item.label}</div>
                <div class="stat-value">${this._formatNumber(item.value)}</div>
              </div>`
              )
              .join("")}
          </div>
          <div class="badges-section">
            <div class="section-title">Badges</div>
            <div class="badges">
              ${badges
                .map((badge) => {
                  const progress = this._badgeProgress(badge);
                  const tierColor = badge.color || "var(--primary-color)";
                  const tierLabel = badge.label || badge.tier || "";
                  return `
                <div class="badge" style="--badge-color: ${tierColor}">
                  <div class="badge-header">
                    <span class="badge-icon">${badge.icon || ""}</span>
                    <span class="badge-name">${badge.name}</span>
                    ${tierLabel ? `<span class="badge-tier">${tierLabel}</span>` : ""}
                  </div>
                  <div class="badge-desc">${badge.desc || ""}</div>
                  ${
                    badge.value !== undefined
                      ? `<div class="badge-value">${this._formatNumber(badge.value)}${
                          badge.next ? ` / ${this._formatNumber(badge.next)}` : ""
                        }</div>`
                      : ""
                  }
                  ${
                    progress !== null
                      ? `<div class="progress"><div class="progress-bar" style="width: ${progress}%"></div></div>`
                      : ""
                  }
                </div>`;
                })
                .join("")}
            </div>
          </div>
        </div>
      </ha-card>
    `;

    if (!this._stylesApplied) {
      const style = document.createElement("style");
      style.textContent = `
        .mapmesh-card {
          padding: 16px;
          color: var(--primary-text-color);
        }
        .header {
          display: flex;
          justify-content: space-between;
          gap: 16px;
          flex-wrap: wrap;
          margin-bottom: 16px;
        }
        .name {
          font-size: 1.4rem;
          font-weight: 600;
        }
        .hardware {
          color: var(--secondary-text-color);
          font-size: 0.85rem;
          margin-top: 4px;
        }
        .headline-stats {
          display: flex;
          gap: 8px;
        }
        .stat-pill {
          background: var(--secondary-background-color, rgba(0,0,0,0.05));
          border-radius: 8px;
          padding: 8px 12px;
          text-align: center;
        }
        .stat-pill .label {
          display: block;
          font-size: 0.7rem;
          color: var(--secondary-text-color);
          text-transform: uppercase;
        }
        .stat-pill .value {
          font-size: 1.1rem;
          font-weight: 600;
        }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
          gap: 12px;
          margin-bottom: 20px;
        }
        .stat-label {
          font-size: 0.75rem;
          color: var(--secondary-text-color);
        }
        .stat-value {
          font-size: 1rem;
          font-weight: 500;
        }
        .section-title {
          font-size: 0.85rem;
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--secondary-text-color);
          text-transform: uppercase;
        }
        .badges {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 10px;
        }
        .badge {
          border-left: 3px solid var(--badge-color);
          padding: 8px 10px;
          background: var(--card-background-color, var(--ha-card-background, transparent));
        }
        .badge-header {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: wrap;
        }
        .badge-name {
          font-weight: 600;
          font-size: 0.9rem;
        }
        .badge-tier {
          font-size: 0.7rem;
          color: var(--badge-color);
          text-transform: uppercase;
        }
        .badge-desc {
          font-size: 0.75rem;
          color: var(--secondary-text-color);
          margin-top: 4px;
        }
        .badge-value {
          font-size: 0.8rem;
          margin-top: 4px;
        }
        .progress {
          height: 4px;
          background: var(--divider-color, rgba(127,127,127,0.3));
          border-radius: 2px;
          margin-top: 6px;
          overflow: hidden;
        }
        .progress-bar {
          height: 100%;
          background: var(--badge-color);
        }
        .error {
          padding: 16px;
          color: var(--error-color, #f44336);
        }
      `;
      this.appendChild(style);
      this._stylesApplied = true;
    }
  }
}

customElements.define("mapmesh-card", MapMeshCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "mapmesh-card",
  name: "MapMe Profile",
  description: "Display MapMe user stats and badges",
  preview: true,
});
