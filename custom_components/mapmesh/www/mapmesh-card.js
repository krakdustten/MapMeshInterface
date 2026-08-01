import {
  badgeProgress,
  escapeHtml,
  formatNumber,
  heroStats,
  iconEmoji,
  moreStats,
  progressFooter,
} from "./mapmesh-card-logic.js";

const CARD_STYLES = `
  .mapmesh-card {
    padding: 16px;
    color: var(--primary-text-color);
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 16px;
  }
  .name {
    font-size: 1.35rem;
    font-weight: 600;
    line-height: 1.2;
  }
  .hardware {
    color: var(--secondary-text-color);
    font-size: 0.8rem;
    margin-top: 4px;
  }
  .headline-stats {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .stat-pill {
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    border-radius: 10px;
    padding: 8px 12px;
    text-align: center;
    min-width: 72px;
  }
  .stat-pill .label {
    display: block;
    font-size: 0.65rem;
    letter-spacing: 0.04em;
    color: var(--secondary-text-color);
    text-transform: uppercase;
  }
  .stat-pill .value {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--primary-color);
  }
  .hero-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 16px;
  }
  .hero-stat {
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
  }
  .hero-stat .value {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--primary-color);
    line-height: 1.1;
  }
  .hero-stat .label {
    margin-top: 6px;
    font-size: 0.65rem;
    letter-spacing: 0.06em;
    color: var(--secondary-text-color);
    text-transform: uppercase;
  }
  .more-stats {
    margin-bottom: 18px;
  }
  .more-stats summary {
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--secondary-text-color);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    list-style: none;
  }
  .more-stats summary::-webkit-details-marker {
    display: none;
  }
  .more-stats summary::before {
    content: "▸";
    display: inline-block;
    margin-right: 6px;
    transition: transform 0.15s ease;
  }
  .more-stats[open] summary::before {
    transform: rotate(90deg);
  }
  .more-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
    margin-top: 10px;
  }
  .more-stat .label {
    font-size: 0.7rem;
    color: var(--secondary-text-color);
  }
  .more-stat .value {
    font-size: 0.95rem;
    font-weight: 600;
  }
  .section-title {
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 10px;
    color: var(--secondary-text-color);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .achievements {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .achievement {
    --badge-color: var(--primary-color);
    border-radius: 12px;
    border-left: 4px solid var(--badge-color);
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
    padding: 12px 14px;
  }
  .achievement-top {
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }
  .achievement-icon {
    font-size: 1.25rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .achievement-body {
    flex: 1;
    min-width: 0;
  }
  .achievement-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }
  .achievement-name {
    font-weight: 700;
    font-size: 0.95rem;
  }
  .achievement-desc {
    font-size: 0.75rem;
    color: var(--secondary-text-color);
    margin-top: 2px;
  }
  .tier-pill {
    flex-shrink: 0;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #fff;
    background: var(--badge-color);
    border-radius: 6px;
    padding: 4px 8px;
  }
  .achievement-progress {
    margin-top: 10px;
  }
  .progress {
    height: 4px;
    background: var(--divider-color, rgba(127, 127, 127, 0.3));
    border-radius: 2px;
    overflow: hidden;
  }
  .progress-bar {
    height: 100%;
    background: var(--badge-color);
  }
  .progress-footer {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-top: 6px;
    font-size: 0.75rem;
    color: var(--secondary-text-color);
  }
  .progress-footer .current {
    color: var(--primary-text-color);
    font-weight: 500;
  }
  .error {
    padding: 16px;
    color: var(--error-color, #f44336);
  }
  @media (max-width: 420px) {
    .hero-stats {
      grid-template-columns: 1fr;
    }
  }
`;

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
    return 6;
  }

  _renderAchievement(badge) {
    const progress = badgeProgress(badge);
    const footer = progressFooter(badge);
    const tierColor = badge.color || "var(--primary-color)";
    const tierLabel = badge.label || badge.tier || "";
    const emoji = iconEmoji(badge.icon);

    return `
      <div class="achievement" style="--badge-color: ${escapeHtml(tierColor)}">
        <div class="achievement-top">
          <span class="achievement-icon" aria-hidden="true">${emoji}</span>
          <div class="achievement-body">
            <div class="achievement-title-row">
              <span class="achievement-name">${escapeHtml(badge.name || "")}</span>
              ${
                tierLabel
                  ? `<span class="tier-pill">${escapeHtml(String(tierLabel))}</span>`
                  : ""
              }
            </div>
            ${
              badge.desc
                ? `<div class="achievement-desc">${escapeHtml(badge.desc)}</div>`
                : ""
            }
          </div>
        </div>
        ${
          progress !== null
            ? `<div class="achievement-progress">
                <div class="progress"><div class="progress-bar" style="width: ${progress}%"></div></div>
                ${
                  footer
                    ? `<div class="progress-footer">
                        <span class="current">${escapeHtml(footer.current)}</span>
                        ${
                          footer.goal
                            ? `<span class="goal">${escapeHtml(footer.goal)}</span>`
                            : ""
                        }
                      </div>`
                    : ""
                }
              </div>`
            : footer
              ? `<div class="progress-footer" style="margin-top: 8px">
                  <span class="current">${escapeHtml(footer.current)}</span>
                </div>`
              : ""
        }
      </div>`;
  }

  _render() {
    if (!this._config || !this._hass) return;

    const moreOpen = this.querySelector("details.more-stats")?.open === true;

    const state = this._hass.states[this._config.entity];
    if (!state) {
      this.innerHTML = `<ha-card header="MapMe"><style>${CARD_STYLES}</style><div class="error">Entity not found</div></ha-card>`;
      return;
    }

    if (state.state === "unavailable") {
      this.innerHTML = `<ha-card header="MapMe"><style>${CARD_STYLES}</style><div class="error">Unavailable</div></ha-card>`;
      return;
    }

    const attrs = state.attributes || {};
    const name = attrs.name || attrs.friendly_name || "MapMe";
    const hardware = attrs.hardware || "";
    const rank = attrs.rank;
    const points = state.state;
    const heroes = heroStats(attrs);
    const secondary = moreStats(attrs);
    const badges = Array.isArray(attrs.badges) ? attrs.badges : [];

    this.innerHTML = `
      <ha-card>
        <style>${CARD_STYLES}</style>
        <div class="mapmesh-card">
          <div class="header">
            <div class="title-block">
              <div class="name">${escapeHtml(name)}</div>
              ${hardware ? `<div class="hardware">${escapeHtml(hardware)}</div>` : ""}
            </div>
            <div class="headline-stats">
              <div class="stat-pill">
                <span class="label">Rank</span>
                <span class="value">#${escapeHtml(formatNumber(rank))}</span>
              </div>
              <div class="stat-pill">
                <span class="label">Points</span>
                <span class="value">${escapeHtml(formatNumber(points))}</span>
              </div>
            </div>
          </div>

          <div class="hero-stats">
            ${heroes
              .map(
                (item) => `
              <div class="hero-stat">
                <div class="value">${escapeHtml(formatNumber(item.value))}</div>
                <div class="label">${escapeHtml(item.label)}</div>
              </div>`
              )
              .join("")}
          </div>

          ${
            secondary.length
              ? `<details class="more-stats"${moreOpen ? " open" : ""}>
                  <summary>More stats</summary>
                  <div class="more-stats-grid">
                    ${secondary
                      .map(
                        (item) => `
                      <div class="more-stat">
                        <div class="label">${escapeHtml(item.label)}</div>
                        <div class="value">${escapeHtml(formatNumber(item.value))}</div>
                      </div>`
                      )
                      .join("")}
                  </div>
                </details>`
              : ""
          }

          <div class="achievements-section">
            <div class="section-title">Achievements</div>
            <div class="achievements">
              ${
                badges.length
                  ? badges.map((badge) => this._renderAchievement(badge)).join("")
                  : `<div class="achievement-desc">No achievements yet</div>`
              }
            </div>
          </div>
        </div>
      </ha-card>
    `;
  }
}

if (!customElements.get("mapmesh-card")) {
  customElements.define("mapmesh-card", MapMeshCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "mapmesh-card")) {
  window.customCards.push({
    type: "mapmesh-card",
    name: "MapMe Profile",
    description: "Display MapMe user stats and badges",
    preview: true,
  });
}
