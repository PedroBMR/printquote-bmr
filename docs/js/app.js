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

// ----- Backup / restauração -----
function downloadJson(filename, obj) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

$("exportDataBtn").addEventListener("click", () => {
  const stamp = new Date().toISOString().slice(0, 10);
  downloadJson(`printquote-backup-${stamp}.json`, Store.exportAll());
  showToast("Backup exportado.");
});

$("importDataBtn").addEventListener("click", () => $("importDataInput").click());

$("importDataInput").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const input = e.target;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      if (!confirm("Importar vai SUBSTITUIR os dados atuais deste navegador (materiais, impressoras, canais, configurações e histórico). Continuar?")) {
        return;
      }
      Store.importAll(data);
      renderMaterialsTable();
      renderPrintersTable();
      renderChannelsTable();
      loadSettingsForm();
      refreshLibraries();
      renderHistoryTable();
      showToast("Dados importados.");
    } catch (err) {
      console.error("Falha ao importar backup", err);
      showToast(`Não foi possível importar: ${err.message || "arquivo inválido"}.`);
    } finally {
      input.value = "";
    }
  };
  reader.onerror = () => {
    showToast("Não foi possível ler o arquivo.");
    input.value = "";
  };
  reader.readAsText(file);
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

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

$("exportBtn").addEventListener("click", () => {
  if (!lastResult || !lastPiece) return showToast("Calcule a peça antes de exportar.");
  const { breakdown, scenarios } = lastResult;

  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const quoteNo = `PQ-${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}`;
  const dateStr = now.toLocaleDateString("pt-BR");
  const dateTimeStr = now.toLocaleString("pt-BR");

  const validityDays = Math.max(parseInt($("quoteValidity").value, 10) || 0, 0);
  let validityStr = "—";
  if (validityDays > 0) {
    const until = new Date(now.getTime() + validityDays * 86400000);
    validityStr = `${validityDays} dia(s) — até ${until.toLocaleDateString("pt-BR")}`;
  }

  const client = $("quoteClient").value.trim();
  const notes = $("quoteNotes").value.trim();
  const weightG = lastPiece.materials.reduce((s, u) => s + u.grams, 0);

  // cenário recomendado (50%) — mesmo índice usado na UI e no histórico
  const rec = scenarios[1] || scenarios[0];
  const recPrice = rec ? rec.priceCostPlus : breakdown.totalCost;
  const recLabel = rec ? rec.label : "—";

  const costRows = [
    ["Material", breakdown.materialCost],
    ["Energia", breakdown.energyCost],
    ["Depreciação da máquina", breakdown.depreciationCost],
    ["Manutenção", breakdown.maintenanceCost],
    ["Mão de obra", breakdown.laborCost],
    ["Overhead", breakdown.overheadCost],
    ["Embalagem", breakdown.packagingCost],
    ["Frete absorvido", breakdown.shippingAbsorbed],
  ].filter(([, v]) => v > 0.0001);
  const costRowsHtml = costRows.map(([l, v]) => `<tr><td>${l}</td><td class="q-num">${formatBRL(v)}</td></tr>`).join("");

  const scenariosHtml = scenarios.map((s) => `
    <tr${s === rec ? ' class="q-row-rec"' : ""}>
      <td>Margem de ${s.label}</td>
      <td class="q-num">${formatBRL(s.priceCostPlus)}</td>
      <td class="q-num">${s.priceMarginOnPrice === Infinity ? "inviável" : formatBRL(s.priceMarginOnPrice)}</td>
    </tr>
  `).join("");

  const materialsLine = lastPiece.materials.map((u) => `${escapeHtml(u.material.name)} (${u.grams} g)`).join(", ");

  $("printArea").innerHTML = `
    <div class="quote">
      <div class="q-head">
        <div class="q-brand">
          <img src="assets/icon-256.png" alt="" class="q-logo" />
          <div>
            <div class="q-brand-name">PrintQuote <span>by BMR</span></div>
            <div class="q-brand-sub">Orçamento de impressão 3D</div>
          </div>
        </div>
        <div class="q-meta">
          <div><span>Orçamento nº</span><strong>${quoteNo}</strong></div>
          <div><span>Data</span><strong>${dateStr}</strong></div>
          <div><span>Validade</span><strong>${validityStr}</strong></div>
        </div>
      </div>

      <div class="q-parties">
        <div class="q-party"><span>Cliente</span><strong>${client ? escapeHtml(client) : "—"}</strong></div>
        <div class="q-party"><span>Peça</span><strong>${escapeHtml(lastPiece.name)}</strong></div>
        <div class="q-party"><span>Impressora</span><strong>${escapeHtml(lastPiece.printer.name)}</strong></div>
        <div class="q-party"><span>Tempo de impressão</span><strong>${lastPiece.printTimeHours.toFixed(2)} h</strong></div>
        <div class="q-party"><span>Peso total</span><strong>${weightG.toFixed(1)} g</strong></div>
        <div class="q-party q-party-wide"><span>Materiais</span><strong>${materialsLine || "—"}</strong></div>
      </div>

      <div class="q-hero">
        <div class="q-hero-label">Preço sugerido</div>
        <div class="q-hero-price">${formatBRL(recPrice)}</div>
        <div class="q-hero-sub">Margem de ${recLabel} sobre o custo · custo total ${formatBRL(breakdown.totalCost)}</div>
      </div>

      <h3 class="q-h3">Composição do custo</h3>
      <table class="q-table">
        <thead><tr><th>Categoria</th><th class="q-num">Valor</th></tr></thead>
        <tbody>
          ${costRowsHtml}
          <tr class="q-total"><td>Custo total</td><td class="q-num">${formatBRL(breakdown.totalCost)}</td></tr>
        </tbody>
      </table>

      <h3 class="q-h3">Cenários de preço</h3>
      <table class="q-table">
        <thead><tr><th>Cenário</th><th class="q-num">Preço (cost-plus)</th><th class="q-num">Preço (margem s/ preço)</th></tr></thead>
        <tbody>${scenariosHtml}</tbody>
      </table>

      ${notes ? `<div class="q-notes"><span>Observações</span><p>${escapeHtml(notes).replace(/\n/g, "<br>")}</p></div>` : ""}

      <div class="q-foot">
        PrintQuote <strong>by BMR</strong> — orçamento gerado em ${dateTimeStr}. Valores em reais (BRL); preços sujeitos a alteração após a validade.
      </div>
    </div>
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
