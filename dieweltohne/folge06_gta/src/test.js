import * as THREE from 'three';
import {makeHuman} from './mh.js';
import {stand} from './poses.js';
export async function build(renderer) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#202428');
  const cam = new THREE.PerspectiveCamera(30, 1080 / 1920, 0.05, 50);
  const h = await makeHuman(window.FIG || 'guy', {top: '#ff0000', bottom: '#00ff00', shoe: '#0000ff', sneakers: '#eee', hair: '#222', skin: 'brown'});
  scene.add(h.root);
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(10, 10), new THREE.MeshStandardMaterial({color: '#777'})); fl.rotation.x = -Math.PI / 2; fl.receiveShadow = true; scene.add(fl);
  const key = new THREE.DirectionalLight('#fff', 2.5); key.position.set(2, 3, 3); key.castShadow = true; scene.add(key);
  scene.add(new THREE.HemisphereLight('#bcd', '#432', 0.8));
  window.H = h; window.THREE = THREE;
  return {scene, camera: cam, update(shot, T) {
    const v = window.VIEW || [0, 1.0, 3.2, 0, 0.9, 0];
    cam.position.set(v[0], v[1], v[2]); cam.lookAt(v[3], v[4], v[5]); cam.fov = v[6] || 30; cam.updateProjectionMatrix();
    if (window.POSEF) window.POSEF(h); else stand(h, {});
    return Object.assign({dof: null}, window.POST || {});
  }};
}
