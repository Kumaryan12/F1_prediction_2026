export default function MonzaCircuit() {
  return (
    <div className="circuit-dossier">
      <div className="circuit-topline"><span className="eyebrow">Circuit dossier / 01</span><span className="circuit-badge">Low downforce</span></div>
      <div className="circuit-title"><h2>MONZA</h2><span>EST.<br /><b>1922</b></span></div>
      <p className="circuit-subtitle">Autodromo Nazionale Monza</p>
      <svg viewBox="0 0 520 310" className="monza-map" role="img" aria-label="Schematic of Monza circuit, showing Rettifilo, Lesmo, Ascari and Curva Alboreto">
        <defs>
          <pattern id="map-grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="#ffffff" strokeOpacity=".055" strokeWidth="1" /></pattern>
          <path id="monza-layout" d="M108 260 L174 174 L185 158 L179 151 L190 148 L216 116 Q247 76 304 56 L368 35 Q383 31 388 44 L394 58 L383 67 L393 81 Q401 94 389 105 L360 129 Q350 137 340 132 L325 124 L232 194 L225 192 L216 208 L205 208 L156 275 Q143 298 120 287 Q103 278 108 260Z" />
        </defs>
        <rect width="520" height="310" fill="url(#map-grid)" />
        <path d="M144 261C286 301 471 200 414 81C388 27 282 49 211 130" fill="none" stroke="#587566" strokeWidth="1" strokeDasharray="4 5" opacity=".4" />
        <use href="#monza-layout" fill="none" stroke="#728779" strokeOpacity=".15" strokeWidth="21" strokeLinejoin="round" />
        <use href="#monza-layout" fill="none" stroke="#efece2" strokeWidth="6" strokeLinejoin="round" />
        <path d="M108 260L174 174M216 116Q247 76 304 56" fill="none" stroke="#ef554c" strokeWidth="6" />
        <path d="M325 124L232 194L225 192L216 208L205 208L156 275" fill="none" stroke="#72b590" strokeWidth="6" strokeLinejoin="round" />
        <g fill="#b4c5b8" fontFamily="monospace" fontSize="9" letterSpacing="1">
          <path d="M181 151H113L97 135M389 83H425L440 68M223 199H291L306 213M124 289H208" fill="none" stroke="#728779" strokeWidth=".75" />
          <text x="30" y="128">01 / RETTIFILO</text><text x="405" y="59">LESMO</text><text x="304" y="224">ASCARI</text><text x="215" y="293">CURVA ALBORETO</text>
        </g>
        <g transform="translate(133 220) rotate(38)"><rect width="12" height="12" fill="#f4f0e8" /><path d="M0 0H6V6H12V12H6V6H0Z" fill="#11281e" /></g>
        <text x="56" y="222" fill="#f4f0e8" fontSize="8" fontFamily="monospace" letterSpacing="1">START / FINISH</text>
        <circle cx="280" cy="66" r="5" fill="#ef554c" stroke="#11281e" strokeWidth="2" className="circuit-marker" />
      </svg>
      <div className="circuit-legend"><span><i className="legend-red" />Sector 1</span><span><i className="legend-ivory" />Sector 2</span><span><i className="legend-green" />Sector 3</span><span className="ml-auto">Schematic ↗</span></div>
      <div className="circuit-bottom"><div><span className="eyebrow">Circuit character</span><strong>Built for speed.</strong></div><span className="circuit-coordinate">45°37′ N<br />09°17′ E</span></div>
    </div>
  );
}
