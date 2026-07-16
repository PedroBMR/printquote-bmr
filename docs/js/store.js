/**
 * Camada de dados do PrintQuote by BMR (versão web): localStorage no
 * lugar do SQLite da versão desktop, mas os mesmos dados padrão (preços
 * 3D Lab, tarifa Copel/PR, impostos MEI) e o mesmo formato de registro.
 */

const LS_KEYS = {
  materials: "pq_materials",
  printers: "pq_printers",
  channels: "pq_channels",
  settings: "pq_settings",
  history: "pq_history",
  seeded: "pq_seeded_v1",
};

function _load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    console.error("Falha ao ler localStorage", key, e);
    return fallback;
  }
}

function _save(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function _nextId(items) {
  return items.reduce((max, item) => Math.max(max, item.id), 0) + 1;
}

// ---------------------------------------------------------------------
// Materiais
// ---------------------------------------------------------------------
const Store = {
  listMaterials() {
    return _load(LS_KEYS.materials, []);
  },
  saveMaterial(material) {
    const items = this.listMaterials();
    if (material.id == null) {
      material.id = _nextId(items);
      items.push(material);
    } else {
      const idx = items.findIndex((m) => m.id === material.id);
      if (idx >= 0) items[idx] = material;
      else items.push(material);
    }
    _save(LS_KEYS.materials, items);
    return material;
  },
  deleteMaterial(id) {
    _save(LS_KEYS.materials, this.listMaterials().filter((m) => m.id !== id));
  },

  // ---------------------------------------------------------------------
  // Impressoras
  // ---------------------------------------------------------------------
  listPrinters() {
    return _load(LS_KEYS.printers, []);
  },
  savePrinter(printer) {
    const items = this.listPrinters();
    if (printer.id == null) {
      printer.id = _nextId(items);
      items.push(printer);
    } else {
      const idx = items.findIndex((p) => p.id === printer.id);
      if (idx >= 0) items[idx] = printer;
      else items.push(printer);
    }
    _save(LS_KEYS.printers, items);
    return printer;
  },
  deletePrinter(id) {
    _save(LS_KEYS.printers, this.listPrinters().filter((p) => p.id !== id));
  },

  // ---------------------------------------------------------------------
  // Canais de venda
  // ---------------------------------------------------------------------
  listChannels() {
    return _load(LS_KEYS.channels, []);
  },
  saveChannel(channel) {
    const items = this.listChannels();
    if (channel.id == null) {
      channel.id = _nextId(items);
      items.push(channel);
    } else {
      const idx = items.findIndex((c) => c.id === channel.id);
      if (idx >= 0) items[idx] = channel;
      else items.push(channel);
    }
    _save(LS_KEYS.channels, items);
    return channel;
  },
  deleteChannel(id) {
    _save(LS_KEYS.channels, this.listChannels().filter((c) => c.id !== id));
  },

  // ---------------------------------------------------------------------
  // Configurações globais
  // ---------------------------------------------------------------------
  loadSettings() {
    return _load(LS_KEYS.settings, defaultSettings());
  },
  saveSettings(settings) {
    _save(LS_KEYS.settings, settings);
  },

  // ---------------------------------------------------------------------
  // Histórico de peças
  // ---------------------------------------------------------------------
  listHistory() {
    return _load(LS_KEYS.history, []).sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
  },
  saveHistoryEntry(entry) {
    const items = _load(LS_KEYS.history, []);
    entry.id = _nextId(items);
    entry.createdAt = new Date().toISOString();
    items.push(entry);
    _save(LS_KEYS.history, items);
    return entry;
  },
  deleteHistoryEntry(id) {
    _save(LS_KEYS.history, _load(LS_KEYS.history, []).filter((h) => h.id !== id));
  },

  seedIfEmpty() {
    if (localStorage.getItem(LS_KEYS.seeded)) return;
    if (this.listMaterials().length === 0) {
      defaultMaterials().forEach((m) => this.saveMaterial(m));
    }
    if (this.listPrinters().length === 0) {
      defaultPrinters().forEach((p) => this.savePrinter(p));
    }
    if (this.listChannels().length === 0) {
      defaultChannels().forEach((c) => this.saveChannel(c));
    }
    if (!localStorage.getItem(LS_KEYS.settings)) {
      this.saveSettings(defaultSettings());
    }
    localStorage.setItem(LS_KEYS.seeded, "1");
  },
};

// ---------------------------------------------------------------------
// Defaults — mesmos valores da versão desktop (calc3d/data/defaults.py)
// ---------------------------------------------------------------------
function defaultSettings() {
  return {
    energyTariffKwh: 0.76, // Copel B1 residencial, Pato Branco/PR (c/ impostos)
    laborRateHour: 25.0,
    failureRatePct: 0.10,
    taxPct: 0.06, // MEI
    paymentGatewayPct: 0.0,
    monthlyFixedCosts: 0.0,
    expectedMonthlyVolume: 1,
    packagingCostDefault: 0.0,
  };
}

function defaultMaterials() {
  const note3dlab = "Preço cheio (sem desconto Pix) — 3dlab.com.br";
  return [
    { id: null, name: "PLA Premium (3D Lab)", materialType: "filamento", pricePerKg: 99.89, unitLabel: "kg", notes: note3dlab },
    { id: null, name: "PLA Silk (3D Lab)", materialType: "filamento", pricePerKg: 128.90, unitLabel: "kg", notes: note3dlab },
    { id: null, name: "PETG Premium (3D Lab)", materialType: "filamento", pricePerKg: 119.87, unitLabel: "kg", notes: note3dlab },
    { id: null, name: "PETG Low Cost (3D Lab)", materialType: "filamento", pricePerKg: 72.73, unitLabel: "kg", notes: note3dlab },
    { id: null, name: "ABS Premium (3D Lab)", materialType: "filamento", pricePerKg: 97.67, unitLabel: "kg", notes: note3dlab },
    { id: null, name: "ABS Natural Engineering (3D Lab)", materialType: "filamento", pricePerKg: 88.76, unitLabel: "kg", notes: note3dlab },
    { id: null, name: "ASA", materialType: "filamento", pricePerKg: 130.0, unitLabel: "kg", notes: "Preço médio de mercado BR (estimativa)" },
    { id: null, name: "TPU", materialType: "filamento", pricePerKg: 150.0, unitLabel: "kg", notes: "Preço médio de mercado BR (estimativa)" },
    { id: null, name: "Resina Padrão", materialType: "resina", pricePerKg: 200.0, unitLabel: "L", notes: "Preço por litro, densidade ~1g/mL (estimativa)" },
    { id: null, name: "Resina Tough/ABS-like", materialType: "resina", pricePerKg: 280.0, unitLabel: "L", notes: "Preço por litro (estimativa)" },
  ];
}

function defaultPrinters() {
  return [
    { id: null, name: "Ender 3 S1", purchasePrice: 2200.0, lifetimeHours: 6000, wattsAvg: 120.0, maintenanceCostPerHour: 0.15, notes: "FDM doméstica" },
    { id: null, name: "Bambu Lab A1 + AMS Lite", purchasePrice: 4200.0, lifetimeHours: 6000, wattsAvg: 100.0, maintenanceCostPerHour: 0.20, notes: "FDM multi-cor" },
    { id: null, name: "P1S (P1P modificada)", purchasePrice: 5500.0, lifetimeHours: 8000, wattsAvg: 140.0, maintenanceCostPerHour: 0.30, notes: "Uso profissional, câmara fechada" },
  ];
}

function defaultChannels() {
  return [
    { id: null, name: "Venda direta (sem taxa)", feePct: 0.0, feeFixed: 0.0 },
    { id: null, name: "Mercado Livre (Clássico)", feePct: 0.12, feeFixed: 6.0 },
    { id: null, name: "Shopee", feePct: 0.14, feeFixed: 4.0 },
    { id: null, name: "Etsy", feePct: 0.065, feeFixed: 0.20 },
    { id: null, name: "Elo7", feePct: 0.12, feeFixed: 1.0 },
  ];
}
