import { expect, test, type Page } from '@playwright/test';
import { openProject } from './projectHelpers';

async function draw(page: Page, from: { x: number; y: number }, to: { x: number; y: number }) {
  await page.mouse.move(from.x, from.y); await page.mouse.down(); await page.mouse.move(to.x, to.y, { steps: 10 }); await page.mouse.up();
}

test('smooth handwriting, colors, stroke eraser, marquee selection, grid and persistence work on the research board', async ({ page }) => {
  await openProject(page);
  const board = page.locator('.research-canvas'); const box = (await board.boundingBox())!;
  const a = { x: box.x + box.width * .35, y: box.y + box.height * .35 };
  const b = { x: a.x + 100, y: a.y + 35 };
  const c = { x: a.x + 20, y: a.y + 80 };
  const d = { x: b.x + 20, y: b.y + 80 };

  await page.getByRole('button', { name: '手寫畫筆' }).click();
  await expect(board).toHaveCSS('cursor', /data:image\/svg\+xml/);
  await page.getByRole('button', { name: '深藍畫筆' }).click();
  await draw(page, a, b); await draw(page, c, d);
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);
  await expect(page.locator('.ink-stroke').first()).toHaveAttribute('stroke', 'var(--brush-blue)');

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
  await page.waitForTimeout(350); await page.reload();
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);
  await expect(page.getByRole('button', { name: '關閉淡色格線' })).toHaveClass(/active/);
  await expect(page.getByRole('button', { name: /淡色橫線/ })).toHaveCount(0);
});

test('pen detection keeps stylus drawing while routing touch to canvas panning', async ({ page }) => {
  const client = await page.context().newCDPSession(page);
  await client.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  await openProject(page);
  const board = page.locator('.research-canvas'); const box = (await board.boundingBox())!;
  const start = { x: Math.round(box.x + box.width * .35), y: Math.round(box.y + box.height * .4) };
  const end = { x: start.x + 90, y: start.y + 35 };

  await page.getByRole('button', { name: '手寫畫筆' }).click();
  await expect(board).toHaveAttribute('data-pen-detected', 'false');
  await expect(page.locator('.canvas-hint')).toContainText('手指也可書寫');

  await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ ...start, id: 1, radiusX: 2, radiusY: 2, force: .5 }] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ ...end, id: 1, radiusX: 2, radiusY: 2, force: .5 }] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await expect(page.locator('[data-ink-stroke]')).toHaveCount(1);

  const penStart = { x: start.x, y: start.y + 80 }; const penEnd = { x: end.x, y: end.y + 80 };
  await client.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: penStart.x, y: penStart.y, button: 'left', buttons: 1, pointerType: 'pen', force: .55 });
  await client.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: penEnd.x, y: penEnd.y, button: 'left', buttons: 1, pointerType: 'pen', force: .7 });
  await client.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: penEnd.x, y: penEnd.y, button: 'left', buttons: 0, pointerType: 'pen', force: 0 });

  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);
  await expect(board).toHaveAttribute('data-pen-detected', 'true');
  await expect(page.locator('.canvas-hint')).toContainText('手指拖動畫布');

  const viewport = page.locator('.react-flow__viewport'); const before = await viewport.getAttribute('style');
  const touchStart = { x: Math.round(box.x + box.width * .62), y: Math.round(box.y + box.height * .62) };
  const touchEnd = { x: touchStart.x + 80, y: touchStart.y + 45 };
  await client.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ ...touchStart, id: 1, radiusX: 2, radiusY: 2, force: .5 }] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ ...touchEnd, id: 1, radiusX: 2, radiusY: 2, force: .5 }] });
  await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });

  await expect(page.locator('[data-ink-stroke]')).toHaveCount(2);
  await expect.poll(() => viewport.getAttribute('style')).not.toBe(before);
});
