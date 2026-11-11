"""Baut avatar.svg (9:16, ganze Figur) aus den Teilen in parts/.

Aufruf:  python3 build_avatar.py
"""
from pathlib import Path

HERE = Path(__file__).parent
O = "#2B2B2B"      # Outline
SK = "#F2C29B"     # Haut
NEON_PINK, NEON_GREEN, NEON_BLUE, NEON_YELLOW = "#FF3FA4", "#39FF6A", "#3FD2FF", "#FFD23F"

defs = (HERE / "parts/defs.frag").read_text()
head = (HERE / "parts/head.frag").read_text()


def limb(d, w, col):
    """Gliedmaße als dicke Linie mit Outline."""
    return (f'<path d="{d}" fill="none" stroke="{O}" stroke-width="{w + 12}" stroke-linecap="round" stroke-linejoin="round"/>\n'
            f'  <path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def drop(x, y):
    return f'<path d="M{x} {y} q-9 16 0 22 q9 -6 0 -22z"/>'


# Beine (kürzer, Oberschenkel kräftiger) – je ein geschlossener Umriss
LEG_L = "M462 1020 C462 1110 476 1190 490 1250 C496 1320 500 1380 502 1430 L522 1430 C522 1380 522 1320 526 1250 C532 1190 538 1130 538 1065 Z"
LEG_R = "M618 1020 C618 1110 604 1190 590 1250 C584 1320 580 1380 578 1430 L558 1430 C558 1380 558 1320 554 1250 C548 1190 542 1130 542 1065 Z"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
  {defs}
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5EC4F0"/><stop offset="1" stop-color="#CDEFFB"/></linearGradient>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2FA4C9"/><stop offset="1" stop-color="#1C7FA6"/></linearGradient>
    <pattern id="net" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <path d="M0 0 H16 M0 0 V16" stroke="#1E1E1E" stroke-width="2.5"/>
    </pattern>
  </defs>

  <!-- Himmel, Sonne, Wolken, Möwen -->
  <rect width="1080" height="1920" fill="url(#sky)"/>
  <circle cx="170" cy="190" r="110" fill="#FFFFFF" opacity="0.35"/>
  <circle cx="170" cy="190" r="78" fill="{NEON_YELLOW}" stroke="{O}" stroke-width="6"/>
  <g fill="#FFFFFF" opacity="0.9">
    <ellipse cx="900" cy="560" rx="80" ry="22"/><ellipse cx="945" cy="543" rx="45" ry="25"/>
    <ellipse cx="120" cy="620" rx="60" ry="16"/>
  </g>
  <g fill="none" stroke="{O}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M820 330 q18 -18 34 0 q16 -18 34 0"/>
    <path d="M900 420 q12 -12 24 0 q12 -12 24 0"/>
  </g>

  <!-- Meer -->
  <rect x="0" y="1060" width="1080" height="860" fill="url(#sea)"/>
  <path d="M0 1060 H1080" stroke="{O}" stroke-width="5"/>
  <g fill="none" stroke="#BFEFFF" stroke-width="5" stroke-linecap="round">
    <path d="M60 1130 q20 -12 40 0 q20 12 40 0"/><path d="M700 1110 q20 -12 40 0 q20 12 40 0"/>
    <path d="M820 1300 q20 -12 40 0 q20 12 40 0"/><path d="M90 1320 q20 -12 40 0"/>
  </g>

  <!-- treibender Schwimm-Flamingo (halb platt) -->
  <g stroke="{O}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">
    <ellipse cx="900" cy="1205" rx="95" ry="30" fill="#FF8FC2"/>
    <ellipse cx="900" cy="1200" rx="50" ry="12" fill="#2A8DB5"/>
    <path d="M960 1190 C990 1150 975 1110 950 1110 C930 1110 925 1135 940 1140" fill="none" stroke="{O}" stroke-width="22"/>
    <path d="M960 1190 C990 1150 975 1110 950 1110 C930 1110 925 1135 940 1140" fill="none" stroke="#FF8FC2" stroke-width="12"/>
    <path d="M936 1132 l-18 10 l14 6 z" fill="{O}"/>
    <circle cx="952" cy="1122" r="3" fill="{O}" stroke="none"/>
  </g>
  <path d="M790 1232 q20 -10 40 0 M960 1236 q20 -10 40 0" fill="none" stroke="#BFEFFF" stroke-width="4" stroke-linecap="round"/>

  <!-- ihr zweiter Sneaker treibt im Meer -->
  <g transform="translate(120 0) rotate(-14 260 1180)" stroke="{O}" stroke-width="5" stroke-linejoin="round">
    <path d="M230 1160 L270 1160 L272 1186 L204 1190 C196 1190 198 1174 212 1172 Z" fill="#FFFFFF"/>
    <rect x="198" y="1186" width="78" height="18" rx="6" fill="{NEON_GREEN}"/>
  </g>
  <path d="M300 1212 q20 -10 40 0 q20 10 40 0 q20 -10 40 0" fill="none" stroke="#BFEFFF" stroke-width="4" stroke-linecap="round"/>

  <!-- Insel -->
  <path d="M-40 1930 C20 1420 220 1330 540 1330 C860 1330 1060 1420 1120 1930 Z" fill="#F4D58D" stroke="{O}" stroke-width="6"/>
  <g fill="#D9B46A"><circle cx="160" cy="1800" r="6"/><circle cx="240" cy="1700" r="5"/><circle cx="900" cy="1820" r="6"/><circle cx="820" cy="1880" r="5"/><circle cx="960" cy="1640" r="5"/><circle cx="420" cy="1880" r="5"/><circle cx="560" cy="1820" r="5"/></g>

  <!-- Palme -->
  <g stroke="{O}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">
    <path d="M140 1580 C150 1350 170 1100 230 860 L268 870 C215 1100 190 1350 185 1580 Z" fill="#B07A45"/>
    <path d="M155 1500 l28 4 M160 1400 l28 6 M168 1290 l28 6 M180 1180 l28 8 M195 1070 l28 8 M210 970 l26 8" fill="none" stroke-width="4"/>
    <g fill="#3FA34D">
      <path d="M250 860 C170 800 90 820 30 890 C100 855 170 855 250 860 Z"/>
      <path d="M250 860 C190 750 100 730 40 765 C120 770 190 800 250 860 Z"/>
      <path d="M250 860 C275 750 355 700 435 712 C355 750 295 800 250 860 Z"/>
      <path d="M250 860 C320 825 400 850 445 920 C375 885 320 873 250 860 Z"/>
      <path d="M250 860 C238 780 262 700 308 665 C285 735 272 805 250 860 Z"/>
    </g>
    <circle cx="232" cy="878" r="18" fill="#7A4A26"/><circle cx="264" cy="884" r="18" fill="#7A4A26"/>
    <!-- heruntergefallene Kokosnüsse -->
    <circle cx="225" cy="1590" r="24" fill="#7A4A26"/><circle cx="268" cy="1600" r="20" fill="#7A4A26"/>
  </g>

  <!-- angespülte Rave-Bassbox, halb im Sand -->
  <g transform="rotate(-8 140 1700)" stroke="{O}" stroke-width="6" stroke-linejoin="round">
    <rect x="40" y="1600" width="200" height="230" rx="14" fill="#2E2E38"/>
    <circle cx="140" cy="1660" r="34" fill="#4A4A58"/><circle cx="140" cy="1660" r="12" fill="{O}"/>
    <circle cx="140" cy="1760" r="52" fill="#4A4A58"/><circle cx="140" cy="1760" r="18" fill="{O}"/>
    <path d="M60 1620 l30 40 l-10 20 l26 30" fill="none" stroke="#9AA0B5" stroke-width="4"/>
    <path d="M50 1610 C80 1640 70 1680 95 1700" fill="none" stroke="#2E7D3A" stroke-width="8" stroke-linecap="round"/>
  </g>
  <path d="M10 1800 C80 1770 200 1770 270 1800 L270 1860 L10 1860 Z" fill="#F4D58D"/>
  <path d="M10 1800 C80 1770 200 1770 270 1800" fill="none" stroke="{O}" stroke-width="5" stroke-linecap="round"/>

  <!-- lange, wellige Haare hinten (blond, mit Glanz) -->
  <path d="M540 360 C606 360 658 406 658 462 C660 520 666 580 688 648 C704 700 714 724 716 764 C718 812 742 842 726 892 C712 946 750 986 720 1018 C702 1040 672 1032 664 1008 C650 1034 618 1032 606 1004 L474 1004 C462 1032 430 1034 416 1008 C408 1032 378 1040 360 1018 C330 986 368 946 354 892 C338 842 362 812 364 764 C366 724 376 700 392 648 C414 580 420 520 422 462 C422 406 474 360 540 360 Z"
        fill="#E8C468" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>
  <g fill="none" stroke-linecap="round">
    <path d="M396 700 C384 770 406 830 392 900 C386 930 396 950 392 970" stroke="#C99A3C" stroke-width="5"/>
    <path d="M684 700 C696 770 674 830 688 900 C694 930 684 950 688 970" stroke="#C99A3C" stroke-width="5"/>
    <path d="M420 600 C412 660 400 700 390 760" stroke="#FFF3C4" stroke-width="7"/>
    <path d="M660 600 C668 660 680 700 690 760" stroke="#FFF3C4" stroke-width="7"/>
    <path d="M380 960 C392 990 408 1000 420 990 M700 960 C688 990 672 1000 660 990" stroke="#C99A3C" stroke-width="4"/>
  </g>

  <!-- Beine mit Netzstrumpfhose -->
  <g stroke="{O}" stroke-width="6" stroke-linejoin="round">
    <path d="{LEG_L}" fill="{SK}"/><path d="{LEG_R}" fill="{SK}"/>
  </g>
  <path d="{LEG_L}" fill="url(#net)"/><path d="{LEG_R}" fill="url(#net)"/>
  <path d="M498 1245 l14 -6 M496 1255 l16 -4" stroke="#D9534F" stroke-width="4" stroke-linecap="round"/>

  <!-- linker Fuß: Plateau-Sneaker -->
  <g transform="translate(0 -60)" stroke="{O}" stroke-width="6" stroke-linejoin="round">
    <path d="M494 1484 L530 1484 L534 1520 L444 1525 C434 1525 436 1504 452 1500 Z" fill="#FFFFFF"/>
    <rect x="436" y="1522" width="102" height="26" rx="8" fill="{NEON_GREEN}"/>
    <path d="M492 1494 l20 0 M488 1506 l24 0" fill="none" stroke-width="4"/>
  </g>
  <!-- rechter Fuß: barfuß -->
  <g transform="translate(0 -60)" stroke="{O}" stroke-width="6" stroke-linejoin="round">
    <path d="M554 1484 L582 1484 C586 1510 626 1512 636 1530 C638 1545 626 1550 606 1550 L560 1550 C548 1550 548 1520 554 1484 Z" fill="{SK}"/>
    <path d="M598 1550 v-10 M612 1550 v-12 M625 1548 v-12" fill="none" stroke-width="3"/>
  </g>

  <!-- Shorts (Hüfte breit) -->
  <path d="M486 945 L594 945 C612 972 622 998 622 1028 L628 1072 L558 1080 L540 1040 L522 1080 L452 1072 L458 1028 C458 998 468 972 486 945 Z"
        fill="#2F3E67" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M454 1064 l10 -10 l10 12 l10 -10 l10 12 l10 -10 l10 10 M560 1070 l10 -10 l10 12 l10 -10 l10 12 l10 -10 l8 10" fill="none" stroke="#C9D3EE" stroke-width="4"/>
  <path d="M486 945 L594 945 L597 962 L483 962 Z" fill="#1E2A4A" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>

  <!-- Taille (schmal) -->
  <path d="M478 852 L602 852 C588 878 584 908 596 948 L484 948 C496 908 492 878 478 852 Z" fill="{SK}" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="540" cy="905" r="4" fill="{O}"/>

  <!-- Hals + Schultern (Netzshirt) -->
  <path d="M522 620 L522 715 L558 715 L558 620 Z" fill="#EDB48C" stroke="{O}" stroke-width="6"/>
  <path d="M458 738 C472 716 502 708 540 707 C578 708 608 716 622 738 L614 790 L466 790 Z" fill="{SK}" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M458 738 C472 716 502 708 540 707 C578 708 608 716 622 738 L614 790 L466 790 Z" fill="url(#net)"/>

  <!-- schwarzes Crop-Top (Oberweite betont, kurz) -->
  <path d="M468 744 C500 754 580 754 612 744 C632 762 642 792 636 816 C632 836 622 848 612 854 L468 854 C458 848 448 836 444 816 C438 792 448 762 468 744 Z" fill="#1C1C22" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>
  <path d="M478 748 L482 712 M602 748 L598 712" stroke="#1C1C22" stroke-width="9"/>
  <path d="M540 754 C541 768 539 780 535 790" fill="none" stroke="#3A3A44" stroke-width="3" stroke-linecap="round"/>
  <path d="M462 822 Q496 846 532 834 M548 834 Q584 846 618 822" fill="none" stroke="#3A3A44" stroke-width="3" stroke-linecap="round"/>
  <path d="M470 780 Q482 764 504 762 M610 780 Q598 764 576 762" fill="none" stroke="#4C4C58" stroke-width="5" stroke-linecap="round"/>
  <path d="M472 844 Q540 852 608 844" fill="none" stroke="#3A3A44" stroke-width="3"/>
  <path d="M596 854 l4 -16 l-8 -6 l9 -12" fill="none" stroke="#6A6A78" stroke-width="3.5"/>

  <!-- Knicklicht-Kette -->
  <path d="M518 708 Q540 740 562 708" fill="none" stroke="{O}" stroke-width="12" stroke-linecap="round"/>
  <path d="M518 708 Q540 740 562 708" fill="none" stroke="{NEON_GREEN}" stroke-width="6" stroke-linecap="round"/>

  <!-- Arme: Hände in die Taille gestemmt -->
  {limb("M464 742 L408 858 L490 910", 25, SK)}
  {limb("M616 742 L672 858 L590 910", 25, SK)}
  <path d="M464 742 L408 858 L490 910 M616 742 L672 858 L590 910" fill="none" stroke="url(#net)" stroke-width="25" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
  <g stroke="{O}" stroke-width="5"><circle cx="492" cy="910" r="17" fill="{SK}"/><circle cx="588" cy="910" r="17" fill="{SK}"/></g>
  <g stroke-linecap="round">
    <path d="M456 878 l18 13" stroke="{O}" stroke-width="12"/><path d="M456 878 l18 13" stroke="{NEON_PINK}" stroke-width="6"/>
    <path d="M624 878 l-18 13" stroke="{O}" stroke-width="12"/><path d="M624 878 l-18 13" stroke="{NEON_BLUE}" stroke-width="6"/>
    <path d="M640 862 l-18 13" stroke="{O}" stroke-width="12"/><path d="M640 862 l-18 13" stroke="{NEON_YELLOW}" stroke-width="6"/>
  </g>

  <!-- Strähnen vorne über den Schultern -->
  <g stroke="{O}" stroke-width="5" stroke-linejoin="round">
    <path d="M436 520 C426 600 452 680 436 760 C424 830 452 900 434 955 C474 935 490 885 478 828 C466 768 494 700 482 620 C478 580 476 545 470 520 Z" fill="#EDCB72"/>
    <path d="M644 520 C654 600 628 680 644 760 C656 830 628 900 646 955 C606 935 590 885 602 828 C614 768 586 700 598 620 C602 580 604 545 610 520 Z" fill="#EDCB72"/>
  </g>
  <g fill="none" stroke-linecap="round">
    <path d="M454 660 C444 730 466 790 450 860" stroke="#FFF3C4" stroke-width="5"/>
    <path d="M626 660 C636 730 614 790 630 860" stroke="#FFF3C4" stroke-width="5"/>
  </g>

{head}
  <!-- Flaschenpost mit SOS -->
  <g transform="rotate(-24 790 1640)" stroke="{O}" stroke-width="5" stroke-linejoin="round">
    <path d="M740 1620 h90 q20 0 20 20 q0 20 -20 20 h-90 q-14 0 -14 -20 q0 -20 14 -20 z" fill="#9FE3C9" opacity="0.9"/>
    <rect x="848" y="1630" width="34" height="20" rx="4" fill="#9FE3C9"/>
    <rect x="880" y="1628" width="14" height="24" rx="3" fill="#B07A45"/>
    <rect x="752" y="1630" width="66" height="20" rx="3" fill="#FFF6DC" stroke-width="3"/>
  </g>
  <text x="784" y="1652" text-anchor="middle" transform="rotate(-24 790 1640)" font-family="'Arial Black', 'DejaVu Sans', sans-serif" font-weight="900" font-size="15" fill="#D64545">SOS</text>

  <!-- Handy: kaputt, kein Netz -->
  <g transform="rotate(18 420 1700)" stroke="{O}" stroke-width="5" stroke-linejoin="round">
    <rect x="380" y="1640" width="80" height="140" rx="12" fill="#1F1F25"/>
    <rect x="388" y="1652" width="64" height="116" rx="6" fill="#3A4256"/>
    <path d="M396 1660 l22 30 l-8 18 l26 22 M418 1690 l26 -14" fill="none" stroke="#C9D3EE" stroke-width="3"/>
  </g>
  <text x="420" y="1755" text-anchor="middle" transform="rotate(18 420 1700)" font-family="'DejaVu Sans', Arial, sans-serif" font-weight="700" font-size="12" fill="#FF6B6B">Kein Netz</text>

  <!-- Knicklicht im Sand -->
  <path d="M330 1600 l40 -30" stroke="{O}" stroke-width="14" stroke-linecap="round"/>
  <path d="M330 1600 l40 -30" stroke="{NEON_BLUE}" stroke-width="7" stroke-linecap="round"/>

  <!-- Seestern -->
  <path d="M900 1700 l12 26 l28 2 l-22 18 l8 28 l-26 -16 l-26 16 l8 -28 l-22 -18 l28 -2 z" fill="#FF8A5C" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>

  <!-- grummelige Krabbe neben ihr -->
  <g transform="translate(400 630)" stroke="{O}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
    <path d="M262 852 l-22 -20 M262 862 l-26 -6 M330 852 l22 -20 M330 862 l26 -6" fill="none"/>
    <path d="M268 832 C250 800 230 800 228 815 C240 812 250 820 255 832 Z" fill="#E8553E"/>
    <path d="M324 832 C342 800 362 800 364 815 C352 812 342 820 337 832 Z" fill="#E8553E"/>
    <ellipse cx="296" cy="848" rx="40" ry="24" fill="#E8553E"/>
    <path d="M284 826 v-14 M308 826 v-14" fill="none"/>
    <circle cx="284" cy="810" r="6" fill="#FFFFFF"/><circle cx="308" cy="810" r="6" fill="#FFFFFF"/>
    <circle cx="281" cy="811" r="2.5" fill="{O}" stroke="none"/><circle cx="305" cy="811" r="2.5" fill="{O}" stroke="none"/>
    <path d="M286 856 q10 -6 20 0" fill="none" stroke-width="4"/>
  </g>
</svg>
'''

(HERE / "avatar.svg").write_text(svg)
print("avatar.svg geschrieben")
