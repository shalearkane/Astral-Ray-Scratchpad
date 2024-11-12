import {
  ArcballControls,
  CameraControls,
  DragControls,
  FaceControls,
  OrbitControls,
  OrthographicCamera,
  PivotControls,
} from "@react-three/drei";
import { RootState, useFrame } from "@react-three/fiber";
import { _XRFrame } from "@react-three/fiber/dist/declarations/src/core/utils";
import { MoonModel } from "components/moon/Moon";

function Canvas() {
  useFrame((state: RootState, delta: number, xrFrame: _XRFrame) => {
    const { x, y, z } = state.camera.position;
    const threshold = 2;
    let new_x = x;
    let new_y = y;
    let new_z = z;
    // This function runs at the native refresh rate inside of a shared render-loop
    if (state.camera.position.x < threshold) new_x = threshold;
    if (state.camera.position.y < threshold) new_y = threshold;
    if (state.camera.position.z < threshold) new_z = threshold;

    if (new_x != x || new_y != y || new_z != z) {
      state.camera.position.set(new_x, new_y, new_z);
    }
  });
  return (
    <>
      <PivotControls anchor={[0, 0, 0]}>
        <ambientLight intensity={0.5} />
        <OrthographicCamera position={[0, 0, 0]}>
          <MoonModel />
        </OrthographicCamera>
      </PivotControls>
    </>
  );
}

export default Canvas;
