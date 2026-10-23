import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type PointerEvent as ReactPointerEvent } from 'react';
import { ReactFlow, ReactFlowProvider, Background, BackgroundVariant, MiniMap, useReactFlow, useViewport, applyNodeChanges, ConnectionMode, MarkerType, type Connection, type Edge, type OnNodesChange, type OnEdgesChange, type Viewport } from '@xyflow/react';
import { Plus, Search, ZoomIn, ZoomOut, Maximize, Undo2, Redo2, Map, Network, X, ArrowRight, Eye, Trash2, Sparkles, LoaderCircle, ExternalLink, PanelRightClose, Hand, PenLine, Eraser, MousePointer2, Grid3X3 } from 'lucide-react';
import '@xyflow/react/dist/style.css';
import { useApp, createNote, deleteNotes, nextPosition, toast, saveEntityDraft, preserveEntityDraft, getWorkspaceEpoch } from '../store';
import { uid, now, colors, relations, type InkColor, type InkPoint, type InkStroke, type Point, type Relation } from '../types';
import { NoteNode, type ResearchNode } from './NoteNode';
import { Modal } from './Modal';
import { GroupSummaryDialog } from './GroupSummaryDialog';
import { useAI, cancelTask } from '../lib/ai';
import { connectedGroup } from '../lib/groupSummary';
import { registerEditor, getProjectId } from '../lib/projectContext';
import { inkPath, normalizedRect, strokeHitsPoint, strokeIntersectsRect, translateStroke } from '../lib/ink';

const nodeTypes = { researchNote: NoteNode };
const inkColors: Record<InkColor, string> = { black: '#26322d', blue: '#316ba0', green: '#41805a', red: '#b85046' };
type InkTool = 'pan' | 'pen' | 'eraser' | 'select';
type InkGesture =
  | { type: 'pen'; pointerId: number; points: InkPoint[] }
  | { type: 'erase'; pointerId: number; ids: Set<string> }
  | { type: 'marquee'; pointerId: number; start: Point; current: Point; additive: boolean }
  | { type: 'move'; pointerId: number; start: Point; delta: Point; ids: Set<string> };
interface CanvasProps { onCollapse?: () => void; onPopout?: (viewport: Viewport) => void }
function EdgeEditor({ edge, close }: { edge: Relation; close: () => void }) {
  const [base] = useState(edge);
  const [epoch] = useState(getWorkspaceEpoch);
  const [projectId] = useState(getProjectId);
  const [draft, setDraft] = useState(edge);
  const latest = useRef(draft); latest.current = draft; const dismissed = useRef(false);
  function finish() { dismissed.current = true; close(); }
  const autoSaved = useRef('');
  useEffect(() => registerEditor(() => { saveEntityDraft('edges', base, latest.current, epoch, projectId); autoSaved.current = JSON.stringify(latest.current); }, () => ({ projectId, epoch, base, values: latest.current })), [base, epoch, projectId]);
  useEffect(() => () => { if (!dismissed.current && JSON.stringify(latest.current) !== autoSaved.current && !useApp.getState().workspace.edges.some(e => e.id === base.id)) void preserveEntityDraft('edges', base, latest.current, epoch, projectId); }, [base, epoch, projectId]);
  function save() { saveEntityDraft('edges', base, draft, epoch); finish(); }
  return <Modal title="編輯便條關係" description="這是你建立的研究連結，可隨時調整。" onClose={finish}>
    <div className="editor-form"><label>關係類型<select value={draft.relationType} onChange={e => setDraft({ ...draft, relationType: e.target.value as Relation['relationType'] })}>{relations.map(r => <option key={r}>{r}</option>)}</select></label>
      <label>說明（選填）<input autoFocus value={draft.label} placeholder="例如：不同資料集得到相同結論" maxLength={200} onChange={e => setDraft({ ...draft, label: e.target.value })} /></label>
      <label className="checkbox-label"><input type="checkbox" checked={draft.directed} onChange={e => setDraft({ ...draft, directed: e.target.checked })} />顯示方向箭頭</label>
      <footer className="modal-actions"><button className="danger-button" onClick={() => { dismissed.current = true; useApp.getState().edit(w => { w.edges = w.edges.filter(e => e.id !== edge.id); }); close(); }}><Trash2 size={14} />刪除連線</button><button className="primary-button" onClick={save}>儲存關係</button></footer></div>
  </Modal>;
}
function CanvasInner({ onCollapse, onPopout }: CanvasProps) {
  const { workspace, preferences, focusNoteId, selectedNoteId, history, future, groupSummaryAnchorId } = useApp();
  const groupTask = useAI(s => s.group);
  const [nodes, setNodes] = useState<ResearchNode[]>([]); const [query, setQuery] = useState('');
  const [miniMap, setMiniMap] = useState(false); const [editEdgeId, setEditEdgeId] = useState<string>();
  const [selectedEdges, setSelectedEdges] = useState<string[]>([]); const [showHidden, setShowHidden] = useState(false);
  const [inkTool, setInkTool] = useState<InkTool>('pan'); const [inkColor, setInkColor] = useState<InkColor>('black');
  const [selectedInk, setSelectedInk] = useState<Set<string>>(new Set()); const gesture = useRef<InkGesture | undefined>(undefined); const [, redrawInk] = useState(0);
  const { fitBounds, getNodesBounds, zoomIn, zoomOut, setCenter, getNode, screenToFlowPosition, getViewport } = useReactFlow<ResearchNode>();
  const liveViewport = useViewport();
  const matches = useMemo(() => {
    const q = query.toLocaleLowerCase().trim();
    return new Set(workspace.notes.filter(n => (!n.hidden || showHidden) && (!q || [n.title, n.originalText, n.translation?.text, n.summary?.text, n.userNotes, n.tags.join(' ')].join(' ').toLocaleLowerCase().includes(q))).map(n => n.id));
  }, [workspace.notes, query, showHidden]);
  useEffect(() => {
    setNodes(old => workspace.notes.filter(n => !n.hidden || showHidden).map(note => {
      const existing = old.find(n => n.id === note.id);
      return { id: note.id, type: 'researchNote', data: { note, paper: workspace.documents.find(d => d.id === note.documentId), highlight: workspace.highlights.find(h => h.id === note.highlightId) },
        position: existing?.dragging ? existing.position : note.position, style: { width: note.width, opacity: matches.has(note.id) ? 1 : 0.18 },
        selected: selectedNoteId === note.id || !!existing?.selected, dragHandle: '.note-header, .note-title' };
    }));
  }, [workspace.notes, workspace.documents, workspace.highlights, selectedNoteId, matches, showHidden]);
  useEffect(() => {
    if (!focusNoteId) return;
    const timer = setTimeout(() => {
      const n = getNode(focusNoteId); if (!n) return;
      setCenter(n.position.x + (n.measured?.width || 320) / 2, n.position.y + (n.measured?.height || 300) / 2, { zoom: Math.min(Math.max(getViewport().zoom, 0.75), 1), duration: 350 });
      useApp.setState({ focusNoteId: undefined });
    }, 100); return () => clearTimeout(timer);
  }, [focusNoteId, nodes.length, getNode, setCenter, getViewport]);
  useEffect(() => { setSelectedInk(ids => new Set([...ids].filter(id => workspace.inkStrokes.some(stroke => stroke.id === id)))); }, [workspace.inkStrokes]);
  const edges: Edge[] = workspace.edges.filter(e => nodes.some(n => n.id === e.source) && nodes.some(n => n.id === e.target)).map(e => ({
    id: e.id, source: e.source, target: e.target, sourceHandle: e.sourceHandle, targetHandle: e.targetHandle,
    type: 'smoothstep', label: e.label || e.relationType, selected: selectedEdges.includes(e.id),
    markerEnd: e.directed ? { type: MarkerType.ArrowClosed, color: '#719180' } : undefined,
    style: { stroke: selectedEdges.includes(e.id) ? '#355c4b' : '#8ca697', strokeWidth: selectedEdges.includes(e.id) ? 2.5 : 1.7 },
    labelStyle: { fill: '#557260', fontSize: 11 }, labelBgStyle: { fill: '#f7f8f4' }, labelBgPadding: [8, 5], labelBgBorderRadius: 5,
  }));
  const onNodesChange: OnNodesChange<ResearchNode> = useCallback(changes => {
    setNodes(n => applyNodeChanges(changes.filter(c => c.type !== 'remove'), n));
  }, []);
  const onEdgesChange: OnEdgesChange = useCallback(changes => { for (const change of changes) if (change.type === 'select') setSelectedEdges(ids => change.selected ? [...new Set([...ids, change.id])] : ids.filter(id => id !== change.id)); }, []);
  const connect = useCallback((c: Connection) => {
    if (!c.source || !c.target || c.source === c.target) return;
    const edge: Relation = { id: uid(), source: c.source, target: c.target, sourceHandle: c.sourceHandle || undefined, targetHandle: c.targetHandle || undefined, relationType: '相關', label: '', directed: false, createdBy: 'user', createdAt: now(), updatedAt: now() };
    useApp.getState().edit(w => { w.edges.push(edge); }); setEditEdgeId(edge.id);
  }, []);
  const editEdge = workspace.edges.find(e => e.id === editEdgeId);
  function refreshInk() { redrawInk(value => value + 1); }
  function cancelInkGesture() { gesture.current = undefined; refreshInk(); }
  function chooseInkTool(tool: InkTool) {
    cancelInkGesture(); setInkTool(tool);
    if (tool !== 'select') setSelectedInk(new Set());
  }
  function pointerPoint(e: ReactPointerEvent<HTMLDivElement>): InkPoint {
    const point = screenToFlowPosition({ x: e.clientX, y: e.clientY });
    return { ...point, ...(e.pointerType === 'pen' && e.pressure > 0 ? { pressure: e.pressure } : {}) };
  }
  function strokeAt(point: Point) {
    const moving = gesture.current?.type === 'move' ? gesture.current : undefined;
    return [...workspace.inkStrokes].reverse().find(stroke => strokeHitsPoint(moving?.ids.has(stroke.id) ? translateStroke(stroke, moving.delta) : stroke, point, 7 / liveViewport.zoom));
  }
  function startInk(e: ReactPointerEvent<HTMLDivElement>) {
    if (inkTool === 'pan' || e.button !== 0 || (e.target as Element).closest('.canvas-tools, .ink-toolbar')) return;
    e.preventDefault(); e.stopPropagation(); e.currentTarget.focus(); e.currentTarget.setPointerCapture(e.pointerId);
    const point = pointerPoint(e);
    if (inkTool === 'pen') gesture.current = { type: 'pen', pointerId: e.pointerId, points: [point] };
    else if (inkTool === 'eraser') {
      const hit = strokeAt(point); gesture.current = { type: 'erase', pointerId: e.pointerId, ids: new Set(hit ? [hit.id] : []) };
    } else {
      const hit = strokeAt(point);
      if (hit) {
        const ids = selectedInk.has(hit.id) ? new Set(selectedInk) : new Set(e.shiftKey ? [...selectedInk, hit.id] : [hit.id]);
        setSelectedInk(ids); gesture.current = { type: 'move', pointerId: e.pointerId, start: point, delta: { x: 0, y: 0 }, ids };
      } else gesture.current = { type: 'marquee', pointerId: e.pointerId, start: point, current: point, additive: e.shiftKey };
    }
    refreshInk();
  }
  function moveInk(e: ReactPointerEvent<HTMLDivElement>) {
    const active = gesture.current; if (!active || active.pointerId !== e.pointerId) return;
    e.preventDefault(); e.stopPropagation(); const point = pointerPoint(e);
    if (active.type === 'pen') {
      const prior = active.points[active.points.length - 1];
      if (Math.hypot(point.x - prior.x, point.y - prior.y) >= 1.25 / liveViewport.zoom) active.points.push(point);
    } else if (active.type === 'erase') {
      for (const stroke of workspace.inkStrokes) if (!active.ids.has(stroke.id) && strokeHitsPoint(stroke, point, 8 / liveViewport.zoom)) active.ids.add(stroke.id);
    } else if (active.type === 'marquee') active.current = point;
    else active.delta = { x: point.x - active.start.x, y: point.y - active.start.y };
    refreshInk();
  }
  function finishInk(e: ReactPointerEvent<HTMLDivElement>) {
    const active = gesture.current; if (!active || active.pointerId !== e.pointerId) return;
    e.preventDefault(); e.stopPropagation();
    if (active.type === 'pen' && active.points.length) {
      const timestamp = now(); const stroke: InkStroke = { id: uid(), color: inkColor, width: 3.2, points: active.points, createdAt: timestamp, updatedAt: timestamp };
      useApp.getState().edit(w => { w.inkStrokes.push(stroke); });
    } else if (active.type === 'erase' && active.ids.size) {
      useApp.getState().edit(w => { w.inkStrokes = w.inkStrokes.filter(stroke => !active.ids.has(stroke.id)); });
      setSelectedInk(ids => new Set([...ids].filter(id => !active.ids.has(id))));
    } else if (active.type === 'marquee') {
      const rect = normalizedRect(active.start, active.current);
      const found = rect.width < 2 / liveViewport.zoom && rect.height < 2 / liveViewport.zoom ? [] : workspace.inkStrokes.filter(stroke => strokeIntersectsRect(stroke, rect)).map(stroke => stroke.id);
      setSelectedInk(new Set(active.additive ? [...selectedInk, ...found] : found));
    } else if (active.type === 'move' && (active.delta.x || active.delta.y)) {
      const timestamp = now();
      useApp.getState().edit(w => { w.inkStrokes = w.inkStrokes.map(stroke => active.ids.has(stroke.id) ? { ...translateStroke(stroke, active.delta), updatedAt: timestamp } : stroke); });
    }
    gesture.current = undefined; if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId); refreshInk();
  }
  function deleteInkSelection() {
    if (!selectedInk.size) return false;
    useApp.getState().edit(w => { w.inkStrokes = w.inkStrokes.filter(stroke => !selectedInk.has(stroke.id)); }); setSelectedInk(new Set()); return true;
  }
  function fitBoard() {
    const boxes: { x: number; y: number; width: number; height: number }[] = [];
    if (nodes.length) boxes.push(getNodesBounds(nodes));
    let pointCount = 0; let inkLeft = Infinity; let inkTop = Infinity; let inkRight = -Infinity; let inkBottom = -Infinity;
    for (const stroke of workspace.inkStrokes) for (const point of stroke.points) {
      pointCount++; inkLeft = Math.min(inkLeft, point.x); inkTop = Math.min(inkTop, point.y); inkRight = Math.max(inkRight, point.x); inkBottom = Math.max(inkBottom, point.y);
    }
    if (pointCount) {
      boxes.push({ x: inkLeft - 12, y: inkTop - 12, width: Math.max(24, inkRight - inkLeft + 24), height: Math.max(24, inkBottom - inkTop + 24) });
    }
    if (!boxes.length) { toast('標記文字、新增便條或手寫後，即可查看全貌'); return; }
    const left = Math.min(...boxes.map(box => box.x)); const top = Math.min(...boxes.map(box => box.y));
    const right = Math.max(...boxes.map(box => box.x + box.width)); const bottom = Math.max(...boxes.map(box => box.y + box.height));
    void fitBounds({ x: left, y: top, width: Math.max(24, right - left), height: Math.max(24, bottom - top) }, { padding: 0.15, duration: 350 });
  }
  function add() {
    const pane = document.querySelector('.research-canvas')!.getBoundingClientRect();
    createNote({ position: nextPosition(screenToFlowPosition({ x: pane.left + pane.width / 2 - 160, y: pane.top + pane.height / 2 - 140 })) });
  }
  function deleteSelection() {
    if (deleteInkSelection()) return;
    const ids = nodes.filter(n => n.selected).map(n => n.id);
    if (ids.length && confirm(`刪除 ${ids.length} 張便條、來源標記與相關連線？可用復原恢復。`)) deleteNotes(ids, true);
    else if (!ids.length && selectedEdges.length) useApp.getState().edit(w => { w.edges = w.edges.filter(e => !selectedEdges.includes(e.id)); });
  }
  function saveViewport(v: Viewport) { useApp.getState().edit(w => { w.viewport = v; }, false); }
  const visibleCount = workspace.notes.filter(n => !n.hidden).length;
  const selectedGroup = useMemo(() => connectedGroup(workspace, selectedNoteId), [workspace, selectedNoteId]);
  const activeInk = gesture.current; const erasedInk = activeInk?.type === 'erase' ? activeInk.ids : new Set<string>();
  const movingInk = activeInk?.type === 'move' ? activeInk : undefined;
  const drawnInk = workspace.inkStrokes.filter(stroke => !erasedInk.has(stroke.id)).map(stroke => movingInk?.ids.has(stroke.id) ? translateStroke(stroke, movingInk.delta) : stroke);
  const marquee = activeInk?.type === 'marquee' ? normalizedRect(activeInk.start, activeInk.current) : undefined;
  return <section className="board-pane" aria-label="研究白板"><div className="pane-heading"><div className="eyebrow"><span className="section-dot terracotta" />知識白板<span className="small-label">CONNECT</span><span className="count-badge">{visibleCount}</span></div>
    <div className="board-heading-actions"><button className={`icon-button ${showHidden ? 'active' : ''}`} onClick={() => setShowHidden(!showHidden)} title="顯示或隱藏已收起的卡片" aria-label="顯示隱藏便條"><Eye size={16} /></button>
      <div className="board-search"><Search size={14} /><input placeholder="尋找…" title="尋找想法、原文或 #標籤" aria-label="搜尋便條" value={query} onChange={e => setQuery(e.target.value)} />{query && <div className="board-search-actions"><span>{matches.size} 張</span><button className="icon-button" onClick={() => setQuery('')} aria-label="清除便條搜尋"><X size={14} /></button><button className="icon-button" title="定位搜尋結果" aria-label="定位搜尋結果" disabled={!matches.size} onClick={() => { if (matches.size) { const id = [...matches][0]; useApp.setState({ selectedNoteId: id, focusNoteId: id }); } }}><ArrowRight size={15} /></button></div>}</div>
      <button className="group-summary-button" aria-label="關聯摘要" disabled={selectedGroup.notes.length < 2 || !!groupTask} title={selectedGroup.notes.length < 2 ? '先點選一張已連線的便條' : `整合這組 ${selectedGroup.notes.length} 張便條`} onClick={() => useApp.setState({ groupSummaryAnchorId: selectedNoteId })}><Sparkles size={14} /><span>關聯摘要</span></button><button className="add-note-button" aria-label="新增便條" title="新增便條" onClick={add}><Plus size={15} /><span>新增便條</span></button>
      <div className="board-pane-tools">{onPopout && <button className="icon-button" title="在新視窗開啟白板" aria-label="在新視窗開啟白板" onClick={() => onPopout(getViewport())}><ExternalLink size={16} /></button>}{onCollapse && <button className="icon-button" title="隱藏知識白板" aria-label="隱藏知識白板" onClick={() => { saveViewport(getViewport()); onCollapse(); }}><PanelRightClose size={17} /></button>}</div>
    </div></div>
    {groupTask && <div className="group-ai-progress" role="status"><LoaderCircle size={15} className="spin" /><span>正在整合 {groupTask.sourceCount} 張關聯便條…</span><button onClick={() => cancelTask(groupTask.taskId)}>取消整合</button></div>}
    <div className={`research-canvas ink-tool-${inkTool}`} onPointerDownCapture={startInk} onPointerMoveCapture={moveInk} onPointerUpCapture={finishInk} onPointerCancelCapture={finishInk}
      onKeyDown={e => { const tag = (e.target as HTMLElement).tagName; if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag) || (e.target as HTMLElement).isContentEditable) return; if (e.key === 'Escape') { cancelInkGesture(); setSelectedInk(new Set()); } else if (e.key === 'Delete' || e.key === 'Backspace') { e.preventDefault(); deleteSelection(); } }} tabIndex={0}>
      <ReactFlow<ResearchNode> nodes={nodes} edges={edges} nodeTypes={nodeTypes} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={connect}
        onNodeClick={(_, n) => useApp.setState({ selectedNoteId: n.id })} onPaneClick={() => { useApp.setState({ selectedNoteId: undefined }); setSelectedEdges([]); setNodes(n => n.map(x => ({ ...x, selected: false }))); }}
        onNodeDragStop={(_, node, dragged) => { const changed = dragged.length ? dragged : [node]; useApp.getState().edit(w => { changed.forEach(n => { const note = w.notes.find(x => x.id === n.id); if (note) note.position = n.position; }); }); }}
        onNodeDoubleClick={(_, node) => useApp.setState({ selectedNoteId: node.id })}
        onEdgeDoubleClick={(_, edge) => setEditEdgeId(edge.id)}
        onNodeDragStart={() => useApp.setState({ focusNoteId: undefined })}
        onMoveEnd={(_, vp) => saveViewport(vp)} defaultViewport={workspace.viewport} minZoom={0.2} maxZoom={1.8}
        connectionMode={ConnectionMode.Loose} deleteKeyCode={null} selectionKeyCode="Shift" multiSelectionKeyCode="Shift" panOnScroll selectionOnDrag={false}
        panOnDrag={inkTool === 'pan'} nodesDraggable={inkTool === 'pan'} nodesConnectable={inkTool === 'pan'} elementsSelectable={inkTool === 'pan'} zoomOnDoubleClick={inkTool === 'pan'}
        proOptions={{ hideAttribution: false }} aria-label="無邊際研究白板">
        <Background variant={preferences.boardGrid ? BackgroundVariant.Lines : BackgroundVariant.Dots} gap={preferences.boardGrid ? 24 : 22} size={preferences.boardGrid ? 0.8 : 1.1} color={preferences.boardGrid ? '#d9e1d3' : '#c8d0c4'} />
        {miniMap && <MiniMap nodeColor={n => (n as ResearchNode).data.note.type === 'group-summary' ? '#a493c5' : colors[(n as ResearchNode).data.note.color]} maskColor="rgba(237,240,232,.7)" pannable zoomable position="bottom-right" />}
      </ReactFlow>
      <svg className="ink-layer" aria-hidden="true"><g transform={`translate(${liveViewport.x} ${liveViewport.y}) scale(${liveViewport.zoom})`}>
        {drawnInk.map(stroke => <g key={stroke.id} data-ink-stroke={stroke.id}>
          {selectedInk.has(stroke.id) && <path className="ink-selection" d={inkPath(stroke.points)} strokeWidth={stroke.width + 6 / liveViewport.zoom} />}
          <path className="ink-stroke" d={inkPath(stroke.points)} stroke={inkColors[stroke.color]} strokeWidth={stroke.width} />
        </g>)}
        {activeInk?.type === 'pen' && <path className="ink-stroke ink-draft" d={inkPath(activeInk.points)} stroke={inkColors[inkColor]} strokeWidth={3.2} />}
        {marquee && <rect className="ink-marquee" x={marquee.x} y={marquee.y} width={marquee.width} height={marquee.height} strokeWidth={1 / liveViewport.zoom} strokeDasharray={`${5 / liveViewport.zoom} ${4 / liveViewport.zoom}`} />}
      </g></svg>
      {!visibleCount && !workspace.inkStrokes.length && <div className="board-empty"><div className="empty-network"><Network size={35} /></div><h3>讓想法，有跡可循。</h3><p>在左側標記一段文字，<br />它就會成為這裡的一張便條。</p><button className="text-button" onClick={add}><Plus size={14} />或先記下一個想法</button><div className="empty-board-line" /><span>拖曳整理 · 手寫註記 · 連線思考</span></div>}
      <div className="ink-toolbar" role="toolbar" aria-label="白板手寫工具">
        <button className={`icon-button ${inkTool === 'pan' ? 'active' : ''}`} onClick={() => chooseInkTool('pan')} title="移動畫布" aria-label="移動畫布"><Hand size={16} /></button>
        <button className={`icon-button ${inkTool === 'pen' ? 'active' : ''}`} onClick={() => chooseInkTool('pen')} title="手寫畫筆" aria-label="手寫畫筆"><PenLine size={16} /></button>
        <button className={`icon-button ${inkTool === 'eraser' ? 'active' : ''}`} onClick={() => chooseInkTool('eraser')} title="整筆橡皮擦" aria-label="整筆橡皮擦"><Eraser size={16} /></button>
        <button className={`icon-button ${inkTool === 'select' ? 'active' : ''}`} onClick={() => chooseInkTool('select')} title="框選多筆畫" aria-label="框選多筆畫"><MousePointer2 size={16} /></button>
        <i />
        <button className={`icon-button ${preferences.boardGrid ? 'active' : ''}`} onClick={() => useApp.getState().pref({ boardGrid: !preferences.boardGrid })} title={preferences.boardGrid ? '關閉淡色格線' : '開啟淡色格線'} aria-label={preferences.boardGrid ? '關閉淡色格線' : '開啟淡色格線'}><Grid3X3 size={16} /></button>
        {inkTool === 'pen' && <div className="ink-palette" aria-label="畫筆顏色">{(Object.keys(inkColors) as InkColor[]).map(color => <button key={color} className={inkColor === color ? 'active' : ''} style={{ '--ink-color': inkColors[color] } as CSSProperties} aria-label={`${{ black: '黑色', blue: '藍色', green: '綠色', red: '紅色' }[color]}畫筆`} title={`${{ black: '黑色', blue: '藍色', green: '綠色', red: '紅色' }[color]}畫筆`} onClick={() => setInkColor(color)} />)}</div>}
      </div>
      <div className="canvas-tools"><button className="icon-button" title="復原 Ctrl+Z" aria-label="復原" disabled={!history.length} onClick={() => useApp.getState().undo()}><Undo2 size={16} /></button><button className="icon-button" title="重做 Ctrl+Shift+Z" aria-label="重做" disabled={!future.length} onClick={() => useApp.getState().redo()}><Redo2 size={16} /></button><i /><button className="icon-button" aria-label="縮小白板" onClick={() => zoomOut()}><ZoomOut size={16} /></button><button className="icon-button" aria-label="放大白板" onClick={() => zoomIn()}><ZoomIn size={16} /></button><button className="icon-button" aria-label="白板全貌" title="回到全貌" onClick={fitBoard}><Maximize size={16} /></button><i /><button className={`icon-button ${miniMap ? 'active' : ''}`} aria-label="切換小地圖" onClick={() => setMiniMap(!miniMap)}><Map size={16} /></button></div>
      <span className="canvas-hint">{inkTool === 'pan' ? 'Shift 多選 · 拖曳連接點建立關係' : inkTool === 'pen' ? '拖曳書寫 · 可使用滑鼠或觸控筆' : inkTool === 'eraser' ? '碰觸筆畫即可整筆擦除' : `${selectedInk.size ? `已選 ${selectedInk.size} 筆 · 拖曳移動 · Delete 刪除` : '拖曳框選多筆畫'}`}</span>
    </div>
    {editEdge && <EdgeEditor key={editEdge.id} edge={editEdge} close={() => setEditEdgeId(undefined)} />}
    {groupSummaryAnchorId && <GroupSummaryDialog anchorId={groupSummaryAnchorId} close={() => useApp.setState({ groupSummaryAnchorId: undefined })} />}
  </section>;
}
export function ResearchCanvas(props: CanvasProps) { return <ReactFlowProvider><CanvasInner {...props} /></ReactFlowProvider>; }
