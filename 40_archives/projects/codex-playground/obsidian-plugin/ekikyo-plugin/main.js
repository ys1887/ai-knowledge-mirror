"use strict";

const fs = require("fs");
const path = require("path");
const { ButtonComponent, Modal, Notice, Plugin } = require("obsidian");

const MODES = {
  SIMPLE: "SIMPLE",
  SIMPLE2: "SIMPLE2",
  EX5_LIST: "EX5-LIST",
};

const CHANGING_LINE_RE = /^[1-6]$/;

module.exports = class EkikyoPlugin extends Plugin {
  async onload() {
    this.dataset = loadQuoteDataset(this.app, this.manifest.id);

    this.addCommand({
      id: "copy-simple-source-output",
      name: "I Ching: 略筮法",
      callback: () => {
        new ModeInputModal(this.app, MODES.SIMPLE, async (mode, rawText) => {
          return this.copyModeOutput(mode, rawText);
        }).open();
      },
    });

    this.addCommand({
      id: "copy-simple2-source-output",
      name: "I Ching: 中筮法",
      callback: () => {
        new ModeInputModal(this.app, MODES.SIMPLE2, async (mode, rawText) => {
          return this.copyModeOutput(mode, rawText);
        }).open();
      },
    });

    this.addCommand({
      id: "copy-ex5-list-source-output",
      name: "I Ching: 5卦",
      callback: () => {
        new ModeInputModal(this.app, MODES.EX5_LIST, async (mode, rawText) => {
          return this.copyModeOutput(mode, rawText);
        }).open();
      },
    });
  }

  async copyModeOutput(mode, rawText) {
    try {
      if (mode === MODES.SIMPLE) {
        const parsed = parseBinaryInput(rawText);
        const resolved = resolveHexagram(parsed.binary, parsed.changingLine, this.dataset);
        copyToClipboard(buildSimpleOutput(resolved));
        new Notice(`Copied ${formatHexagramLabel(resolved.hexagramNumber, resolved.hexagramName)} / ${resolved.takashima.lineHeading}`);
        return true;
      }

      if (mode === MODES.SIMPLE2) {
        const parsed = parseBinaryInputMultiple(rawText);
        const resolved = resolveHexagramWithZhiGua(parsed.binary, parsed.changingLines, this.dataset);
        copyToClipboard(buildSimple2Output(resolved));
        new Notice(formatSimple2Notice(resolved));
        return true;
      }

      if (mode === MODES.EX5_LIST) {
        const parsed = parseBinaryInputMultiple(rawText);
        const resolved = resolveHexagramSummary(parsed.binary, parsed.changingLines, this.dataset);
        const output = buildEx5Output(resolved);
        copyToClipboard(output);
        new Notice(output);
        return true;
      }

      throw new Error(`Unknown mode: ${mode}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      new Notice(message, 6000);
      return false;
    }
  }
};

class ModeInputModal extends Modal {
  constructor(app, defaultMode, onSubmit) {
    super(app);
    this.defaultMode = defaultMode;
    this.onSubmit = onSubmit;
    this.textarea = null;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();

    contentEl.createEl("h2", { text: "Ekikyo Input" });
    const body = contentEl.createDiv({ cls: "ekikyo-input-body" });
    body.style.display = "grid";
    body.style.gridTemplateColumns = "minmax(0, 1fr) 180px";
    body.style.gap = "16px";
    body.style.alignItems = "start";

    const leftPane = body.createDiv({ cls: "ekikyo-input-left-pane" });

    this.textarea = leftPane.createEl("textarea", {
      cls: "ekikyo-input-textarea",
    });
    this.textarea.rows = 4;
    this.textarea.placeholder = "111111\n2";

    this.textarea.addEventListener("keydown", async (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        await this.submit(this.defaultMode);
      }
    });

    const rightPane = body.createDiv({ cls: "ekikyo-input-actions" });
    rightPane.style.display = "flex";
    rightPane.style.flexDirection = "column";
    rightPane.style.gap = "8px";

    rightPane.createEl("div", {
      text: "Mode",
      cls: "ekikyo-input-actions-title",
    });

    const createModeButton = (label, mode) => {
      const button = new ButtonComponent(rightPane).setButtonText(label);
      if (this.defaultMode === mode) {
        button.setCta();
      }
      button.onClick(async () => {
        await this.submit(mode);
      });
    };

    createModeButton("略筮法", MODES.SIMPLE);
    createModeButton("中筮法", MODES.SIMPLE2);
    createModeButton("5卦", MODES.EX5_LIST);

    this.textarea.focus();
  }

  async submit(mode) {
    if (!this.textarea) {
      return;
    }
    const shouldClose = await this.onSubmit(mode, this.textarea.value);
    if (shouldClose !== false) {
      this.close();
    }
  }
}

function loadQuoteDataset(app, pluginId) {
  const vaultBasePath = app.vault.adapter.basePath;
  if (!vaultBasePath) {
    throw new Error("Vault base path を取得できません。");
  }

  const datasetPath = path.join(
    vaultBasePath,
    app.vault.configDir,
    "plugins",
    pluginId,
    "data",
    "quote-dataset.json",
  );

  const rawDataset = JSON.parse(fs.readFileSync(datasetPath, "utf8"));
  const byBinary = new Map();
  const byNumber = new Map();

  for (const hexagram of rawDataset.hexagrams) {
    byBinary.set(hexagram.binary, hexagram);
    byNumber.set(hexagram.number, hexagram);
  }

  return {
    hexagrams: rawDataset.hexagrams,
    byBinary,
    byNumber,
  };
}

function normalizeBinary(binary) {
  return String(binary || "").trim();
}

function validateBinary(binary) {
  const normalized = normalizeBinary(binary);
  if (normalized.length !== 6) {
    throw new Error("本卦の2進数表記は6桁で入力してください。");
  }
  if (!/^[01]{6}$/.test(normalized)) {
    throw new Error("本卦の2進数表記は0と1のみで入力してください。");
  }
  return normalized;
}

function validateChangingLine(value) {
  const normalized = String(value || "").trim();
  if (!CHANGING_LINE_RE.test(normalized)) {
    throw new Error("変爻は半角数字の1から6で入力してください。");
  }
  return Number(normalized);
}

function validateChangingLines(value, options = {}) {
  const tokens = Array.isArray(value)
    ? value.map((line) => String(line).trim())
    : String(value || "").trim().split(/\s+/);
  const normalizedTokens = tokens.filter((token) => token.length > 0);

  if (normalizedTokens.length === 0) {
    if (Array.isArray(value) && options.allowZero) {
      return [];
    }
    throw new Error("変爻は半角数字の0から6で入力してください。");
  }

  if (normalizedTokens.includes("0")) {
    if (options.allowZero && normalizedTokens.length === 1) {
      return [];
    }
    throw new Error("変爻0は単独で入力してください。");
  }

  const lines = normalizedTokens.map((token) => validateChangingLine(token));
  const uniqueLines = new Set(lines);
  if (uniqueLines.size !== lines.length) {
    throw new Error("変爻は重複しないように入力してください。");
  }

  return lines;
}

function parseBinaryInput(rawText) {
  const lines = String(rawText || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  if (lines.length < 2) {
    throw new Error("入力は2行必要です。1行目に本卦、2行目に変爻を入力してください。");
  }

  return {
    binary: validateBinary(lines[0]),
    changingLine: validateChangingLine(lines[1]),
  };
}

function parseBinaryInputMultiple(rawText) {
  const lines = String(rawText || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  if (lines.length < 2) {
    throw new Error("入力は2行必要です。1行目に本卦、2行目に変爻を入力してください。");
  }

  return {
    binary: validateBinary(lines[0]),
    changingLines: validateChangingLines(lines[1], { allowZero: true }),
  };
}

function resolveHexagram(binary, changingLine, dataset) {
  const normalizedBinary = validateBinary(binary);
  const validatedLine = validateChangingLine(changingLine);
  const hexagram = dataset.byBinary.get(normalizedBinary);

  if (!hexagram) {
    throw new Error("対応する本卦が見つかりません。");
  }

  const takashimaLine = hexagram.takashima && hexagram.takashima.lines
    ? hexagram.takashima.lines[String(validatedLine)]
    : null;
  if (!hexagram.takashima || !takashimaLine) {
    throw new Error("対応する高島易断ブロックが見つかりません。");
  }

  const bodyExcerptLine = hexagram.bodyExcerpt && hexagram.bodyExcerpt.lines
    ? hexagram.bodyExcerpt.lines[String(validatedLine)]
    : null;

  return {
    binary: normalizedBinary,
    changingLine: validatedLine,
    hexagramNumber: hexagram.number,
    hexagramName: hexagram.name,
    bodyExcerpt: {
      honka: hexagram.bodyExcerpt ? hexagram.bodyExcerpt.honka || "" : "",
      line: bodyExcerptLine || "",
    },
    takashima: {
      kaji: hexagram.takashima.kaji,
      tanden: hexagram.takashima.tanden,
      taisho: hexagram.takashima.taisho,
      lineHeading: takashimaLine.heading,
      lineText: takashimaLine.text,
    },
    referenceCaseExcerpt: hexagram.referenceCases
      ? hexagram.referenceCases[String(validatedLine)] || ""
      : "",
  };
}

function resolveHexagramWithZhiGua(binary, changingLines, dataset) {
  const normalizedBinary = validateBinary(binary);
  const validatedLines = validateChangingLines(changingLines, { allowZero: true });

  if (validatedLines.length === 1) {
    const resolved = resolveHexagram(normalizedBinary, validatedLines[0], dataset);
    return {
      ...resolved,
      changingLines: validatedLines,
      zhiHexagram: getHexagramByBinary(
        dataset,
        calculateZhiGua(resolved.binary, validatedLines),
        "対応する之卦が見つかりません。",
      ),
    };
  }

  const hexagram = getHexagramByBinary(dataset, normalizedBinary, "対応する本卦が見つかりません。");
  const zhiHexagram = validatedLines.length > 0
    ? getHexagramByBinary(
      dataset,
      calculateZhiGua(normalizedBinary, validatedLines),
      "対応する之卦が見つかりません。",
    )
    : null;

  return {
    binary: normalizedBinary,
    changingLines: validatedLines,
    hexagramNumber: hexagram.number,
    hexagramName: hexagram.name,
    bodyExcerpt: {
      honka: hexagram.bodyExcerpt ? hexagram.bodyExcerpt.honka || "" : "",
    },
    takashima: {
      kaji: hexagram.takashima.kaji,
      tanden: hexagram.takashima.tanden,
      taisho: hexagram.takashima.taisho,
    },
    zhiHexagram,
  };
}

function resolveHexagramSummary(binary, changingLines, dataset) {
  const normalizedBinary = validateBinary(binary);
  const validatedLines = validateChangingLines(changingLines, { allowZero: true });
  const mainHexagram = getHexagramByBinary(dataset, normalizedBinary, "対応する本卦が見つかりません。");
  const zhiHexagram = validatedLines.length > 0
    ? getHexagramByBinary(
      dataset,
      calculateZhiGua(normalizedBinary, validatedLines),
      "対応する之卦が見つかりません。",
    )
    : null;
  const huHexagram = getHexagramByBinary(
    dataset,
    calculateHuGua(normalizedBinary),
    "対応する互卦が見つかりません。",
  );
  const cuoHexagram = getHexagramByBinary(
    dataset,
    calculateCuoGua(normalizedBinary),
    "対応する錯卦が見つかりません。",
  );
  const zongHexagram = getHexagramByBinary(
    dataset,
    calculateZongGua(normalizedBinary),
    "対応する綜卦が見つかりません。",
  );

  return {
    binary: normalizedBinary,
    changingLines: validatedLines,
    mainHexagram,
    zhiHexagram,
    huHexagram,
    cuoHexagram,
    zongHexagram,
  };
}

function buildSimpleOutput(resolved) {
  if (!resolved.bodyExcerpt.honka.trim() || !resolved.bodyExcerpt.line.trim()) {
    throw new Error("対応する本文抜粋ブロックが見つかりません。");
  }

  const lines = [
    ...buildSimpleHonkaSection(
      resolved.hexagramName,
      resolved.bodyExcerpt.honka,
      resolved.takashima,
    ),
    ...buildSimpleChangingLineSection(
      resolved.takashima.lineHeading,
      resolved.bodyExcerpt.line,
      resolved.takashima.lineText,
    ),
  ];

  if (resolved.referenceCaseExcerpt && resolved.referenceCaseExcerpt.trim()) {
    lines.push("## 占例抜粋", "", resolved.referenceCaseExcerpt.trim(), "");
  }

  return lines.join("\n");
}

function buildSimple2Output(resolved) {
  const lines = [
    ...buildSimpleHonkaSection(
      resolved.hexagramName,
      resolved.bodyExcerpt.honka,
      resolved.takashima,
    ),
  ];

  if (resolved.changingLines.length === 1) {
    lines.push(
      ...buildSimpleChangingLineSection(
        resolved.takashima.lineHeading,
        resolved.bodyExcerpt.line,
        resolved.takashima.lineText,
      ),
    );
  }

  if (resolved.zhiHexagram) {
    lines.push(
      ...buildSimpleHonkaSection(
        resolved.zhiHexagram.name,
        resolved.zhiHexagram.bodyExcerpt.honka,
        resolved.zhiHexagram.takashima,
      ),
    );
  }

  if (resolved.referenceCaseExcerpt && resolved.referenceCaseExcerpt.trim()) {
    lines.push("## 占例抜粋", "", resolved.referenceCaseExcerpt.trim(), "");
  }

  return lines.join("\n");
}

function buildSimpleHonkaSection(hexagramName, bodyExcerptHonka, takashima) {
  return [
    `## ${hexagramName}`,
    "",
    bodyExcerptHonka.trim(),
    "",
    "#### 卦辞",
    "",
    takashima.kaji.trim(),
    "",
    "#### 彖伝",
    "",
    takashima.tanden.trim(),
    "",
    "#### 大象伝",
    "",
    takashima.taisho.trim(),
    "",
  ];
}

function buildSimpleChangingLineSection(lineHeading, bodyExcerptLine, lineText) {
  return [
    `## ${lineHeading}`,
    "",
    bodyExcerptLine.trim(),
    "",
    `### 爻辞と小象伝（${lineHeading}）`,
    "",
    lineText.trim(),
    "",
  ];
}

function buildEx5Output(resolved) {
  const rows = [
    ["本卦", formatHexagramLabel(resolved.mainHexagram.number, resolved.mainHexagram.name)],
  ];

  if (resolved.changingLines.length > 0) {
    rows.push(
      ["変爻", formatChangingLinesLabel(resolved.changingLines)],
      ["之卦", formatHexagramLabel(resolved.zhiHexagram.number, resolved.zhiHexagram.name)],
    );
  }

  rows.push(
    ["互卦", formatHexagramLabel(resolved.huHexagram.number, resolved.huHexagram.name)],
    ["錯卦", formatHexagramLabel(resolved.cuoHexagram.number, resolved.cuoHexagram.name)],
    ["綜卦", formatHexagramLabel(resolved.zongHexagram.number, resolved.zongHexagram.name)],
  );

  return buildSummaryOutput(rows);
}

function buildSummaryOutput(rows) {
  return rows.map(([label, value]) => `${label}：${value}`).join("\n");
}

function formatHexagramLabel(number, name) {
  return `${number}.${name}`;
}

function formatChangingLinesLabel(changingLines) {
  return changingLines.length > 0 ? changingLines.join(" ") : "なし";
}

function formatSimple2Notice(resolved) {
  const baseLabel = formatHexagramLabel(resolved.hexagramNumber, resolved.hexagramName);
  if (resolved.changingLines.length === 1) {
    return `Copied ${baseLabel} / ${resolved.takashima.lineHeading}`;
  }
  return `Copied ${baseLabel} / 変爻${formatChangingLinesLabel(resolved.changingLines)}`;
}

function getHexagramByBinary(dataset, binary, errorMessage) {
  const hexagram = dataset.byBinary.get(binary);
  if (!hexagram) {
    throw new Error(errorMessage);
  }
  return hexagram;
}

function calculateZhiGua(binary, changingLines) {
  const digits = validateBinary(binary).split("");
  for (const line of changingLines) {
    const index = line - 1;
    digits[index] = digits[index] === "0" ? "1" : "0";
  }
  return digits.join("");
}

function calculateHuGua(binary) {
  const normalized = validateBinary(binary);
  return normalized.slice(1, 4) + normalized.slice(2, 5);
}

function calculateCuoGua(binary) {
  return validateBinary(binary)
    .split("")
    .map((digit) => (digit === "0" ? "1" : "0"))
    .join("");
}

function calculateZongGua(binary) {
  const normalized = validateBinary(binary);
  const reversed = normalized.split("").reverse().join("");
  return normalized === reversed ? normalized : reversed;
}

function copyToClipboard(text) {
  try {
    const { clipboard } = require("electron");
    clipboard.writeText(text);
    return;
  } catch (error) {
    if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text);
      return;
    }
    throw new Error("クリップボードへコピーできませんでした。");
  }
}
