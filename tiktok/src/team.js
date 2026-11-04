// ---------- Die restlichen 8 Spieler ----------
const HAIR = {
  mullet: c => `<path d="M100 210 Q100 70 250 70 Q400 70 400 210 Q380 140 250 140 Q120 140 100 210Z" fill="${c}"/>`,
  mulletBack: c => `<path d="M100 220 Q80 330 130 360 L150 250Z M400 220 Q420 330 370 360 L350 250Z" fill="${c}" stroke="${K}" stroke-width="6"/>`,
  bald: () => ``,
  pig: c => `<path d="M100 220 Q100 68 250 68 Q400 68 400 220 Q330 120 250 150 Q170 120 100 220Z" fill="${c}"/>`,
  cap: c => `<path d="M104 170 Q120 66 250 66 Q380 66 396 170 Z" fill="${c}"/>`,
  bun: c => `<path d="M100 200 Q100 74 250 74 Q400 74 400 200 Q330 128 250 136 Q170 128 100 200Z" fill="${c}"/>`,
  afro: c => ``,
  mohawk: c => `<path d="M215 70 L285 70 L282 150 L218 150Z" fill="${c}"/>`,
  curly: c => `<path d="M100 210 Q100 70 250 70 Q400 70 400 210 Q370 150 250 150 Q130 150 100 210Z" fill="${c}"/>`,
};

function roster() {
  return [
    // #7 der Lange mit Vokuhila und Stirnband
    {num: '7', skin: '#F5D3AE', hair: HAIR.mullet('#B5651D'), behind: HAIR.mulletBack('#B5651D'),
     hairOver: `<rect x="112" y="130" width="276" height="26" rx="8" fill="#E8432E" stroke="${K}" stroke-width="6" transform="rotate(-4 250 143)"/>`},
    // #5 der Bulldozer: Glatze, roter Vollbart
    {num: '5', skin: '#F0C49C', hair: `<path d="M110 250 Q122 340 180 356 Q250 384 320 356 Q378 340 390 250 Q380 310 330 318 Q250 296 170 318 Q120 310 110 250Z" fill="#C0501E"/>`,
     hairOver: `<path d="M190 100 q20 -12 40 -4" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".6"/>`, mood: 'talk', mouth: .4},
    // #10 die Spielmacherin mit Zoepfen
    {num: '10', skin: '#E9B98F', hair: HAIR.pig('#3A2416'),
     behind: `<circle cx="96" cy="300" r="40" fill="#3A2416" stroke="${K}" stroke-width="7"/><circle cx="404" cy="300" r="40" fill="#3A2416" stroke="${K}" stroke-width="7"/>`,
     hairOver: `<circle cx="112" cy="250" r="12" fill="#FF3FA4" stroke="${K}" stroke-width="4"/><circle cx="388" cy="250" r="12" fill="#FF3FA4" stroke="${K}" stroke-width="4"/>`},
    // #8 der Juengste: Cap und Zahnspange
    {num: '8', skin: '#F5D3AE', hair: HAIR.cap('#E8432E'), mood: 'talk', mouth: .6,
     hairOver: `<path d="M110 168 Q60 168 40 186 L250 186 Z" fill="#E8432E" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>`,
     face: `<path d="M222 312 H278" stroke="#B8B8B8" stroke-width="6"/>`},
    // #6 der Hipster: Dutt, Brille
    {num: '6', skin: '#C98E62', hair: HAIR.bun('#1C1C1C'),
     hairOver: `<circle cx="250" cy="74" r="36" fill="#1C1C1C" stroke="${K}" stroke-width="7"/>`,
     face: `<g fill="none" stroke="${K}" stroke-width="9"><rect x="150" y="180" width="92" height="72" rx="14"/><rect x="258" y="180" width="92" height="72" rx="14"/><path d="M242 206 h16"/></g>`},
    // #11 der Coole: Afro und Sonnenbrille
    {num: '11', skin: '#8D5A3B', hair: '', browCol: '#111',
     behindHead: `<circle cx="250" cy="150" r="170" fill="#1E1410" stroke="${K}" stroke-width="8"/>`,
     eyes: `<path d="M150 192 H350 L340 232 Q300 256 260 232 L250 214 L240 232 Q200 256 160 232 Z" fill="#111" stroke="${K}" stroke-width="5"/><path d="M175 205 l20 -8 M285 205 l20 -8" stroke="#fff" stroke-width="5" opacity=".6"/>`, noBrows: true},
    // #3 der Punk: gruener Irokese
    {num: '3', skin: '#F5D3AE', hair: HAIR.mohawk('#4BD44B'),
     hairOver: `<path d="M220 90 L230 20 L250 80 L262 14 L274 80 L292 30 L284 96" fill="#4BD44B" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>`,
     face: `<circle cx="388" cy="262" r="8" fill="none" stroke="#C0C0C0" stroke-width="5"/>`},
    // #14 der Traeumer: Locken und Kopfhoerer
    {num: '14', skin: '#E6B48A', hair: HAIR.curly('#7A4A22'),
     hairOver: `<path d="M120 90 q20 -30 50 -10 q20 -30 50 -6 q30 -26 60 -2 q30 -22 54 6 q30 -6 40 20" fill="none" stroke="#7A4A22" stroke-width="30" stroke-linecap="round"/>
       <path d="M96 240 Q80 60 250 50 Q420 60 404 240" fill="none" stroke="${K}" stroke-width="16"/>
       <rect x="70" y="200" width="54" height="84" rx="20" fill="#2F7FD8" stroke="${K}" stroke-width="7"/><rect x="376" y="200" width="54" height="84" rx="20" fill="#2F7FD8" stroke="${K}" stroke-width="7"/>`},
  ];
}

function teamPlayer(i, t) {
  const r = roster()[i];
  const o = Object.assign({mood: 'smile', blink: blinkAt(t, i * 0.37)}, r);
  return (r.behindHead || '') + player(o);
}

// 11 Spieler + Trainer + Pichu: zwei Reihen
function fullTeam(t, baseBack, baseFront, s, m, rolling) {
  let back = '', front = '';
  const backRow = [[0, 140], [1, 290], [2, 440], [3, 590], [4, 740], [5, 890]];
  backRow.forEach(([i, x]) => back += place(teamPlayer(i, t), x, baseBack, s * 0.92));
  const fr = [
    [vlad({blink: blinkAt(t, .4)}), 110], [opa({blink: blinkAt(t, 1.1)}), 250],
    [teamPlayer(6, t), 390], [busguy({blink: blinkAt(t, 2)}), 790], [teamPlayer(7, t), 910]];
  fr.forEach(([svg, x]) => front += place(svg, x, baseFront, s));
  front += place(coach({mouth: m, blink: blinkAt(t)}), 590, baseFront + 6, s * 1.1);
  const dog = place(corgi({wag: Math.sin(t * 14), blink: blinkAt(t, 1.7)}), 500, baseFront + 120, 0.34);
  return back + front + dog;
}

