// Fischauge-Kamera: rendert die Welt in eine Cubemap und verzerrt sie dann
// (equisolid-Projektion) auf das Hochformat-Bild – wie eine 360°-Actioncam.
import * as THREE from 'three';

export class FisheyeCamera {
  constructor(renderer, { size = 1536, fov = 150 } = {}) {
    this.renderer = renderer;
    this.rt = new THREE.WebGLCubeRenderTarget(size, { generateMipmaps: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
    this.rt.texture.colorSpace = THREE.SRGBColorSpace;
    this.cube = new THREE.CubeCamera(0.03, 3000, this.rt);
    this.cube.coordinateSystem = renderer.coordinateSystem; this.cube.updateCoordinateSystem();
    this.yaw = 0; this.pitch = 0; this.roll = 0; this.fov = fov;
    const W = renderer.domElement.width, H = renderer.domElement.height;
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
      uniforms: {
        uCube: { value: this.rt.texture }, uRot: { value: new THREE.Matrix3() },
        uAspect: { value: W / H }, uK: { value: 0 }, uPx: { value: 1 / H }, uTime: { value: 0 }, uGrain: { value: 0.012 },
      },
      vertexShader: `varying vec2 vP; void main(){ vP = position.xy; gl_Position = vec4(position.xy,0.0,1.0); }`,
      fragmentShader: `
        uniform samplerCube uCube; uniform mat3 uRot; uniform float uAspect, uK, uPx, uTime, uGrain;
        varying vec2 vP;
        vec3 dirFor(vec2 p){
          float r = length(p);
          float th = 2.0 * asin(clamp(r * uK, 0.0, 1.0));
          vec2 d2 = r > 1e-6 ? p / r : vec2(0.0);
          vec3 d = vec3(d2 * sin(th), -cos(th));
          return uRot * d;
        }
        float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))) * 43758.5453); }
        void main(){
          vec2 p = vec2(vP.x * uAspect, vP.y);
          // 4-fach Supersampling gegen Treppenkanten
          vec3 c = vec3(0.0);
          c += textureCube(uCube, dirFor(p + vec2(-0.25, 0.75) * uPx)).rgb;
          c += textureCube(uCube, dirFor(p + vec2(0.75, 0.25) * uPx)).rgb;
          c += textureCube(uCube, dirFor(p + vec2(0.25, -0.75) * uPx)).rgb;
          c += textureCube(uCube, dirFor(p + vec2(-0.75, -0.25) * uPx)).rgb;
          c *= 0.25;
          // leichtes Papierkorn
          c += (hash(gl_FragCoord.xy + uTime) - 0.5) * uGrain;
          gl_FragColor = vec4(c, 1.0);
          #include <colorspace_fragment>
        }`,
      depthTest: false, depthWrite: false,
    }));
    this.quad.frustumCulled = false;
    this.post = new THREE.Scene(); this.post.add(this.quad);
    this.orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this._e = new THREE.Euler(); this._m = new THREE.Matrix4(); this._fwd = new THREE.Vector3(); this._d = new THREE.Vector3();
  }
  render(scene, pos, t = 0) {
    const r = this.renderer;
    this._e.set(this.pitch, this.yaw, this.roll, 'YXZ');
    this._m.makeRotationFromEuler(this._e);
    this.quad.material.uniforms.uRot.value.setFromMatrix4(this._m);
    // Bildhöhe (halbe Höhe = 1) entspricht fov/2 Abweichung von der Blickrichtung
    this.quad.material.uniforms.uK.value = Math.sin(THREE.MathUtils.degToRad(this.fov) / 4);
    this.quad.material.uniforms.uTime.value = t;
    this._fwd.set(0, 0, -1).applyMatrix4(this._m);
    // Cubemap rendern – Seiten, die garantiert nicht im Bild sind, überspringen
    this.cube.position.copy(pos); this.cube.updateMatrixWorld(true);
    const prevRT = r.getRenderTarget();
    r.shadowMap.needsUpdate = true;
    this.cube.children.forEach((cam, i) => {
      cam.getWorldDirection(this._d);
      if (this._d.dot(this._fwd) < -0.86) return; // gegenüberliegende Seite
      r.setRenderTarget(this.rt, i);
      r.render(scene, cam);
    });
    r.setRenderTarget(prevRT);
    r.render(this.post, this.orthoCam);
  }
}
