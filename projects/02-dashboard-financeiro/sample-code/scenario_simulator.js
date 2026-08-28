/**
 * Financial Scenario Simulator
 * Recalculates P&L in real-time as the user adjusts sliders.
 *
 * Sanitized version — no real financial data or company references.
 */

const PRESET_SCENARIOS = [
    {
        name: "Current (Live Data)",
        dynamic: true,
        description: "Real-time data from the database",
    },
    {
        name: "Cut Marketing 30%",
        adjustments: { marketingDelta: -0.30 },
        description: "What if we reduce ad spend by 30%?",
    },
    {
        name: "ROAS Drops to 1.5x",
        adjustments: { targetRoas: 1.5 },
        description: "Stress test: low ROAS scenario",
    },
    {
        name: "Double Subscriptions",
        adjustments: { subscriptionMultiplier: 2.0 },
        description: "What if recurring revenue doubles?",
    },
    {
        name: "Refund Rate 20%",
        adjustments: { refundRate: 0.20 },
        description: "Stress test: high refund scenario",
    },
    {
        name: "Scale Up 50%",
        adjustments: { marketingDelta: 0.50, targetRoas: null },
        description: "Increase spend 50%, keep current ROAS",
    },
    {
        name: "Break Even",
        adjustments: { breakevenMode: true },
        description: "Find the minimum ROAS to cover all costs",
    },
];


function simulateScenario(baseData, adjustments) {
    const sim = { ...baseData };

    // Marketing spend
    if (adjustments.marketingDelta !== undefined) {
        sim.marketing = baseData.marketing * (1 + adjustments.marketingDelta);
    }

    // Revenue projection based on ROAS
    const effectiveRoas = adjustments.targetRoas || baseData.roas;
    sim.grossRevenue = sim.marketing * effectiveRoas;
    sim.netRevenue = sim.grossRevenue * (1 - baseData.platformFeeRate);

    // Refund projection
    const refundRate = adjustments.refundRate || baseData.refundRate;
    sim.refunds = sim.grossRevenue * refundRate;

    // Subscription revenue
    const subMultiplier = adjustments.subscriptionMultiplier || 1.0;
    sim.subscriptions = baseData.subscriptions * subMultiplier;

    // Fixed costs (don't scale with marketing)
    sim.fixedCosts = baseData.payroll + baseData.software + baseData.operations;

    // P&L calculations
    sim.totalExpenses = sim.marketing + sim.fixedCosts;
    sim.operatingProfit = sim.netRevenue - sim.totalExpenses;
    sim.finalResult = sim.operatingProfit + sim.subscriptions;

    // Derived metrics
    sim.roas = sim.marketing > 0 ? sim.netRevenue / sim.marketing : 0;
    sim.netMargin = sim.grossRevenue > 0
        ? ((sim.netRevenue - sim.totalExpenses) / sim.grossRevenue * 100)
        : 0;
    sim.cpa = sim.orderCount > 0 ? sim.marketing / sim.orderCount : 0;

    // Breakeven ROAS (minimum ROAS to cover all costs)
    sim.breakevenRoas = sim.marketing > 0
        ? sim.totalExpenses / sim.marketing
        : 0;

    // Subscription dependency alert
    sim.subscriptionDependency = sim.operatingProfit < 0 && sim.finalResult > 0;

    return sim;
}


function renderSimulationResults(sim) {
    // Hero KPIs
    updateKPI("revenue", formatBRL(sim.netRevenue), deltaPercent(sim.netRevenue, sim._baseNetRevenue));
    updateKPI("roas", sim.roas.toFixed(2) + "x", deltaPercent(sim.roas, sim._baseRoas));
    updateKPI("margin", sim.netMargin.toFixed(1) + "%", deltaPP(sim.netMargin, sim._baseMargin));
    updateKPI("subs", formatBRL(sim.subscriptions));

    // P&L table
    updatePnlRow("gross-revenue", sim.grossRevenue);
    updatePnlRow("platform-fees", -(sim.grossRevenue - sim.netRevenue));
    updatePnlRow("net-revenue", sim.netRevenue);
    updatePnlRow("marketing", -sim.marketing);
    updatePnlRow("fixed-costs", -sim.fixedCosts);
    updatePnlRow("operating-profit", sim.operatingProfit);
    updatePnlRow("subscriptions", sim.subscriptions);
    updatePnlRow("final-result", sim.finalResult);
    updatePnlRow("breakeven-roas", sim.breakevenRoas, "x");

    // Alerts
    if (sim.subscriptionDependency) {
        showAlert(
            "Subscription Dependency",
            `Operating result is negative (${formatBRL(sim.operatingProfit)}), ` +
            `but subscriptions (${formatBRL(sim.subscriptions)}) bring it to ` +
            `${formatBRL(sim.finalResult)}. The business depends on recurring revenue.`,
            "warning"
        );
    }

    if (sim.roas < sim.breakevenRoas) {
        showAlert(
            "Below Breakeven",
            `Current ROAS (${sim.roas.toFixed(2)}x) is below breakeven ` +
            `(${sim.breakevenRoas.toFixed(2)}x). The operation is losing money.`,
            "danger"
        );
    }
}


// Slider event handlers
function initSliders(baseData) {
    const sliders = {
        "slider-marketing": { key: "marketingDelta", min: -0.5, max: 1.0, step: 0.05, format: pctFormat },
        "slider-roas":      { key: "targetRoas",     min: 0.5,  max: 5.0, step: 0.1,  format: roasFormat },
        "slider-refund":    { key: "refundRate",      min: 0.0,  max: 0.3, step: 0.01, format: pctFormat },
        "slider-subs":      { key: "subscriptionMultiplier", min: 0.0, max: 3.0, step: 0.1, format: multFormat },
    };

    for (const [id, config] of Object.entries(sliders)) {
        const el = document.getElementById(id);
        el.min = config.min;
        el.max = config.max;
        el.step = config.step;

        el.addEventListener("input", () => {
            const adjustments = collectSliderValues(sliders);
            const sim = simulateScenario(baseData, adjustments);
            renderSimulationResults(sim);
        });
    }
}


// --- Utility ---

function formatBRL(value) {
    return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function deltaPercent(current, base) {
    if (base === 0) return null;
    return ((current - base) / Math.abs(base) * 100).toFixed(1);
}

function deltaPP(current, base) {
    return (current - base).toFixed(1);
}
