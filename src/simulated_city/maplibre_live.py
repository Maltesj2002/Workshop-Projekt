"""MapLibre live-update helper for anymap-ts.

Goal: enable *incremental* marker updates (e.g. MQTT streaming coordinates)
without needing to redraw the whole map.

Implementation approach:
- anymap-ts ships a bundled ESM module (maplibre.js) whose frontend registers
  a set of JS methods (addMarker/removeMarker/animateAlongRoute/...)
- For live updates we add a new JS method `moveMarker` that updates an existing
  marker in-place via `marker.setLngLat([lng, lat])` (or creates it if missing).

We avoid patching the installed bundle on disk by generating a patched ESM file
in a temp directory at runtime and pointing the widget instance at it.

This keeps workshop code self-contained and works in Jupyter/VS Code notebooks.
"""

from __future__ import annotations

import importlib.metadata
import re
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple


def _require_anymap_ts():
	try:
		from anymap_ts.maplibre import MapLibreMap, STATIC_DIR
	except Exception as exc:  # pragma: no cover
		raise ImportError(
			"anymap-ts is required for LiveMapLibreMap. "
			"Install extras: `pip install -e .[notebooks]`"
		) from exc
	return MapLibreMap, STATIC_DIR


def _inject_renderer_binding(content: str) -> str:
	"""Ensure a stable MapLibreRenderer binding exists in the bundle."""
	if re.search(r"\b(const|let|var)\s+MapLibreRenderer\b", content):
		return content

	match = re.search(r"export\{[^}]*\bas\s+MapLibreRenderer\b[^}]*\};", content)
	if not match:
		raise RuntimeError(
			"Unsupported anymap-ts bundle shape: could not locate MapLibreRenderer export. "
			"Try upgrading/downgrading anymap-ts, or update the patcher."
		)

	export_block = match.group(0)
	id_match = re.search(r"([\w$]+)\s+as\s+MapLibreRenderer", export_block)
	if not id_match:
		raise RuntimeError(
			"Unsupported anymap-ts bundle shape: could not parse MapLibreRenderer export. "
			"Try upgrading/downgrading anymap-ts, or update the patcher."
		)

	renderer_id = id_match.group(1)
	injection = f"const MapLibreRenderer={renderer_id};"
	return content[: match.start()] + injection + export_block + content[match.end() :]


def _patched_maplibre_esm_path() -> Path:
	"""Return a Path to a patched `maplibre.js` ESM file.

	The patched file is generated once per anymap-ts version + source bundle stamp
	(size/mtime) and stored in the OS temp directory.
	"""
	MapLibreMap, STATIC_DIR = _require_anymap_ts()
	orig_path = STATIC_DIR / "maplibre.js"
	stat = orig_path.stat()
	try:
		anymap_version = importlib.metadata.version("anymap-ts")
	except Exception:  # pragma: no cover
		anymap_version = "unknown"

	# IMPORTANT: bump this when changing the injected JS patch.
	patch_id = "move_marker_v5_regex_export"

	cache_name = (
		f"anymap_ts_maplibre_patched_move_marker_"
		f"{patch_id}_v{anymap_version}_s{stat.st_size}_m{stat.st_mtime_ns}.js"
	)
	out_path = Path(tempfile.gettempdir()) / cache_name
	if out_path.exists():
		return out_path

	content = orig_path.read_text(encoding="utf-8")
	if "__anymap_moveMarker_patched" in content or "anymap:moveMarkerAck" in content:
		# Already patched (or upstream added an equivalent patch marker).
		return orig_path

	content = _inject_renderer_binding(content)

	patch_js = r"""
;(()=>{
	try{
		const proto = (typeof MapLibreRenderer !== 'undefined' && MapLibreRenderer.prototype) ? MapLibreRenderer.prototype : null;
		if(!proto || proto.__anymap_moveMarker_patched) return;
		proto.__anymap_moveMarker_patched = true;

		const origRegisterMethods = proto.registerMethods;
		proto.registerMethods = function(){
			origRegisterMethods.call(this);
			try{
				this.registerMethod("moveMarker", this.handleMoveMarker.bind(this));
			}catch(_e){}
		};

		proto.handleMoveMarker = function(t,e){
			if(!this.map) return;
			let lng = null;
			let lat = null;
			if(Array.isArray(t) && t.length >= 2){
				lng = t[0];
				lat = t[1];
			}
			const id = e && e.id;
			if(id == null){
				console.warn("[anymap-ts patch] moveMarker called without id");
				return;
			}
			const existing = this.markersMap && this.markersMap.get(id);
			if(existing){
				if(lng != null && lat != null) existing.setLngLat([lng, lat]);
				// Send a single ack per widget instance to avoid flooding `_js_events`.
				if(!this.__anymap_moveMarkerAckSent){
					this.__anymap_moveMarkerAckSent = true;
					try{ this.sendEvent && this.sendEvent("anymap:moveMarkerAck", {id, lng, lat}); }catch(_e){}
				}
				return;
			}
			// Fall back to creating the marker using upstream logic.
			if(typeof this.handleAddMarker === 'function'){
				this.handleAddMarker(t, e || {id});
				if(!this.__anymap_moveMarkerAckSent){
					this.__anymap_moveMarkerAckSent = true;
					try{ this.sendEvent && this.sendEvent("anymap:moveMarkerAck", {id, lng, lat}); }catch(_e){}
				}
			}
		};
	}catch(err){
		console.error("[anymap-ts patch] moveMarker init failed", err);
	}
})();
"""

	out_path.write_text(content + patch_js, encoding="utf-8")
	return out_path


class LiveMapLibreMap:  # populated below
	pass


# Define the subclass only if anymap-ts is available.
_MapLibreMap, _STATIC_DIR = None, None
try:  # pragma: no cover
	_MapLibreMap, _STATIC_DIR = _require_anymap_ts()
except Exception:
	_MapLibreMap = None

if _MapLibreMap is not None:  # pragma: no cover
	class LiveMapLibreMap(_MapLibreMap):
		"""A MapLibreMap with a `move_marker()` method for incremental updates."""

		def __init__(self, *args, **kwargs):
			# anywidget expects `_esm` to contain JS *source*, not a filesystem path.
			# Use FileContents so `str(self._esm)` resolves to the file contents.
			from anywidget._file_contents import FileContents

			self._esm = FileContents(_patched_maplibre_esm_path(), start_thread=False)
			super().__init__(*args, **kwargs)

			# `moveMarker` is a runtime-patched JS method; some notebook frontends or
			# caching modes may ignore it. We detect support via a JS -> Python ack
			# event, and fall back to remove+add marker updates until confirmed.
			self._move_marker_supported: Optional[bool] = None
			self._move_marker_ack_count: int = 0
			self._marker_style: Dict[str, Dict[str, Optional[str]]] = {}

			def _on_ack(_data):
				self._move_marker_supported = True
				self._move_marker_ack_count += 1

			self.on_map_event("anymap:moveMarkerAck", _on_ack)

		def move_marker(
			self,
			marker_id: str,
			lnglat: Tuple[float, float],
			*,
			color: Optional[str] = None,
			popup: Optional[str] = None,
		) -> None:
			"""Move an existing marker in-place (or create it if missing)."""
			lng, lat = lnglat

			style = self._marker_style.get(marker_id, {"color": None, "popup": None})
			if color is not None:
				style["color"] = color
			if popup is not None:
				style["popup"] = popup
			self._marker_style[marker_id] = style

			kwargs = {"id": marker_id}
			if style.get("color") is not None:
				kwargs["color"] = style["color"]
			if style.get("popup") is not None:
				kwargs["popup"] = style["popup"]

			# Try the patched in-place move first (fast/smooth).
			self.call_js_method("moveMarker", lng, lat, **kwargs)

			# If support hasn't been confirmed yet, also do a guaranteed fallback.
			# Once the frontend sends an ack event, we stop doing this.
			if self._move_marker_supported is not True:
				try:
					self.remove_marker(marker_id)
					self.add_marker(
						lng,
						lat,
						name=marker_id,
						color=style.get("color") or "#3388ff",
						popup=style.get("popup"),
					)
				except Exception:
					# Never let UI updates crash a simulation loop.
					pass
