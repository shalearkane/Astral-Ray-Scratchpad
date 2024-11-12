import { useLoader } from "@react-three/fiber";
// @ts-expect-error as no ts declarations
import { TextureLoader } from "three/src/loaders/TextureLoader";

export function MoonModel(props: any) {
  const colorMap = useLoader(TextureLoader, "/moon_texture.jpg");

  return (
    <group {...props} dispose={null}>
      <mesh>
        <sphereGeometry args={[4, 60, 60]} />
        <meshStandardMaterial map={colorMap} />
      </mesh>
    </group>
  );
}
