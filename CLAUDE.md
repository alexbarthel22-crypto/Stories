# Regeln für „Heute ist Alex …“ (TikTok-Serie)

- Neue Folgen zuerst mit Vorschaustimme (tools/preview.sh), Gemini erst nach Freigabe.
- Stimme: gemini-3.8-flash-tts, Puck, TTS_PROFILE="pickme"; tighten 1.08 0.22 + tools/match_level.py (wie Pick-me-Boy); kein anderes Modell.
- „Alex“ deutsch aussprechen (GEMINI_LINE_TEXT mit „Aleks“), Verkündung ohne Stottern, kurze Pause danach (INTRO_LEN 3.3).
- **Nach jeder Gemini-Vertonung immer Video + Thumbnail schicken und die Beschreibung (5 Hashtags inkl. #heuteistalex) im Chat mitschicken**; Beschreibung auch in branding/tiktok_texte.md.
- Nur Situationen mit Freunden/Bros (Alltag Jugendlicher 2026), keine Szenen zwischen Alex und seiner Mutter.
- Lustigste Fakten zuerst, Box-Animationen (enter/move) pro Szene variieren, nichts darf Text/Emojis überdecken, Textboxen nie in Hintergrundfarbe, Abstand zum Boxrand, Sicherheitsbereich beachten.
- Schluss: „Kennst du auch einen/eine X? Markier sie oder ihn!“
