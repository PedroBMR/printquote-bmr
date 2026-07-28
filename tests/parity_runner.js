/**
 * Runner de paridade (lado JS). Lê tests/cases.json, roda cada caso pelo
 * motor real da versão web (docs/js/core.js) e imprime no stdout um JSON
 * com o breakdown, os cenários e a análise de concorrente normalizados —
 * pra o teste em Python comparar com o motor desktop (calc3d).
 *
 * Valores não-finitos (Infinity/NaN) viram a string "inf" pra serem
 * comparáveis de forma estável entre as duas linguagens.
 */
const fs = require("fs");
const path = require("path");
const core = require(path.join(__dirname, "..", "docs", "js", "core.js"));

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "cases.json"), "utf8"));

function n(x) {
  return Number.isFinite(x) ? x : "inf";
}

function buildPiece(c) {
  return {
    name: c.id,
    printer: {
      purchasePrice: c.printer.purchasePrice,
      lifetimeHours: c.printer.lifetimeHours,
      wattsAvg: c.printer.wattsAvg,
      maintenanceCostPerHour: c.printer.maintenanceCostPerHour,
    },
    printTimeHours: c.printTimeHours,
    materials: c.materials.map((m) => ({ material: { pricePerKg: m.pricePerKg }, grams: m.grams })),
    wastePct: c.wastePct,
    labor: {
      modelingHours: c.labor.modelingHours,
      slicingHours: c.labor.slicingHours,
      postProcessingHours: c.labor.postProcessingHours,
      packagingHours: c.labor.packagingHours,
    },
    laborRateHour: c.laborRateHour,
    failureRatePct: c.failureRatePct,
    packagingCost: c.packagingCost,
    shipping: c.shipping,
    saleChannel: c.saleChannel,
    taxPct: c.taxPct,
    paymentGatewayPct: c.paymentGatewayPct,
    overheadPerPiece: c.overheadPerPiece,
    energyTariffKwh: c.energyTariffKwh,
  };
}

function runCase(c) {
  const piece = buildPiece(c);
  const res = core.computePricing(piece, c.settings, {
    margins: c.margins,
    competitorPrice: c.competitorPrice,
  });
  const b = res.breakdown;
  return {
    id: c.id,
    breakdown: {
      materialCost: b.materialCost,
      energyCost: b.energyCost,
      depreciationCost: b.depreciationCost,
      maintenanceCost: b.maintenanceCost,
      laborCost: b.laborCost,
      baseCost: b.baseCost,
      failureAdjustedCost: b.failureAdjustedCost,
      overheadCost: b.overheadCost,
      packagingCost: b.packagingCost,
      shippingAbsorbed: b.shippingAbsorbed,
      totalCost: b.totalCost,
    },
    scenarios: res.scenarios.map((s) => ({
      marginPct: s.marginPct,
      priceCostPlus: n(s.priceCostPlus),
      priceMarginOnPrice: n(s.priceMarginOnPrice),
      netProfitCostPlus: n(s.netProfitCostPlus),
      netProfitMarginOnPrice: n(s.netProfitMarginOnPrice),
    })),
    competitor: res.competitorAnalysis
      ? {
          price: n(res.competitorAnalysis.price),
          fees: n(res.competitorAnalysis.fees),
          netProfit: n(res.competitorAnalysis.netProfit),
          netMarginPct: n(res.competitorAnalysis.netMarginPct),
        }
      : null,
  };
}

const results = {};
for (const c of cases) results[c.id] = runCase(c);
process.stdout.write(JSON.stringify(results));
