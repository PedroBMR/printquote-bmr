/**
 * UI do PrintQuote by BMR (versão web). Lê/escreve via Store (localStorage)
 * e calcula via core.js — este arquivo só cuida de DOM e eventos.
 */

let lastResult = null;
let lastPiece = null;
let editingMaterialId = null;
let editingPrinterId = null;
let editingChannelId = null;
let selectedHistoryId = null;

// ---------------------------------------------------------------------
// Util
// ---------------------------------------------------------------------
function $(id) {
  return document.getElementById(id);
}

function showToast(message) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.remove("show"), 2800);
}

function num(id) {
  const v = parseFloat($(id).value);
  return Number.isFinite(v) ? v : 0;
}

// ---------------------------------------------------------------------
// Abas
// ---------------------------------------------------------------------
function switchTab(name) {
  document.querySelectorAll("nav.tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("active", p.id === `tab-${name}`));
  if (name === "calculator") refreshLibraries();
  if (name === "history") renderHistoryTable();
}

document.querySelectorAll("nav.tabs button").forEach((btn) => {
  btn.addEventListener("click", () => switchTab(btn.dataset.tab));
});

// =======================================================================
// MATERIAIS
// =======================================================================
function renderMaterialsTable() {
  const tbody = $("materialsTableBody");
  const items = Store.listMaterials().sort((a, b) => a.name.localeCompare(b.name));
  tbody.innerHTML = items.map((m) => `
    <tr class="selectable" data-id="${m.id}">
      <td>${m.name}</td>
      <td>${m.materialType === "filamento" ? "Filamento" : "Resina"}</td>
      <td class="num">${formatBRL(m.pricePerKg)}</td>
      <td>${m.unitLabel}</td>
      <td>${m.notes || ""}</td>
    </tr>
  `).join("") || `<tr><td colspan="5" class="hint">Nenhum material cadastrado ainda.</td></tr>`;

  tbody.querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => selectMaterialForEdit(Number(row.dataset.id)));
  });
}

function selectMaterialForEdit(id) {
  const material = Store.listMaterials().find((m) => m.id === id);
  if (!material) return;
  editingMaterialId = id;
  $("matName").value = material.name;
  $("matType").value = material.materialType;
  $("matPrice").value = material.pricePerKg;
  $("matUnit").value = material.unitLabel;
  $("matNotes").value = material.notes || "";
}

function clearMaterialForm() {
  editingMaterialId = null;
  $("matName").value = "";
  $("matType").value = "filamento";
  $("matPrice").value = 0;
  $("matUnit").value = "kg";
  $("matNotes").value = "";
}

$("matType").addEventListener("change", () => {
  $("matUnit").value = $("matType").value === "filamento" ? "kg" : "L";
});

$("matSaveBtn").addEventListener("click", () => {
  const name = $("matName").value.trim();
  if (!name) return showToast("Informe o nome do material.");
  Store.saveMaterial({
    id: editingMaterialId,
    name,
    materialType: $("matType").value,
    pricePerKg: num("matPrice"),
    unitLabel: $("matUnit").value,
    notes: $("matNotes").value.trim(),
  });
  clearMaterialForm();
  renderMaterialsTable();
  refreshLibraries();
  showToast("Material salvo.");
});

$("matNewBtn").addEventListener("click", clearMaterialForm);

$("matDeleteBtn").addEventListener("click", () => {
  if (editingMaterialId == null) return;
  if (!confirm("Excluir este material?")) return;
  Store.deleteMaterial(editingMaterialId);
  clearMaterialForm();
  renderMaterialsTable();
  refreshLibraries();
  showToast("Material excluído.");
});

// =======================================================================
// IMPRESSORAS
// =======================================================================
function renderPrintersTable() {
  const tbody = $("printersTableBody");
  const items = Store.listPrinters().sort((a, b) => a.name.localeCompare(b.name));
  tbody.innerHTML = items.map((p) => `
    <tr class="selectable" data-id="${p.id}">
      <td>${p.name}</td>
      <td class="num">${formatBRL(p.purchasePrice)}</td>
      <td class="num">${p.lifetimeHours}</td>
      <td class="num">${p.wattsAvg}</td>
      <td class="num">${formatBRL(p.maintenanceCostPerHour)}</td>
    </tr>
  `).join("") || `<tr><td colspan="5" class="hint">Nenhuma impressora cadastrada ainda.</td></tr>`;

  tbody.querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => selectPrinterForEdit(Number(row.dataset.id)));
  });
}

function selectPrinterForEdit(id) {
  const printer = Store.listPrinters().find((p) => p.id === id);
  if (!printer) return;
  editingPrinterId = id;
  $("prnName").value = printer.name;
  $("prnPrice").value = printer.purchasePrice;
  $("prnLifetime").value = printer.lifetimeHours;
  $("prnWatts").value = printer.wattsAvg;
  $("prnMaintenance").value = printer.maintenanceCostPerHour;
  $("prnNotes").value = printer.notes || "";
}

function clearPrinterForm() {
  editingPrinterId = null;
  $("prnName").value = "";
  $("prnPrice").value = 0;
  $("prnLifetime").value = 6000;
  $("prnWatts").value = 120;
  $("prnMaintenance").value = 0.15;
  $("prnNotes").value = "";
}

$("prnSaveBtn").addEventListener("click", () => {
  const name = $("prnName").value.trim();
  if (!name) return showToast("Informe o nome da impressora.");
  Store.savePrinter({
    id: editingPrinterId,
    name,
    purchasePrice: num("prnPrice"),
    lifetimeHours: num("prnLifetime"),
    wattsAvg: num("prnWatts"),
    maintenanceCostPerHour: num("prnMaintenance"),
    notes: $("prnNotes").value.trim(),
  });
  clearPrinterForm();
  renderPrintersTable();
  refreshLibraries();
  showToast("Impressora salva.");
});

$("prnNewBtn").addEventListener("click", clearPrinterForm);

$("prnDeleteBtn").addEventListener("click", () => {
  if (editingPrinterId == null) return;
  if (!confirm("Excluir esta impressora?")) return;
  Store.deletePrinter(editingPrinterId);
  clearPrinterForm();
  renderPrintersTable();
  refreshLibraries();
  showToast("Impressora excluída.");
});

// =======================================================================
// CANAIS DE VENDA
// =======================================================================
function renderChannelsTable() {
  const tbody = $("channelsTableBody");
  const items = Store.listChannels().sort((a, b) => a.name.localeCompare(b.name));
  tbody.innerHTML = items.map((c) => `
    <tr class="selectable" data-id="${c.id}">
      <td>${c.name}</td>
      <td class="num">${formatPct(c.feePct)}</td>
      <td class="num">${formatBRL(c.feeFixed)}</td>
    </tr>
  `).join("") || `<tr><td colspan="3" class="hint">Nenhum canal cadastrado ainda.</td></tr>`;

  tbody.querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => selectChannelForEdit(Number(row.dataset.id)));
  });
}

function selectChannelForEdit(id) {
  const channel = Store.listChannels().find((c) => c.id === id);
  if (!channel) return;
  editingChannelId = id;
  $("chnName").value = channel.name;
  $("chnFeePct").value = channel.feePct * 100;
  $("chnFeeFixed").value = channel.feeFixed;
}

function clearChannelForm() {
  editingChannelId = null;
  $("chnName").value = "";
  $("chnFeePct").value = 0;
  $("chnFeeFixed").value = 0;
}

$("chnSaveBtn").addEventListener("click", () => {
  const name = $("chnName").value.trim();
  if (!name) return showToast("Informe o nome do canal.");
  Store.saveChannel({
    id: editingChannelId,
    name,
    feePct: num("chnFeePct") / 100,
    feeFixed: num("chnFeeFixed"),
  });
  clearChannelForm();
  renderChannelsTable();
  refreshLibraries();
  showToast("Canal salvo.");
});

$("chnNewBtn").addEventListener("click", clearChannelForm);

$("chnDeleteBtn").addEventListener("click", () => {
  if (editingChannelId == null) return;
  if (!confirm("Excluir este canal?")) return;
  Store.deleteChannel(editingChannelId);
  clearChannelForm();
  renderChannelsTable();
  refreshLibraries();
  showToast("Canal excluído.");
});

// =======================================================================
// CONFIGURAÇÕES
// =======================================================================
function loadSettingsForm() {
  const s = Store.loadSettings();
  $("setTariff").value = s.energyTariffKwh;
  $("setLaborRate").value = s.laborRateHour;
  $("setFailure").value = s.failureRatePct * 100;
  $("setTax").value = s.taxPct * 100;
  $("setGateway").value = s.paymentGatewayPct * 100;
  $("setMonthlyFixed").value = s.monthlyFixedCosts;
  $("setVolume").value = s.expectedMonthlyVolume;
  $("setPackagingDefault").value = s.packagingCostDefault;
  updateOverheadPreview();
}

function updateOverheadPreview() {
  const volume = Math.max(num("setVolume"), 1);
  const overhead = num("setMonthlyFixed") / volume;
  $("setOverheadPreview").value = `${formatBRL(overhead)} por peça`;
}

["setMonthlyFixed", "setVolume"].forEach((id) => $(id).addEventListener("input", updateOverheadPreview));

function currentSettings() {
  return {
    energyTariffKwh: num("setTariff"),
    laborRateHour: num("setLaborRate"),
    failureRatePct: num("setFailure") / 100,
    taxPct: num("setTax") / 100,
    paymentGatewayPct: num("setGateway") / 100,
    monthlyFixedCosts: num("setMonthlyFixed"),
    expectedMonthlyVolume: Math.max(num("setVolume"), 1),
    packagingCostDefault: num("setPackagingDefault"),
  };
}

$("settingsSaveBtn").addEventListener("click", () => {
  Store.saveSettings(currentSettings());
  showToast("Configurações salvas.");
});

// =======================================================================
// CALCULADORA
// =======================================================================
function refreshLibraries() {
  const materials = Store.listMaterials().sort((a, b) => a.name.localeCompare(b.name));
  const printers = Store.listPrinters().sort((a, b) => a.name.localeCompare(b.name));
  const channels = Store.listChannels().sort((a, b) => a.name.localeCompare(b.name));

  const printerSelect = $("printerSelect");
  const prevPrinter = printerSelect.value;
  printerSelect.innerHTML = printers.map((p) => `<option value="${p.id}">${p.name}</option>`).join("");
  if (printers.some((p) => String(p.id) === prevPrinter)) printerSelect.value = prevPrinter;

  const channelSelect = $("channelSelect");
  const prevChannel = channelSelect.value;
  channelSelect.innerHTML = channels.map((c) => `<option value="${c.id}">${c.name}</option>`).join("");
  if (channels.some((c) => String(c.id) === prevChannel)) channelSelect.value = prevChannel;

  document.querySelectorAll("#materialRows .row-material").forEach((select) => {
    const prev = select.value;
    select.innerHTML = materials.map((m) => `<option value="${m.id}">${m.name} (${m.unitLabel})</option>`).join("");
    if (materials.some((m) => String(m.id) === prev)) select.value = prev;
  });
}

function addMaterialRow() {
  const materials = Store.listMaterials().sort((a, b) => a.name.localeCompare(b.name));
  const row = document.createElement("div");
  row.className = "material-row";
  row.innerHTML = `
    <select class="row-material">${materials.map((m) => `<option value="${m.id}">${m.name} (${m.unitLabel})</option>`).join("")}</select>
    <input class="row-grams" type="number" min="0" step="0.01" value="0" placeholder="Peso (g)" />
    <button class="btn btn-danger" type="button">Remover</button>
  `;
  row.querySelector("button").addEventListener("click", () => row.remove());
  $("materialRows").appendChild(row);
}

$("addMaterialBtn").addEventListener("click", addMaterialRow);

function buildPieceFromForm() {
  const printerId = Number($("printerSelect").value);
  const printer = Store.listPrinters().find((p) => p.id === printerId);
  if (!printer) {
    showToast("Cadastre e selecione uma impressora na aba Impressoras.");
    return null;
  }

  const materials = Store.listMaterials();
  const usages = [];
  document.querySelectorAll("#materialRows .material-row").forEach((row) => {
    const materialId = Number(row.querySelector(".row-material").value);
    const grams = parseFloat(row.querySelector(".row-grams").value) || 0;
    const material = materials.find((m) => m.id === materialId);
    if (material && grams > 0) usages.push({ material, grams });
  });
  if (usages.length === 0) {
    showToast("Adicione ao menos um material com peso maior que zero.");
    return null;
  }

  const channelId = Number($("channelSelect").value);
  const channel = Store.listChannels().find((c) => c.id === channelId) || null;

  const failureOverride = num("failureOverride");
  const laborRateOverride = num("laborRateOverride");
  const gatewayOverride = num("gatewayOverride");
  const taxOverride = num("taxOverride");

  return {
    name: $("pieceName").value.trim() || "Peça sem nome",
    printer,
    printTimeHours: num("printTime"),
    materials: usages,
    wastePct: num("wastePct") / 100,
    labor: {
      modelingHours: num("laborModeling"),
      slicingHours: num("laborSlicing"),
      postProcessingHours: num("laborPost"),
      packagingHours: num("laborPackaging"),
    },
    laborRateHour: laborRateOverride || null,
    failureRatePct: failureOverride ? failureOverride / 100 : null,
    packagingCost: num("packagingCost"),
    shipping: {
      mode: $("shippingMode").value,
      shippingCost: num("shippingCost"),
      subsidizePct: num("shippingSubsidizePct") / 100,
    },
    saleChannel: channel,
    taxPct: taxOverride ? taxOverride / 100 : null,
    paymentGatewayPct: gatewayOverride ? gatewayOverride / 100 : null,
    overheadPerPiece: num("overheadOverride"),
  };
}

function buildDonutGradient(items) {
  const total = items.reduce((s, [, v]) => s + v, 0);
  if (total <= 0) return "conic-gradient(var(--border) 0% 100%)";
  let acc = 0;
  const stops = items.map(([label, value]) => {
    const pct = (value / total) * 100;
    const start = acc;
    acc += pct;
    return `${CHART_COLORS[label] || "#94a3b8"} ${start}% ${acc}%`;
  });
  return `conic-gradient(${stops.join(", ")})`;
}

function renderResult(result) {
  const { breakdown, scenarios, competitorAnalysis } = result;

  $("resultEmpty").style.display = "none";
  $("resultContent").style.display = "block";
  $("scenariosCard").style.display = "block";

  const items = breakdownChartItems(breakdown);
  $("donutChart").style.background = buildDonutGradient(items);
  $("donutTotal").textContent = formatBRL(breakdown.totalCost);

  const total = items.reduce((s, [, v]) => s + v, 0) || 1;
  $("chartLegend").innerHTML = items.map(([label, value]) => `
    <div class="legend-row">
      <span class="legend-name"><span class="swatch" style="background:${CHART_COLORS[label] || "#94a3b8"}"></span>${label}</span>
      <span class="legend-value">${formatBRL(value)} <span style="color:var(--text-muted)">(${((value / total) * 100).toFixed(1)}%)</span></span>
    </div>
  `).join("");

  const recommendedIdx = 1; // cenário de 50%
  $("pricingGrid").innerHTML = scenarios.map((s, idx) => {
    const mpInviavel = s.priceMarginOnPrice === Infinity;
    return `
    <div class="pricing-card ${idx === recommendedIdx ? "recommended" : ""}">
      ${idx === recommendedIdx ? '<span class="badge">Recomendado</span>' : ""}
      <div class="margin-label">Margem de ${s.label}</div>

      <div class="price-block">
        <div class="price-caption">Cost-plus (sobre o custo)</div>
        <div class="price-value">${formatBRL(s.priceCostPlus)}</div>
        <div class="price-profit ${s.netProfitCostPlus >= 0 ? "profit-positive" : "profit-negative"}">
          Lucro real: ${formatBRL(s.netProfitCostPlus)}
        </div>
      </div>

      <hr />

      <div class="price-block">
        <div class="price-caption">Margem sobre o preço final</div>
        <div class="price-value">${mpInviavel ? "Inviável" : formatBRL(s.priceMarginOnPrice)}</div>
        <div class="price-profit ${mpInviavel ? "" : (s.netProfitMarginOnPrice >= 0 ? "profit-positive" : "profit-negative")}">
          ${mpInviavel ? "Margem alta demais para as taxas configuradas" : `Lucro real: ${formatBRL(s.netProfitMarginOnPrice)}`}
        </div>
      </div>
    </div>
  `;
  }).join("");

  const competitorBox = $("competitorBox");
  if (competitorAnalysis) {
    const win = competitorAnalysis.netProfit >= 0;
    competitorBox.innerHTML = `
      <div class="result-box ${win ? "competitor-win" : "competitor-loss"}">
        Preço concorrente <strong>${formatBRL(competitorAnalysis.price)}</strong> →
        lucro real <strong>${formatBRL(competitorAnalysis.netProfit)}</strong>
        (${formatPct(competitorAnalysis.netMarginPct)} de margem líquida)
      </div>
    `;
  } else {
    competitorBox.innerHTML = "";
  }
}

$("calculateBtn").addEventListener("click", () => {
  const piece = buildPieceFromForm();
  if (!piece) return;
  const settings = Store.loadSettings();
  const competitorPrice = num("competitorPrice") || null;
  const result = computePricing(piece, settings, { competitorPrice });
  lastResult = result;
  lastPiece = piece;
  renderResult(result);
});

$("saveHistoryBtn").addEventListener("click", () => {
  if (!lastResult || !lastPiece) return showToast("Calcule a peça antes de salvar.");
  const weightG = lastPiece.materials.reduce((s, u) => s + u.grams, 0);
  const recommendedPrice = lastResult.scenarios[1] ? lastResult.scenarios[1].priceCostPlus : null;
  Store.saveHistoryEntry({
    name: lastPiece.name,
    printerId: lastPiece.printer.id,
    printerName: lastPiece.printer.name,
    printTimeHours: lastPiece.printTimeHours,
    weightG,
    materials: lastPiece.materials.map((u) => ({ name: u.material.name, grams: u.grams })),
    labor: lastPiece.labor,
    breakdown: lastResult.breakdown,
    finalPrice: recommendedPrice,
  });
  showToast("Peça salva no histórico.");
});

$("exportBtn").addEventListener("click", () => {
  if (!lastResult || !lastPiece) return showToast("Calcule a peça antes de exportar.");
  const { breakdown, scenarios } = lastResult;
  const rows = [
    ["Material", breakdown.materialCost],
    ["Energia", breakdown.energyCost],
    ["Depreciação", breakdown.depreciationCost],
    ["Manutenção", breakdown.maintenanceCost],
    ["Mão de obra", breakdown.laborCost],
    ["Overhead", breakdown.overheadCost],
    ["Embalagem", breakdown.packagingCost],
    ["Frete absorvido", breakdown.shippingAbsorbed],
  ];
  const rowsHtml = rows.map(([l, v]) => `<tr><td>${l}</td><td style="text-align:right">${formatBRL(v)}</td></tr>`).join("");
  const scenariosHtml = scenarios.map((s) => `
    <tr>
      <td>${s.label}</td>
      <td style="text-align:right">${formatBRL(s.priceCostPlus)}</td>
      <td style="text-align:right">${s.priceMarginOnPrice === Infinity ? "inviável" : formatBRL(s.priceMarginOnPrice)}</td>
    </tr>
  `).join("");

  $("printArea").innerHTML = `
    <h2>Orçamento — ${lastPiece.name}</h2>
    <p>Impressora: ${lastPiece.printer.name} | Tempo de impressão: ${lastPiece.printTimeHours.toFixed(2)} h</p>
    <table border="1" cellspacing="0" cellpadding="4" width="100%">
      <tr><th>Categoria</th><th>Valor</th></tr>
      ${rowsHtml}
      <tr><td><b>Custo total</b></td><td style="text-align:right"><b>${formatBRL(breakdown.totalCost)}</b></td></tr>
    </table>
    <h3>Cenários de preço sugeridos</h3>
    <table border="1" cellspacing="0" cellpadding="4" width="100%">
      <tr><th>Margem</th><th>Preço (cost-plus)</th><th>Preço (margem)</th></tr>
      ${scenariosHtml}
    </table>
    <p>PrintQuote by BMR — Orçamento gerado automaticamente.</p>
  `;
  window.print();
});

// =======================================================================
// HISTÓRICO
// =======================================================================
function renderHistoryTable() {
  const tbody = $("historyTableBody");
  const items = Store.listHistory();
  tbody.innerHTML = items.map((h) => `
    <tr class="selectable" data-id="${h.id}">
      <td>${new Date(h.createdAt).toLocaleString("pt-BR")}</td>
      <td>${h.name}</td>
      <td class="num">${h.weightG.toFixed(1)}</td>
      <td class="num">${h.printTimeHours.toFixed(2)}</td>
      <td class="num">${h.finalPrice ? formatBRL(h.finalPrice) : "-"}</td>
    </tr>
  `).join("") || `<tr><td colspan="5" class="hint">Nenhuma peça salva ainda.</td></tr>`;

  tbody.querySelectorAll("tr[data-id]").forEach((row) => {
    row.addEventListener("click", () => selectHistoryEntry(Number(row.dataset.id)));
  });
}

function selectHistoryEntry(id) {
  const entry = Store.listHistory().find((h) => h.id === id);
  if (!entry) return;
  selectedHistoryId = id;
  const lines = [];
  lines.push(`<strong>${entry.name}</strong>`);
  lines.push(`<span class="hint">Criada em ${new Date(entry.createdAt).toLocaleString("pt-BR")}</span>`);
  lines.push("<p><b>Materiais:</b><br>" + entry.materials.map((m) => `— ${m.name}: ${m.grams} g`).join("<br>") + "</p>");
  lines.push("<p><b>Breakdown de custos:</b><br>" + Object.entries(entry.breakdown).map(([k, v]) => `${k}: ${formatBRL(v)}`).join("<br>") + "</p>");
  $("historyDetail").innerHTML = lines.join("");
  $("historyDeleteBtn").style.display = "inline-block";
}

$("historyDeleteBtn").addEventListener("click", () => {
  if (selectedHistoryId == null) return;
  if (!confirm("Excluir esta peça do histórico?")) return;
  Store.deleteHistoryEntry(selectedHistoryId);
  selectedHistoryId = null;
  $("historyDetail").innerHTML = "Selecione uma peça na lista.";
  $("historyDeleteBtn").style.display = "none";
  renderHistoryTable();
  showToast("Peça excluída do histórico.");
});

// =======================================================================
// Boot
// =======================================================================
Store.seedIfEmpty();
renderMaterialsTable();
renderPrintersTable();
renderChannelsTable();
loadSettingsForm();
refreshLibraries();
addMaterialRow();
renderHistoryTable();
