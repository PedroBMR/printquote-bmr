/**
 * Motor de cálculo do PrintQuote by BMR — espelha exatamente as fórmulas
 * de calc3d/core/calculator.py (versão desktop) em JavaScript puro, sem
 * dependências. Toda a lógica de negócio mora aqui, isolada da UI.
 */

const CHART_COLORS = {
  "Material": "#c4b5fd",
  "Energia": "#fcd34d",
  "Máquina (depreciação+manutenção)": "#a5f3fc",
  "Mão de obra": "#86efac",
  "Overhead": "#fca5a5",
  "Embalagem": "#94a3b8",
  "Frete absorvido": "#f0abfc",
};

function formatBRL(value) {
  const n = Number(value) || 0;
  return n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatPct(fraction) {
  return `${(fraction * 100).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
}

function computeMaterialCost(piece) {
  return piece.materials.reduce((total, usage) => {
    const gramsWithWaste = usage.grams * (1 + piece.wastePct);
    const pricePerGram = usage.material.pricePerKg / 1000;
    return total + gramsWithWaste * pricePerGram;
  }, 0);
}

function computeEnergyCost(piece, settings) {
  const tariff = piece.energyTariffKwh ?? settings.energyTariffKwh;
  const kwh = (piece.printer.wattsAvg / 1000) * piece.printTimeHours;
  return kwh * tariff;
}

function computeDepreciationCost(piece) {
  const { purchasePrice, lifetimeHours } = piece.printer;
  const perHour = lifetimeHours > 0 ? purchasePrice / lifetimeHours : 0;
  return perHour * piece.printTimeHours;
}

function computeMaintenanceCost(piece) {
  return piece.printer.maintenanceCostPerHour * piece.printTimeHours;
}

function computeLaborCost(piece, settings) {
  const rate = piece.laborRateHour ?? settings.laborRateHour;
  const hours =
    piece.labor.modelingHours +
    piece.labor.slicingHours +
    piece.labor.postProcessingHours +
    piece.labor.packagingHours;
  return hours * rate;
}

function computeShippingAbsorbed(piece) {
  const { mode, shippingCost, subsidizePct } = piece.shipping;
  if (mode === "repassar") return 0;
  if (mode === "gratis_embutido") return shippingCost;
  if (mode === "subsidiar") return shippingCost * subsidizePct;
  return 0;
}

function computeBreakdown(piece, settings) {
  const materialCost = computeMaterialCost(piece);
  const energyCost = computeEnergyCost(piece, settings);
  const depreciationCost = computeDepreciationCost(piece);
  const maintenanceCost = computeMaintenanceCost(piece);
  const laborCost = computeLaborCost(piece, settings);

  const baseCost = materialCost + energyCost + depreciationCost + maintenanceCost + laborCost;

  let failureRate = piece.failureRatePct ?? settings.failureRatePct;
  failureRate = Math.min(Math.max(failureRate, 0), 0.95);
  const failureAdjustedCost = failureRate < 1 ? baseCost / (1 - failureRate) : baseCost;

  const overheadCost = piece.overheadPerPiece;
  const packagingCost = piece.packagingCost;
  const shippingAbsorbed = computeShippingAbsorbed(piece);

  const totalCost = failureAdjustedCost + overheadCost + packagingCost + shippingAbsorbed;

  return {
    materialCost,
    energyCost,
    depreciationCost,
    maintenanceCost,
    laborCost,
    baseCost,
    failureAdjustedCost,
    overheadCost,
    packagingCost,
    shippingAbsorbed,
    totalCost,
  };
}

function breakdownChartItems(breakdown) {
  const items = [
    ["Material", breakdown.materialCost],
    ["Energia", breakdown.energyCost],
    ["Máquina (depreciação+manutenção)", breakdown.depreciationCost + breakdown.maintenanceCost],
    ["Mão de obra", breakdown.laborCost],
    ["Overhead", breakdown.overheadCost],
    ["Embalagem", breakdown.packagingCost],
    ["Frete absorvido", breakdown.shippingAbsorbed],
  ];
  return items.filter(([, value]) => value > 0.0001);
}

function totalFeePct(piece, settings) {
  const channelPct = piece.saleChannel ? piece.saleChannel.feePct : 0;
  const gatewayPct = piece.paymentGatewayPct ?? settings.paymentGatewayPct;
  const taxPct = piece.taxPct ?? settings.taxPct;
  return channelPct + gatewayPct + taxPct;
}

function channelFixedFee(piece) {
  return piece.saleChannel ? piece.saleChannel.feeFixed : 0;
}

function priceCostPlus(totalCost, markupMultiplier) {
  return totalCost * markupMultiplier;
}

function priceMarginOnPrice(totalCost, marginPct, feePct, feeFixed) {
  const denom = 1 - marginPct - feePct;
  if (denom <= 0) return Infinity;
  return (totalCost + feeFixed) / denom;
}

function analyzePrice(price, totalCost, feePct, feeFixed) {
  const fees = price * feePct + feeFixed;
  const netProfit = price - fees - totalCost;
  const netMarginPct = price ? netProfit / price : 0;
  return { price, fees, netProfit, netMarginPct };
}

function buildScenarios(totalCost, piece, settings, margins = [0.3, 0.5, 1.0]) {
  const feePct = totalFeePct(piece, settings);
  const feeFixed = channelFixedFee(piece);
  return margins.map((m) => {
    const cpPrice = priceCostPlus(totalCost, 1 + m);
    const cpAnalysis = analyzePrice(cpPrice, totalCost, feePct, feeFixed);
    const mpPrice = priceMarginOnPrice(totalCost, m, feePct, feeFixed);
    const mpAnalysis = analyzePrice(mpPrice, totalCost, feePct, feeFixed);
    return {
      label: `${Math.round(m * 100)}%`,
      marginPct: m,
      priceCostPlus: cpPrice,
      priceMarginOnPrice: mpPrice,
      netProfitCostPlus: cpAnalysis.netProfit,
      netProfitMarginOnPrice: mpAnalysis.netProfit,
    };
  });
}

function computePricing(piece, settings, options = {}) {
  const margins = options.margins ?? [0.3, 0.5, 1.0];
  const competitorPrice = options.competitorPrice ?? null;

  const breakdown = computeBreakdown(piece, settings);
  const scenarios = buildScenarios(breakdown.totalCost, piece, settings, margins);

  let competitorAnalysis = null;
  if (competitorPrice) {
    const feePct = totalFeePct(piece, settings);
    const feeFixed = channelFixedFee(piece);
    competitorAnalysis = analyzePrice(competitorPrice, breakdown.totalCost, feePct, feeFixed);
  }

  return { breakdown, scenarios, competitorPrice, competitorAnalysis };
}
