// Film-Look: Umgebungsverdeckung, Bloom, Tiefenunschärfe, Filmkorn, Vignette, leichte chromatische Aberration
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {GTAOPass} from 'three/addons/postprocessing/GTAOPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {BokehPass} from 'three/addons/postprocessing/BokehPass.js';
import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';

const FilmShader = {
  uniforms: {tDiffuse: {value: null}, time: {value: 0}, grain: {value: 0.05}, vig: {value: 0.32}, ca: {value: 0.0018}, lift: {value: 0.0}},
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float time, grain, vig, ca, lift; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)) + time * 13.37) * 43758.5453); }
    void main(){
      vec2 d = vUv - 0.5; float r2 = dot(d, d);
      vec3 c; c.r = texture2D(tDiffuse, vUv + d * ca * 1.0).r; c.g = texture2D(tDiffuse, vUv).g; c.b = texture2D(tDiffuse, vUv - d * ca).b;
      c *= 1.0 - vig * smoothstep(0.08, 0.55, r2 * 1.6);
      float l = dot(c, vec3(0.299, 0.587, 0.114));
      float n = (h(vUv * vec2(1080.0, 1920.0)) - 0.5) * grain * (1.2 - l);
      c += n + lift;
      gl_FragColor = vec4(c, 1.0);
    }`,
};

export function makePost(renderer, W = 1080, H = 1920) {
  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, {type: THREE.HalfFloatType, samples: 4}));
  composer.setPixelRatio(1); composer.setSize(W, H);
  const rp = new RenderPass(new THREE.Scene(), new THREE.PerspectiveCamera());
  const ao = new GTAOPass(new THREE.Scene(), new THREE.PerspectiveCamera(), W / 2, H / 2);
  ao.output = GTAOPass.OUTPUT.Default; ao.blendIntensity = 0.85;
  ao.updateGtaoMaterial({radius: 0.35, distanceExponent: 1.4, thickness: 1.2, scale: 1.0, samples: 12});
  ao.updatePdMaterial({lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, rings: 2, samples: 12});
  const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.35, 0.6, 0.85);
  const bokeh = new BokehPass(new THREE.Scene(), new THREE.PerspectiveCamera(), {focus: 2.0, aperture: 0.002, maxblur: 0.006});
  const out = new OutputPass();
  const film = new ShaderPass(FilmShader);
  composer.addPass(rp); composer.addPass(ao); composer.addPass(bloom); composer.addPass(bokeh); composer.addPass(out); composer.addPass(film);
  return {
    composer, ao, bloom, bokeh, film,
    // o: {ao, bloom:[strength,radius,threshold], dof:{focus,aperture,maxblur}|null, grain, vig}
    render(scene, camera, T, o = {}) {
      rp.scene = scene; rp.camera = camera; ao.scene = scene; ao.camera = camera; bokeh.scene = scene; bokeh.camera = camera;
      ao.enabled = o.ao !== false; ao.blendIntensity = o.aoAmount ?? 0.85;
      const b = o.bloom || [0.35, 0.6, 0.85]; bloom.strength = b[0]; bloom.radius = b[1]; bloom.threshold = b[2];
      bokeh.enabled = !!o.dof;
      if (o.dof) { bokeh.uniforms.focus.value = o.dof.focus; bokeh.uniforms.aperture.value = o.dof.aperture ?? 0.002; bokeh.uniforms.maxblur.value = o.dof.maxblur ?? 0.006; }
      film.uniforms.time.value = T; film.uniforms.grain.value = o.grain ?? 0.05; film.uniforms.vig.value = o.vig ?? 0.32; film.uniforms.ca.value = o.ca ?? 0.0018;
      composer.render();
    },
  };
}
