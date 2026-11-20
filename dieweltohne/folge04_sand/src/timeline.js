// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet jedes Sandkorn der Welt – auch der Sand in Glas, Beton und Computerchips.
// Als er zurückkommt, ist er nur noch Sand: kein Glas, kein Beton, keine Chips.
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},        // Handy filmt Beachvolleyball am Strand
  {id: 'wait', t0: 3.5, t1: 10},        // Beachvolleyball, Countdown läuft
  {id: 'beach_drop', t0: 10, t1: 17},   // Stufe 1: Sand weg, alle fallen einen Meter tief
  {id: 'gaming', t0: 17, t1: 24},       // Stufe 2: Zocken – Bildschirmglas und Chips verschwinden
  {id: 'skywalk', t0: 24, t1: 31},      // Stufe 3: Glasboden über der Schlucht verschwindet
  {id: 'stadium', t0: 31, t1: 39},      // Stufe 4: Betontribünen im Stadion zerbröseln
  {id: 'dubai', t0: 39, t1: 47},        // Stufe 5: Palmeninsel versinkt, Wolkenkratzer stürzen
  {id: 'flood', t0: 47, t1: 57},        // Stufe 6: Dünen weg – die Nordsee flutet die Niederlande
  {id: 'sandcity', t0: 57, t1: 68},     // Stufe 7: Sand zurück – aber nur als Sand
  {id: 'aerial', t0: 68, t1: 80},       // Stufe 7: Luftbild – die Stadt ist eine Wüste
  {id: 'hand', t0: 80, t1: 90},         // Stufe 7: Handy zerrinnt in der Hand
];

export const VANISH = 10.0;   // Sand verschwindet
export const RETURN = 57.0;   // Sand zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.3], [24, 8.4], [31, 7.4], [39, 6.0], [47, 4.0], [57, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const SKY_DROP = 26.0, STAND_FALL = 33.5, TOWER_FALL = 42.5, DUNE_BREAK = 48.5, CRUMBLE = 59.0;

export const STAGES = ['HARMLOS', 'ÄRGERLICH', 'GEFÄHRLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {beach_drop: 1, gaming: 2, skywalk: 3, stadium: 4, dubai: 5, flood: 6, sandcity: 7, aerial: 7, hand: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Sand ist überall. Und niemand denkt darüber nach.'],
  [7.0, 9.8, 'Bis er für zehn Sekunden verschwindet.'],
  [10.5, 13.3, 'Am Strand: ein Meter freier Fall.'],
  [13.5, 16.8, 'Peinlich. Aber Sand steckt nicht nur am Strand.'],
  [17.4, 20.4, 'Glas wird aus Sand gemacht. Computerchips auch.'],
  [20.6, 23.8, 'Bildschirm weg. Grafikkarte weg. Match verloren.'],
  [24.4, 27.4, 'Der Glasboden hält 200 Meter über der Schlucht.'],
  [27.6, 30.8, 'Glas. Aus Sand.'],
  [31.4, 34.6, 'Beton besteht größtenteils aus Sand und Kies.'],
  [34.8, 38.8, 'Ohne Sand hält keine Tribüne. 60.000 Fans.'],
  [39.4, 42.4, 'Dubai hat ganze Inseln aus Sand aufgeschüttet.'],
  [42.6, 46.8, 'Und Wolkenkratzer aus Beton gebaut.'],
  [47.4, 50.6, 'Ein Viertel der Niederlande liegt unter dem Meeresspiegel.'],
  [50.8, 53.8, 'Geschützt von Dünen. Aus Sand.'],
  [54.0, 56.8, 'Die Nordsee wartet nicht zehn Sekunden.'],
  [57.4, 60.2, 'Der Sand ist zurück.'],
  [60.4, 63.8, 'Aber nicht als Glas. Nicht als Beton. Nur als Sand.'],
  [64.0, 67.8, 'Jedes Fenster, jedes Haus, jede Brücke der Welt.'],
  [68.4, 72.0, 'Sand ist nach Wasser der meistgenutzte Rohstoff der Welt.'],
  [72.2, 75.8, 'Wir haben unsere ganze Welt daraus gebaut.'],
  [76.0, 79.8, 'Jetzt liegt sie in Haufen auf der Straße.'],
  [80.4, 84.2, 'Zehn Sekunden ohne Sand.'],
  [84.4, 89.8, 'Und die ganze Welt ist eine Wüste.'],
];

// Nur für die übernommene Strandszene (Kompatibilität)
export const DARK = 999;
export function lightLeft() { return 0; }
