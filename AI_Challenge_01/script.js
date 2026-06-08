const plans = [
  {
    name: "Bronze",
    monthly_premium: 150,
    annual_limit: 500000,
    benefits: {
      outpatient: { limit_per_visit: 3000, visits_per_year: 30 },
      inpatient: { limit_per_day: 10000, days_per_year: 60 },
      dental: null,
      maternity: null,
    },
    copay_percentage: 20,
    waiting_period_days: 30,
    highlights: ["Basic coverage", "No dental or maternity"],
  },
  {
    name: "Silver",
    monthly_premium: 350,
    annual_limit: 1500000,
    benefits: {
      outpatient: { limit_per_visit: 5000, visits_per_year: 60 },
      inpatient: { limit_per_day: 25000, days_per_year: 120 },
      dental: { limit_per_year: 30000 },
      maternity: null,
    },
    copay_percentage: 10,
    waiting_period_days: 15,
    highlights: ["Includes dental", "Lower copay", "Higher limits"],
  },
  {
    name: "Gold",
    monthly_premium: 700,
    annual_limit: 5000000,
    benefits: {
      outpatient: { limit_per_visit: 10000, visits_per_year: -1 },
      inpatient: { limit_per_day: 50000, days_per_year: -1 },
      dental: { limit_per_year: 100000 },
      maternity: { limit_per_pregnancy: 200000 },
    },
    copay_percentage: 0,
    waiting_period_days: 0,
    highlights: ["Full coverage", "No copay", "No waiting period", "Unlimited visits"],
  },
];

const rows = [
  { id: "premium", label: "Monthly premium", best: "lowest" },
  { id: "annual", label: "Annual limit", best: "highest" },
  { id: "outpatient", label: "Outpatient care", best: "highest" },
  { id: "inpatient", label: "Inpatient care", best: "highest" },
  { id: "dental", label: "Dental", best: "highest" },
  { id: "maternity", label: "Maternity", best: "highest" },
  { id: "copay", label: "Copay", best: "lowest" },
  { id: "waiting", label: "Waiting period", best: "lowest" },
  { id: "highlights", label: "Highlights", best: null },
];

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function money(value) {
  return currencyFormatter.format(value);
}

function number(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function isUnlimited(value) {
  return value === -1;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusHtml(included, label) {
  const icon = included ? checkIcon() : crossIcon();
  return `<span class="status ${included ? "included" : "missing"}"><span class="status-icon">${icon}</span>${escapeHtml(label)}</span>`;
}

function checkIcon() {
  return '<svg viewBox="0 0 20 20" width="14" height="14" aria-hidden="true"><path d="M7.7 14.2 3.8 10.3l1.4-1.4 2.5 2.5 7.1-7.1 1.4 1.4-8.5 8.5Z" fill="currentColor"/></svg>';
}

function crossIcon() {
  return '<svg viewBox="0 0 20 20" width="13" height="13" aria-hidden="true"><path d="m5.2 4 4.8 4.8L14.8 4 16 5.2 11.2 10l4.8 4.8-1.2 1.2-4.8-4.8L5.2 16 4 14.8 8.8 10 4 5.2 5.2 4Z" fill="currentColor"/></svg>';
}

function valueForRow(plan, rowId) {
  const benefit = plan.benefits;

  if (rowId === "premium") {
    return plan.monthly_premium;
  }

  if (rowId === "annual") {
    return plan.annual_limit;
  }

  if (rowId === "outpatient") {
    const outpatient = benefit.outpatient;
    return isUnlimited(outpatient.visits_per_year)
      ? Infinity
      : outpatient.limit_per_visit * outpatient.visits_per_year;
  }

  if (rowId === "inpatient") {
    const inpatient = benefit.inpatient;
    return isUnlimited(inpatient.days_per_year)
      ? Infinity
      : inpatient.limit_per_day * inpatient.days_per_year;
  }

  if (rowId === "dental") {
    return benefit.dental ? benefit.dental.limit_per_year : null;
  }

  if (rowId === "maternity") {
    return benefit.maternity ? benefit.maternity.limit_per_pregnancy : null;
  }

  if (rowId === "copay") {
    return plan.copay_percentage;
  }

  if (rowId === "waiting") {
    return plan.waiting_period_days;
  }

  return null;
}

function cellContent(plan, rowId) {
  const b = plan.benefits;

  switch (rowId) {
    case "premium":
      return metric(`${money(plan.monthly_premium)}`, "per member per month");
    case "annual":
      return metric(money(plan.annual_limit), "maximum annual coverage");
    case "outpatient":
      return metric(
        `${money(b.outpatient.limit_per_visit)} per visit`,
        isUnlimited(b.outpatient.visits_per_year)
          ? "unlimited visits per year"
          : `${number(b.outpatient.visits_per_year)} visits per year`
      );
    case "inpatient":
      return metric(
        `${money(b.inpatient.limit_per_day)} per day`,
        isUnlimited(b.inpatient.days_per_year)
          ? "unlimited days per year"
          : `${number(b.inpatient.days_per_year)} days per year`
      );
    case "dental":
      return b.dental
        ? `${statusHtml(true, "Included")}${metric(money(b.dental.limit_per_year), "per year")}`
        : statusHtml(false, "Not included");
    case "maternity":
      return b.maternity
        ? `${statusHtml(true, "Included")}${metric(money(b.maternity.limit_per_pregnancy), "per pregnancy")}`
        : statusHtml(false, "Not included");
    case "copay":
      return metric(`${plan.copay_percentage}%`, "member cost share");
    case "waiting":
      return metric(`${plan.waiting_period_days} days`, "before coverage starts");
    case "highlights":
      return `<ul class="summary-list">${plan.highlights
        .map((item) => `<li><span class="dot-check"></span>${escapeHtml(item)}</li>`)
        .join("")}</ul>`;
    default:
      return "";
  }
}

function metric(main, detail) {
  return `<span class="metric-value"><span class="metric-main">${escapeHtml(main)}</span><span class="metric-detail">${escapeHtml(detail)}</span></span>`;
}

function bestPlanNames(row) {
  if (!row.best) {
    return new Set();
  }

  const values = plans
    .map((plan) => ({ plan, value: valueForRow(plan, row.id) }))
    .filter((item) => item.value !== null && item.value !== undefined);

  if (!values.length) {
    return new Set();
  }

  const target =
    row.best === "lowest"
      ? Math.min(...values.map((item) => item.value))
      : Math.max(...values.map((item) => item.value));

  return new Set(
    values.filter((item) => item.value === target).map((item) => item.plan.name)
  );
}

function scorePlan(plan) {
  const includedBenefits =
    2 + Number(Boolean(plan.benefits.dental)) + Number(Boolean(plan.benefits.maternity));
  const breadthScore = includedBenefits * 8;
  const annualLimitScore = Math.log10(plan.annual_limit / 100000) * 10;
  const copayScore = (20 - plan.copay_percentage) * 0.7;
  const waitingScore = (30 - plan.waiting_period_days) * 0.28;
  const efficiencyScore = Math.min(plan.annual_limit / plan.monthly_premium / 300, 14);
  const premiumPenalty = plan.monthly_premium / 12;

  return breadthScore + annualLimitScore + copayScore + waitingScore + efficiencyScore - premiumPenalty;
}

function recommendedPlan() {
  return plans
    .map((plan) => ({ plan, score: scorePlan(plan) }))
    .sort((a, b) => b.score - a.score)[0].plan;
}

function renderPlanCards(recommended) {
  const container = document.querySelector("#plan-grid");

  container.innerHTML = plans
    .map((plan) => {
      const tier = plan.name.toLowerCase();
      const isRecommended = plan.name === recommended.name;
      return `
        <article class="plan-card" data-tier="${tier}">
          <div class="plan-top">
            <div>
              <span class="tier-chip">${escapeHtml(plan.name)}</span>
              <h3>${escapeHtml(plan.name)} Plan</h3>
            </div>
            ${isRecommended ? '<span class="recommended-badge">Recommended</span>' : ""}
          </div>
          <p class="price"><strong>${money(plan.monthly_premium)}</strong> <span>/ month</span></p>
          <ul class="summary-list">
            <li><span class="dot-check"></span><strong>${money(plan.annual_limit)}</strong> annual limit</li>
            <li><span class="dot-check"></span><strong>${plan.copay_percentage}%</strong> copay</li>
            <li><span class="dot-check"></span><strong>${plan.waiting_period_days} days</strong> waiting period</li>
          </ul>
          <ul class="highlight-list">
            ${plan.highlights
              .map((item) => `<li><span class="dot-check"></span>${escapeHtml(item)}</li>`)
              .join("")}
          </ul>
        </article>
      `;
    })
    .join("");
}

function renderTable() {
  const table = document.querySelector("#comparison-table");
  const header = `
    <thead>
      <tr>
        <th scope="col">Feature</th>
        ${plans.map((plan) => `<th scope="col">${escapeHtml(plan.name)}</th>`).join("")}
      </tr>
    </thead>`;

  const body = rows
    .map((row) => {
      const winners = bestPlanNames(row);
      return `
        <tr>
          <td class="row-label">${escapeHtml(row.label)}</td>
          ${plans
            .map((plan) => {
              const isBest = winners.has(plan.name);
              return `
                <td class="${isBest ? "best-cell" : ""}">
                  ${cellContent(plan, row.id)}
                  ${isBest ? '<span class="best-pill">Best value</span>' : ""}
                </td>
              `;
            })
            .join("")}
        </tr>
      `;
    })
    .join("");

  table.innerHTML = `${header}<tbody>${body}</tbody>`;
}

function renderMobileComparison() {
  const container = document.querySelector("#mobile-comparison");
  container.innerHTML = plans
    .map((plan) => {
      return `
        <article class="mobile-plan">
          <div class="mobile-plan-header">
            <h3>${escapeHtml(plan.name)}</h3>
            <span class="tier-chip">${money(plan.monthly_premium)} / month</span>
          </div>
          ${rows
            .map((row) => {
              const winners = bestPlanNames(row);
              const isBest = winners.has(plan.name);
              return `
                <div class="mobile-row ${isBest ? "best-cell" : ""}">
                  <span class="mobile-row-label">${escapeHtml(row.label)}</span>
                  ${cellContent(plan, row.id)}
                  ${isBest ? '<span class="best-pill">Best value</span>' : ""}
                </div>
              `;
            })
            .join("")}
        </article>
      `;
    })
    .join("");
}

function renderRecommendation(plan) {
  document.querySelector("#recommended-plan-name").textContent = `${plan.name} Plan`;
  document.querySelector("#recommended-plan-reason").textContent =
    "Silver provides dental coverage, lower copay, shorter waiting period, and materially higher limits while keeping the monthly premium far below Gold.";
}

function init() {
  const recommended = recommendedPlan();
  renderRecommendation(recommended);
  renderPlanCards(recommended);
  renderTable();
  renderMobileComparison();
}

init();
