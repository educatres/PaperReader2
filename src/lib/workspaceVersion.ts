import type { Workspace } from '../types';

// Database records have already crossed the import validator. Keep every legacy field.
export function upgradeWorkspace(value: Workspace | Record<string, unknown>): Workspace {
  if (value.schemaVersion === 1) return { ...value, schemaVersion: 3, pdfLayouts: [], pdfParagraphs: [], pdfTranslations: [], pdfTranslationJobs: [], inkStrokes: [] } as Workspace;
  if (value.schemaVersion === 2) return { ...value, schemaVersion: 3, inkStrokes: [] } as Workspace;
  if (value.schemaVersion !== 3) throw new Error('研究資料版本較新，請更新 PaperReader。');
  return { ...value, inkStrokes: Array.isArray(value.inkStrokes) ? value.inkStrokes : [] } as Workspace;
}
