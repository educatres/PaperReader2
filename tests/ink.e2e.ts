import { expect, test, type Page } from '@playwright/test';
import { openProject } from './projectHelpers';

async function draw(page: Page, from: { x: number; y: number }, to: { x: number; y: number }) {
  await page.mouse.move(from.x, from.y); await page.mouse.down(); await page.mouse.move(to.x, to.y, { steps: 10 }); await page.mouse.up();
}

test('handwriting colors, stroke eraser, marquee selection, grid and persistence work on the research board', async ({ page }) => {
  await openProject(page);
  const board = page.locator('.research-canvas'); const box = (await board.boundingBox())!;
  const a = { x: box.x + box.width * .35, y: box.y + box.height * .35 };
  const b = { x: a.x + 100, y: a.y + 35 };
  const c = { x: a.x + 20, y: a.y + 80 };
  const d = { x: b.x + 20, y: b.y + 80 };

  await page.getByRole('button', { name: '手寫畫筆' }).click();
  await page.getByRole('button', { name: '藍色畫筆' }).click();
  await draw(page, a, b); await draw(page, c, d);
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);
  await expect(page.locator('.ink-stroke').first()).toHaveAttribute('stroke', '#316ba0');

  await page.getByRole('button', { name: '整筆橡皮擦' }).click(); await page.mouse.click(a.x + 50, a.y + 18);
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(1);
  await page.getByRole('button', { name: '復原', exact: true }).click();
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);

  await page.getByRole('button', { name: '框選多筆畫' }).click();
  await draw(page, { x: a.x - 20, y: a.y - 20 }, { x: d.x + 20, y: d.y + 20 });
  await expect(page.locator('.ink-selection')).toHaveCount(2);
  const beforeMove = await page.locator('.ink-stroke').first().getAttribute('d');
  await draw(page, { x: a.x + 50, y: a.y + 18 }, { x: a.x + 90, y: a.y + 38 });
  await expect.poll(() => page.locator('.ink-stroke').first().getAttribute('d')).not.toBe(beforeMove);
  await page.keyboard.press('Delete'); await expect(page.locator('[data-ink-stroke]')).toHaveCount(0);
  await page.getByRole('button', { name: '復原', exact: true }).click();
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);

  await page.getByRole('button', { name: '開啟淡色格線' }).click();
  await expect(page.getByRole('button', { name: '關閉淡色格線' })).toHaveClass(/active/);
  await page.getByRole('button', { name: '開啟淡色橫線' }).click();
  await expect(page.getByRole('button', { name: '關閉淡色橫線' })).toHaveClass(/active/);
  await expect(page.getByRole('button', { name: '開啟淡色格線' })).not.toHaveClass(/active/);
  await expect(page.getByTestId('ruled-background')).toBeVisible();
  await page.waitForTimeout(350); await page.reload();
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);
  await expect(page.getByRole('button', { name: '關閉淡色橫線' })).toHaveClass(/active/);
  await expect(page.getByTestId('ruled-background')).toBeVisible();
});
