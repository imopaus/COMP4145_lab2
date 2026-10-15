async function loadDashboardData() {
    const response = await fetch('dashboard_data.json');
    if (!response.ok) {
        throw new Error('Unable to load dashboard data');
    }
    return await response.json();
}

function formatPercent(value) {
    return `${Number(value).toFixed(2)}%`;
}

function plotPriceChart(data) {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;

    const priceSeries = data.price_history.map(item => ({
        x: new Date(item.Date).getTime(),
        y: Number(item.Close)
    }));

    const ma50Series = data.price_history.map(item => ({
        x: new Date(item.Date).getTime(),
        y: Number(item.MA50)
    }));

    const ma200Series = data.price_history.map(item => ({
        x: new Date(item.Date).getTime(),
        y: Number(item.MA200)
    }));

    const buyPoints = data.trades.map(trade => ({
        x: new Date(trade.BuyDate).getTime(),
        y: Number(trade.BuyPrice)
    }));

    const sellPoints = data.trades.map(trade => ({
        x: new Date(trade.SellDate).getTime(),
        y: Number(trade.SellPrice)
    }));

    new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Close Price',
                    data: priceSeries,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37,99,235,0.1)',
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    tension: 0.1
                },
                {
                    label: 'MA 50',
                    data: ma50Series,
                    borderColor: '#f59e0b',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                },
                {
                    label: 'MA 200',
                    data: ma200Series,
                    borderColor: '#10b981',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                },
                {
                    label: 'Buy Signal',
                    data: buyPoints,
                    type: 'scatter',
                    showLine: false,
                    pointBackgroundColor: '#22c55e',
                    pointRadius: 6,
                    pointHoverRadius: 7,
                    pointStyle: 'circle'
                },
                {
                    label: 'Sell Signal',
                    data: sellPoints,
                    type: 'scatter',
                    showLine: false,
                    pointBackgroundColor: '#ef4444',
                    pointRadius: 6,
                    pointHoverRadius: 7,
                    pointStyle: 'circle'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'nearest',
                intersect: false
            },
            parsing: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw?.y ?? context.parsed.y;
                            return `${context.dataset.label}: ${Number(value).toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'month',
                        tooltipFormat: 'MMM d, yyyy'
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Price (USD)'
                    }
                }
            }
        }
    });
}

function renderSummary(data) {
    const summary = data.summary;

    const cards = [
        { id: 'totalTrades', label: 'Total trades', value: summary.total_trades },
        { id: 'winRate', label: 'Win rate', value: formatPercent(summary.win_rate) },
        { id: 'avgProfit', label: 'Average profit', value: formatPercent(summary.avg_profit) },
        { id: 'avgHolding', label: 'Average holding', value: `${Number(summary.avg_holding).toFixed(1)} days` }
    ];

    cards.forEach(card => {
        const el = document.getElementById(card.id);
        if (el) {
            el.textContent = card.value;
        }
    });

    const winEl = document.getElementById('winningTrades');
    const lossEl = document.getElementById('losingTrades');
    if (winEl) winEl.textContent = summary.win_trades;
    if (lossEl) lossEl.textContent = summary.loss_trades;
}

function renderTradeTable(data) {
    const tbody = document.getElementById('tradeTableBody');
    if (!tbody) return;

    tbody.innerHTML = data.trades.map(trade => {
        const profitClass = Number(trade.ProfitPct) >= 0 ? 'positive' : 'negative';
        return `
            <tr>
                <td>${trade.BuyDate}</td>
                <td>${Number(trade.BuyPrice).toFixed(2)}</td>
                <td>${trade.SellDate}</td>
                <td>${Number(trade.SellPrice).toFixed(2)}</td>
                <td>${trade.HoldingDays}</td>
                <td class="${profitClass}">${Number(trade.ProfitPct).toFixed(2)}%</td>
                <td>${trade.SellReason}</td>
            </tr>
        `;
    }).join('');
}

async function initializeDashboard() {
    try {
        const data = await loadDashboardData();
        plotPriceChart(data);
        renderSummary(data);
        renderTradeTable(data);
    } catch (error) {
        console.error(error);
        document.body.innerHTML = '<h2 style="padding: 2rem;">Unable to load market data.</h2>';
    }
}

window.addEventListener('DOMContentLoaded', initializeDashboard);
