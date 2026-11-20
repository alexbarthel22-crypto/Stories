// Zentrale Zeitleiste (Sekunden im Video). Die Tonmischung (mix.py) nutzt dieselben Zeiten.
// Aufbau: Für 10 Sekunden verschwindet Taylor Swift – und mit ihr jeder Song, den sie je gesungen hat.
// Sie selbst ist nie zu sehen: nur ihre Abwesenheit (leere Bühne, stummer Player, Text).
export const FPS = 30, DURATION = 90;

export const SHOTS = [
  {id: 'intro', t0: 0, t1: 3.5},         // Handy-Player: Lieblingssong läuft
  {id: 'wait', t0: 3.5, t1: 10},         // Zimmer: sie singt in die Haarbürste
  {id: 'room_drop', t0: 10, t1: 17},     // Stufe 1: Musik weg, sie singt allein weiter, Bruder filmt
  {id: 'party', t0: 17, t1: 24},         // Stufe 2: Schulparty, Musik weg, Stille auf der Tanzfläche
  {id: 'concert', t0: 24, t1: 32},       // Stufe 3: Stadionkonzert, die Bühne ist leer
  {id: 'stadium', t0: 32, t1: 40},       // Stufe 4: 70.000 Fans stürmen nach vorn
  {id: 'server', t0: 40, t1: 48},        // Stufe 5: Rechenzentrum unter der Last der Suchanfragen
  {id: 'seismo', t0: 48, t1: 57},        // Stufe 6: Erdbebenwarte, Fans weltweit auf der Straße
  {id: 'comeback', t0: 57, t1: 66},      // Stufe 7: Sie ist zurück – das Stadion explodiert vor Freude
  {id: 'quake', t0: 66, t1: 75},         // Stufe 7: das stärkste Fan-Beben aller Zeiten
  {id: 'viral', t0: 75, t1: 90},         // Stufe 7: das Video des Bruders geht viral
];

export const VANISH = 10.0;   // Taylor Swift verschwindet
export const RETURN = 57.0;   // zurück (Weltzeit 10 s, über die Einstellungen gedehnt)

const WK = [[10, 10], [17, 9.3], [24, 8.5], [32, 7.4], [40, 6.0], [48, 4.0], [57, 0]];
export function worldLeft(T) {
  if (T <= WK[0][0]) return 10;
  for (let i = 1; i < WK.length; i++) if (T <= WK[i][0]) {
    const [a, va] = WK[i - 1], [b, vb] = WK[i];
    return va + (vb - va) * (T - a) / (b - a);
  }
  return 0;
}
// Wichtige Momente (Videozeit) für Bild und Ton
export const PARTY_STOP = 18.2, MIC_DROP = 24.6, SURGE = 34.5, BARRIER = 36.8, OVERLOAD = 43.5, SPARK = 45.2, NEEDLE = 50.0, JUMP = 59.0, SNAP = 69.0;

export const STAGES = ['HARMLOS', 'PEINLICH', 'UNHEIMLICH', 'KRITISCH', 'KATASTROPHE', 'UNAUFHALTSAM', 'WELTUNTERGANG'];
export const STAGE_OF = {room_drop: 1, party: 2, concert: 3, stadium: 4, server: 5, seismo: 6, comeback: 7, quake: 7, viral: 7};

export const CAPTIONS = [
  [4.0, 6.8, 'Ihre Songs laufen gerade überall auf der Welt.'],
  [7.0, 9.8, 'Bis Taylor Swift für zehn Sekunden verschwindet.'],
  [10.5, 13.3, 'Mit ihr verschwindet jeder Song, den sie je gesungen hat.'],
  [13.5, 16.8, 'Blöd nur, dass du gerade laut mitsingst.'],
  [17.4, 20.4, 'Schulparty. 300 Leute auf der Tanzfläche.'],
  [20.6, 23.8, 'Und plötzlich: nur noch Stille.'],
  [24.4, 27.6, 'Ein Stadionkonzert. 70.000 Fans.'],
  [27.8, 31.8, 'Die Band spielt weiter. Aber die Bühne ist leer.'],
  [32.4, 35.8, '2023 in Seattle tanzten ihre Fans so heftig, dass Seismografen ein Beben maßen.'],
  [36.0, 39.8, 'Jetzt drängen 70.000 Menschen gleichzeitig nach vorn.'],
  [40.4, 43.6, 'Weltweit suchen alle gleichzeitig: Wo ist Taylor?'],
  [43.8, 47.8, 'So viele Anfragen hält kein Rechenzentrum aus.'],
  [48.4, 51.6, 'Fans auf der ganzen Welt laufen auf die Straße.'],
  [51.8, 54.4, 'Die Erdbebenwarten schlagen Alarm.'],
  [54.6, 56.8, 'Noch eine Sekunde.'],
  [57.4, 60.2, 'Taylor Swift ist zurück.'],
  [60.4, 65.8, '70.000 Fans springen gleichzeitig vor Freude.'],
  [66.4, 70.2, 'Das stärkste Fan-Beben, das je gemessen wurde.'],
  [70.4, 74.8, 'Weltweit. In jeder Stadt gleichzeitig.'],
  [75.4, 78.8, 'Alles ist wieder normal.'],
  [79.0, 82.6, 'Fast alles. Dein Bruder hat das Video hochgeladen.'],
  [82.8, 85.8, 'Zehn Millionen Aufrufe.'],
  [86.0, 89.6, 'Zehn Sekunden ohne Taylor Swift. Dein persönlicher Weltuntergang.'],
];
