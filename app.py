import json
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Proyecto Kendry Morón - Red Política",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# 1. CONTROL DE ACCESO CON CLAVE
# ============================================================================
CLAVE_CORRECTA = st.secrets.get("CLAVE_ACCESO", "kendry2026")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
        <style>
        .stApp { background-color: #0f172a; color: #f8fafc; }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## ♟️ Proyecto Kendry Morón")
        st.caption("Acceso restringido — Estructura Electoral y Red de Influencia (≥100 partidas)")
        clave_ingresada = st.text_input("Introduce la clave de acceso:", type="password", placeholder="••••••••")
        if st.button("Entrar al Sistema", use_container_width=True, type="primary"):
            if clave_ingresada == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta. Inténtalo de nuevo.")
    st.stop()

# ============================================================================
# 2. CARGA DE LA BASE DE DATOS REAL
# ============================================================================
ARCHIVO_DB = "datos_federacion_real.json"
if not os.path.exists(ARCHIVO_DB):
    st.error("❌ No se encontró 'datos_federacion_real.json' en el repositorio.")
    st.stop()

with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
    db = json.load(f)

# Ajustar márgenes superiores para que el título y el botón Salir no queden tapados por la barra de Streamlit
st.markdown("""
    <style>
    header[data-testid="stHeader"] { background: transparent; }
    .block-container {
        padding-top: 3.2rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    </style>
""", unsafe_allow_html=True)

top_c1, top_c2 = st.columns([5, 1])
with top_c1:
    st.markdown("#### ♟️ Red Política — Proyecto Kendry Morón")
with top_c2:
    if st.button("🔒 Salir", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# ============================================================================
# 3. VISOR INTERACTIVO RESPONSIVO (PC + MÓVIL TÁCTIL)
# ============================================================================
db_json_str = json.dumps(db, ensure_ascii=False)

html_app = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: #0f172a;
      color: #f8fafc;
      margin: 0;
      display: flex;
      height: 820px;
      overflow: hidden;
      border-radius: 10px;
      border: 1px solid #334155;
    }}
    #sidebar {{
      width: 340px;
      background: #1e293b;
      padding: 16px;
      border-right: 1px solid #334155;
      overflow-y: auto;
      z-index: 10;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    #canvas-container {{
      flex: 1;
      position: relative;
      background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
      touch-action: none;
    }}
    h3 {{ font-size: 0.88rem; margin: 4px 0; color: #cbd5e1; }}
    select {{
      width: 100%;
      padding: 10px;
      border-radius: 6px;
      background: #0f172a;
      color: #f8fafc;
      border: 1px solid #475569;
      font-size: 0.9rem;
    }}
    .stat {{ background: #0f172a; padding: 8px 10px; border-radius: 6px; font-size: 0.82rem; border: 1px solid #334155; }}
    .legend {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 0.78rem; }}
    .dot {{ width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex-shrink: 0; }}
    svg {{ width: 100%; height: 100%; cursor: grab; display: block; touch-action: none; }}
    svg:active {{ cursor: grabbing; }}
    text {{ fill: #e2e8f0; font-size: 10px; pointer-events: none; text-anchor: middle; user-select: none; }}
    #zoom-controls {{ position: absolute; bottom: 14px; right: 14px; display: flex; gap: 6px; z-index: 20; }}
    .btn-zoom {{
      background: #1e293b;
      color: #f8fafc;
      border: 1px solid #475569;
      border-radius: 6px;
      padding: 8px 14px;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }}
    .btn-zoom:hover {{ background: #334155; border-color: #38bdf8; }}

    #info-card {{
      background: #0f172a;
      border: 1px solid #38bdf8;
      border-radius: 8px;
      padding: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }}
    #info-card .header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; border-bottom: 1px solid #334155; padding-bottom: 6px; margin-bottom: 8px; }}
    #info-card .title {{ font-weight: bold; font-size: 0.94rem; color: #f8fafc; }}
    #info-card .close-btn {{ background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 1.1rem; padding: 0 6px; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: bold; margin-bottom: 8px; }}
    .badge-vota {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }}
    .badge-rn {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }}
    .badge-no {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
    .info-row {{ display: flex; justify-content: space-between; font-size: 0.8rem; padding: 3px 0; border-bottom: 1px dashed #1e293b; }}
    .info-label {{ color: #94a3b8; }}
    .info-val {{ font-weight: 600; color: #e2e8f0; text-align: right; }}
    .rel-list {{ margin: 5px 0 0 0; padding-left: 16px; font-size: 0.78rem; color: #cbd5e1; max-height: 130px; overflow-y: auto; }}
    .rel-list li {{ margin-bottom: 3px; }}

    /* ADAPTACIÓN AUTOMÁTICA PARA CELULARES (pantallas <= 768px) */
    @media (max-width: 768px) {{
      body {{
        flex-direction: column;
        height: auto;
        min-height: 920px;
        overflow-y: auto;
      }}
      #canvas-container {{
        order: 1;
        width: 100%;
        height: 460px;
        flex: none;
        border-bottom: 1px solid #334155;
      }}
      #sidebar {{
        order: 2;
        width: 100%;
        border-right: none;
        padding: 12px;
        overflow-y: visible;
      }}
      .btn-zoom {{
        padding: 10px 15px;
        font-size: 1.05rem;
      }}
    }}
  </style>
</head>
<body>
  <div id="sidebar">
    <div>
      <label style="font-size:0.78rem; color:#94a3b8; display:block; margin-bottom:4px;">Filtrar por Miembro de Cúpula (Encargado 1):</label>
      <select id="filtroCupula">
        <option value="TODOS">-- Ver Toda la Estructura --</option>
      </select>
    </div>

    <div id="info-card">
      <div style="font-size:0.82rem; color:#94a3b8; text-align:center; padding:6px 0;">
        👆 Toca cualquier círculo en el mapa para ver su ficha completa, partidas y conexiones.
      </div>
    </div>

    <div id="stats"></div>

    <div>
      <h3>Jerarquía y Voto (&ge;100)</h3>
      <div class="legend"><span class="dot" style="background:#a855f7; border: 2px solid #fff;"></span> Nodo Raíz: Proyecto</div>
      <div class="legend"><span class="dot" style="background:#f59e0b; border: 2px solid #fff;"></span> Cúpula (Encargado 1)</div>
      <div class="legend"><span class="dot" style="background:#10b981;"></span> Vota por FIDE (&ge;100 FIDE)</div>
      <div class="legend"><span class="dot" style="background:#38bdf8;"></span> Vota por RN (FIDE + Nac &ge;100)</div>
      <div class="legend"><span class="dot" style="background:#ef4444;"></span> Menos de 100 partidas</div>
    </div>

    <p style="font-size:0.75rem; color:#94a3b8; margin:2px 0 0 0; line-height:1.35;">
      • <strong>Tocar / Clic en nodo:</strong> Ver ficha.<br>
      • <strong>Pellizcar / Rueda:</strong> Zoom.<br>
      • <strong>Arrastrar con 1 dedo:</strong> Mover mapa o nodo.
    </p>
  </div>

  <div id="canvas-container">
    <div id="zoom-controls">
      <button class="btn-zoom" id="zoomIn">+</button>
      <button class="btn-zoom" id="zoomOut">−</button>
      <button class="btn-zoom" id="zoomReset">Centrar</button>
    </div>
    <svg id="grafo"><g id="viewport"></g></svg>
  </div>

  <script>
    const data = {db_json_str};
    const {{ jugadores, relaciones }} = data;
    const select = document.getElementById('filtroCupula');
    const infoCard = document.getElementById('info-card');
    const cupulaNodes = jugadores.filter(j => j.esCupula).sort((a, b) => a.nombre.localeCompare(b.nombre));

    cupulaNodes.forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `${{c.aliasCupula || c.nombre}} (${{c.nombre}})`;
      select.appendChild(opt);
    }});

    const svg = document.getElementById('grafo');
    const viewport = document.getElementById('viewport');
    const isMobile = window.innerWidth <= 768;

    const baseSize = 800;
    const cx = baseSize / 2;
    const cy = baseSize / 2;

    let scale = 1, panX = 0, panY = 0;
    let isPanning = false, startPanX = 0, startPanY = 0;
    let draggedNode = null, dragMoved = false, selectedNodeId = null;
    let initialPinchDist = null, initialPinchScale = 1;

    function fitToScreen() {{
      const rect = svg.getBoundingClientRect();
      const w = rect.width || (isMobile ? 360 : 900);
      const h = rect.height || (isMobile ? 460 : 780);
      scale = Math.min(w / baseSize, h / baseSize) * 0.94;
      panX = (w - baseSize * scale) / 2;
      panY = (h - baseSize * scale) / 2;
      updateTransform();
    }}

    function updateTransform() {{
      viewport.setAttribute('transform', `translate(${{panX}}, ${{panY}}) scale(${{scale}})`);
    }}

    svg.addEventListener('wheel', (e) => {{
      e.preventDefault();
      const rect = svg.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      const newScale = Math.min(Math.max(0.25, scale * zoomFactor), 5);
      panX = mouseX - (mouseX - panX) * (newScale / scale);
      panY = mouseY - (mouseY - panY) * (newScale / scale);
      scale = newScale;
      updateTransform();
    }}, {{ passive: false }});

    document.getElementById('zoomIn').onclick = () => {{
      const rect = svg.getBoundingClientRect();
      const mx = rect.width / 2, my = rect.height / 2;
      const newScale = Math.min(scale * 1.25, 5);
      panX = mx - (mx - panX) * (newScale / scale);
      panY = my - (my - panY) * (newScale / scale);
      scale = newScale;
      updateTransform();
    }};
    document.getElementById('zoomOut').onclick = () => {{
      const rect = svg.getBoundingClientRect();
      const mx = rect.width / 2, my = rect.height / 2;
      const newScale = Math.max(scale * 0.8, 0.25);
      panX = mx - (mx - panX) * (newScale / scale);
      panY = my - (my - panY) * (newScale / scale);
      scale = newScale;
      updateTransform();
    }};
    document.getElementById('zoomReset').onclick = fitToScreen;

    svg.addEventListener('mousedown', (e) => {{
      if (draggedNode) return;
      isPanning = true;
      startPanX = e.clientX - panX;
      startPanY = e.clientY - panY;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (draggedNode) {{
        dragMoved = true;
        const rect = svg.getBoundingClientRect();
        draggedNode.x = (e.clientX - rect.left - panX) / scale;
        draggedNode.y = (e.clientY - rect.top - panY) / scale;
        render();
      }} else if (isPanning) {{
        panX = e.clientX - startPanX;
        panY = e.clientY - startPanY;
        updateTransform();
      }}
    }});

    window.addEventListener('mouseup', () => {{
      isPanning = false;
      draggedNode = null;
    }});

    svg.addEventListener('touchstart', (e) => {{
      if (e.touches.length === 2) {{
        isPanning = false;
        draggedNode = null;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        initialPinchDist = Math.hypot(dx, dy);
        initialPinchScale = scale;
      }} else if (e.touches.length === 1 && !draggedNode) {{
        isPanning = true;
        startPanX = e.touches[0].clientX - panX;
        startPanY = e.touches[0].clientY - panY;
      }}
    }}, {{ passive: false }});

    svg.addEventListener('touchmove', (e) => {{
      e.preventDefault();
      if (e.touches.length === 2 && initialPinchDist) {{
        const rect = svg.getBoundingClientRect();
        const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2 - rect.left;
        const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2 - rect.top;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.hypot(dx, dy);
        const newScale = Math.min(Math.max(0.25, initialPinchScale * (dist / initialPinchDist)), 5);
        panX = midX - (midX - panX) * (newScale / scale);
        panY = midY - (midY - panY) * (newScale / scale);
        scale = newScale;
        updateTransform();
      }} else if (e.touches.length === 1) {{
        if (draggedNode) {{
          dragMoved = true;
          const rect = svg.getBoundingClientRect();
          draggedNode.x = (e.touches[0].clientX - rect.left - panX) / scale;
          draggedNode.y = (e.touches[0].clientY - rect.top - panY) / scale;
          render();
        }} else if (isPanning) {{
          panX = e.touches[0].clientX - startPanX;
          panY = e.touches[0].clientY - startPanY;
          updateTransform();
        }}
      }}
    }}, {{ passive: false }});

    svg.addEventListener('touchend', (e) => {{
      if (draggedNode && !dragMoved) {{
        selectedNodeId = draggedNode.id;
        mostrarFicha(draggedNode);
        render();
        if (isMobile) infoCard.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
      if (e.touches.length < 2) initialPinchDist = null;
      if (e.touches.length === 0) {{
        isPanning = false;
        draggedNode = null;
      }}
    }});

    function mostrarFicha(n) {{
      if (!n) {{
        infoCard.innerHTML = `<div style="font-size:0.82rem; color:#94a3b8; text-align:center; padding:6px 0;">👆 Toca cualquier círculo en el mapa para ver su ficha completa, partidas y conexiones.</div>`;
        return;
      }}

      const total = Number(n.partidasFide || 0) + Number(n.partidasNac || 0);
      let badgeHtml = '';
      if (n.esProyecto) badgeHtml = '<span class="badge badge-rn">NODO CENTRAL DEL PROYECTO</span>';
      else if (n.partidasFide >= 100) badgeHtml = '<span class="badge badge-vota">✔ HABILITADO PARA VOTAR (FIDE &ge;100)</span>';
      else if (total >= 100) badgeHtml = '<span class="badge badge-rn">✔ HABILITADO POR RN (FIDE + NAC &ge;100)</span>';
      else badgeHtml = `<span class="badge badge-no">✖ NO HABILITADO (Faltan ${{100 - total}} partidas)</span>`;

      const entrantes = relaciones.filter(r => r.para === n.id).map(r => {{
        const src = jugadores.find(j => j.id === r.de);
        return src ? `${{src.aliasCupula || src.nombre}} (${{r.tipo}})` : null;
      }}).filter(Boolean);

      const salientes = relaciones.filter(r => r.de === n.id).map(r => {{
        const dst = jugadores.find(j => j.id === r.para);
        if (!dst) return null;
        const t = Number(dst.partidasFide || 0) + Number(dst.partidasNac || 0);
        return `${{dst.nombre}} [${{t}} pts]`;
      }}).filter(Boolean);

      let conexionesHtml = '';
      if (entrantes.length > 0) {{
        conexionesHtml += `<div style="margin-top:6px; font-size:0.78rem; color:#38bdf8; font-weight:bold;">Enlace / Encargado:</div><ul class="rel-list">${{entrantes.map(e => `<li>${{e}}</li>`).join('')}}</ul>`;
      }}
      if (salientes.length > 0) {{
        conexionesHtml += `<div style="margin-top:6px; font-size:0.78rem; color:#f59e0b; font-weight:bold;">Jugadores a cargo (${{salientes.length}}):</div><ul class="rel-list">${{salientes.map(s => `<li>${{s}}</li>`).join('')}}</ul>`;
      }}

      infoCard.innerHTML = `
        <div class="header">
          <div class="title">${{n.nombre}}</div>
          <button class="close-btn" id="cerrarFicha">✕</button>
        </div>
        ${{badgeHtml}}
        <div class="info-row"><span class="info-label">FIDE ID:</span><span class="info-val">${{n.fide_id}}</span></div>
        <div class="info-row"><span class="info-label">Rol:</span><span class="info-val">${{n.cargo}}</span></div>
        <div class="info-row"><span class="info-label">Provincia:</span><span class="info-val">${{n.provincia}}</span></div>
        <div class="info-row"><span class="info-label">Estatus Político:</span><span class="info-val">${{n.status}}</span></div>
        ${{!n.esProyecto ? `
          <div class="info-row"><span class="info-label">Partidas FIDE:</span><span class="info-val">${{n.partidasFide}}</span></div>
          <div class="info-row"><span class="info-label">Partidas Nac (RN):</span><span class="info-val">${{n.partidasNac}}</span></div>
          <div class="info-row"><span class="info-label">Total Partidas:</span><span class="info-val" style="color:#38bdf8;">${{total}}</span></div>
        ` : ''}}
        ${{conexionesHtml}}
      `;

      document.getElementById('cerrarFicha').onclick = () => {{
        selectedNodeId = null;
        mostrarFicha(null);
        render();
      }};
    }}

    const cupulaList = jugadores.filter(j => j.nivel === 1);
    const baseList = jugadores.filter(j => j.nivel === 2);

    const nodes = jugadores.map(j => {{
      if (j.nivel === 0) return {{ ...j, x: cx, y: cy }};
      if (j.nivel === 1) {{
        const idx = cupulaList.findIndex(c => c.id === j.id);
        const angle = (idx / cupulaList.length) * 2 * Math.PI - Math.PI / 2;
        return {{ ...j, x: cx + 165 * Math.cos(angle), y: cy + 165 * Math.sin(angle) }};
      }}
      const idx = baseList.findIndex(b => b.id === j.id);
      const angle = (idx / baseList.length) * 2 * Math.PI;
      const r = 310 + (idx % 2) * 40;
      return {{ ...j, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }};
    }});

    function render() {{
      const filtroId = select.value;
      viewport.innerHTML = '';

      let visibleIds = new Set(nodes.map(n => n.id));
      let visibleRels = relaciones;

      if (filtroId !== 'TODOS') {{
        const cid = Number(filtroId);
        visibleIds = new Set([1, cid]);
        visibleRels = relaciones.filter(r =>
          (r.de === 1 && r.para === cid) ||
          (r.de === cid && (r.tipo === 'ENCARGADO_1' || r.tipo === 'ENLACE_CUPULA'))
        );
        visibleRels.forEach(r => {{ visibleIds.add(r.de); visibleIds.add(r.para); }});
      }}

      const visNodes = nodes.filter(n => visibleIds.has(n.id));
      const soloJugadores = visNodes.filter(n => n.nivel > 0);
      const habilitados = soloJugadores.filter(j => (j.partidasFide + j.partidasNac) >= 100).length;

      document.getElementById('stats').innerHTML = `
        <div class="stat"><strong>Nodos visibles:</strong> ${{soloJugadores.length}} | <strong>Votan (&ge;100):</strong> ${{habilitados}}</div>
      `;

      visibleRels.forEach(rel => {{
        const s = nodes.find(n => n.id === rel.de);
        const t = nodes.find(n => n.id === rel.para);
        if (!s || !t) return;

        const isHighlighted = selectedNodeId && (rel.de === selectedNodeId || rel.para === selectedNodeId);
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', s.x); line.setAttribute('y1', s.y);
        line.setAttribute('x2', t.x); line.setAttribute('y2', t.y);
        line.setAttribute('stroke', isHighlighted ? '#facc15' : (rel.tipo === 'CUPULA_PROYECTO' ? '#f59e0b' : (rel.tipo === 'ENCARGADO_2' ? '#64748b' : '#38bdf8')));
        line.setAttribute('stroke-width', isHighlighted ? '3' : (rel.tipo === 'CUPULA_PROYECTO' ? '2.2' : '1.2'));
        line.setAttribute('stroke-opacity', selectedNodeId ? (isHighlighted ? '1' : '0.15') : (rel.tipo === 'ENCARGADO_2' ? '0.35' : '0.7'));
        if (rel.tipo === 'ENCARGADO_2') line.setAttribute('stroke-dasharray', '4,4');
        viewport.appendChild(line);
      }});

      visNodes.forEach(n => {{
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        const total = n.partidasFide + n.partidasNac;

        let color = '#ef4444';
        if (n.esProyecto) color = '#a855f7';
        else if (n.esCupula) color = '#f59e0b';
        else if (n.partidasFide >= 100) color = '#10b981';
        else if (total >= 100) color = '#38bdf8';

        const isSelected = selectedNodeId === n.id;
        const baseR = n.esProyecto ? 28 : (n.esCupula ? 18 : (isMobile ? 13 : 10));
        const r = baseR + (isSelected ? 4 : 0);

        circle.setAttribute('cx', n.x);
        circle.setAttribute('cy', n.y);
        circle.setAttribute('r', r);
        circle.setAttribute('fill', color);
        circle.style.cursor = 'pointer';

        if (isSelected) {{
          circle.setAttribute('stroke', '#facc15');
          circle.setAttribute('stroke-width', '3.5');
        }} else if (n.esProyecto || n.esCupula) {{
          circle.setAttribute('stroke', '#fff');
          circle.setAttribute('stroke-width', '2');
        }}

        circle.addEventListener('mousedown', (e) => {{
          e.stopPropagation();
          draggedNode = n;
          dragMoved = false;
        }});

        circle.addEventListener('touchstart', (e) => {{
          if (e.touches.length === 1) {{
            e.stopPropagation();
            draggedNode = n;
            dragMoved = false;
          }}
        }}, {{ passive: false }});

        circle.addEventListener('click', (e) => {{
          e.stopPropagation();
          if (!dragMoved) {{
            selectedNodeId = n.id;
            mostrarFicha(n);
            render();
          }}
        }});

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', n.x);
        text.setAttribute('y', n.y + r + 12);
        text.style.fontWeight = (n.esProyecto || n.esCupula || isSelected) ? 'bold' : 'normal';
        text.style.fill = isSelected ? '#facc15' : '#e2e8f0';
        text.textContent = n.esProyecto ? n.nombre : (n.esCupula ? `${{n.aliasCupula}}` : `${{n.nombre.split(',')[0]}} (${{total}})`);

        g.appendChild(circle);
        g.appendChild(text);
        viewport.appendChild(g);
      }});

      updateTransform();
    }}

    select.onchange = () => {{
      selectedNodeId = null;
      mostrarFicha(null);
      render();
    }};

    window.addEventListener('resize', fitToScreen);
    render();
    setTimeout(fitToScreen, 50);
  </script>
</body>
</html>"""

components.html(html_app, height=940, scrolling=True)
