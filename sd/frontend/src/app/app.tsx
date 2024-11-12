import { Stage, Layer, Image, Shape } from "react-konva";
import useImage from "use-image";
import { ReactNode, useEffect, useRef, useState } from "react";
import Konva from "konva";
import Overlay from "./overlay";
import { Vector2d } from "konva/lib/types";
import { Canvas } from "@react-three/fiber";
import CanvasComponent from "./canvas";
import { Coordinate, Patch } from "../types/coord";
import { getVector2dFromCoordinate } from "../lib/utils";

export const INITIAL_SCALING_FACTOR = 1;

const dummy: Patch[] = [
  // {
  //   boundingBox: [
  //     {
  //       lat: 5,
  //       lon: 50,
  //     },
  //     {
  //       lat: 5,
  //       lon: 60,
  //     },
  //     {
  //       lat: 60,
  //       lon: 60,
  //     },
  //     {
  //       lat: 60,
  //       lon: 5,
  //     },
  //   ],
  //   color: "#00D2FF",
  // },
];

function App() {
  const [image] = useImage("moon.png");
  const [testImage] = useImage("test.png");
  const imageRef = useRef<Konva.Image>(null);
  const stageRef = useRef<Konva.Stage>(null);
  const overlayLayerRef = useRef<Konva.Layer>(null);
  const [pointerPosition, setPointerPosition] = useState<Vector2d>({
    x: 0,
    y: 0,
  });
  const [imageWidth, setImageWidth] = useState<number | undefined>();
  const [imageHeight, setImageHeight] = useState<number | undefined>();
  const [scalingFactor, setScalingFactor] = useState<number>(
    INITIAL_SCALING_FACTOR,
  );

  console.log(image?.height, image?.width);

  const handleDragMove = (evt: Konva.KonvaEventObject<DragEvent>) => {
    handleBoundingBox(evt);
  };

  const handleBoundingBox = (evt: Konva.KonvaEventObject<DragEvent>) => {
    if (!stageRef.current || !imageRef.current) return;
    const stageWidth = window.innerWidth;
    const stageHeight = window.innerHeight;
    const imageScaleX = imageRef.current.scaleX();
    const imageScaleY = imageRef.current.scaleY();
    const imageWidth = imageRef.current.getWidth() * imageScaleX;
    const imageHeight = imageRef.current.getHeight() * imageScaleY;
    const absPos = {
      x: evt.evt.clientX,
      y: evt.evt.clientY,
    };

    const left = absPos.x;
    const right = stageWidth - absPos.x;
    const top = absPos.y;
    const bottom = stageHeight - absPos.y;

    const relPos = imageRef.current.getRelativePointerPosition() ?? {
      x: 0,
      y: 0,
    };

    relPos.x *= scalingFactor;
    relPos.y *= scalingFactor;

    let newPos = stageRef.current?.position() ?? {
      x: 0,
      y: 0,
    };

    if (stageWidth < imageWidth) {
      if (relPos.x - left < 0) newPos.x -= left - relPos.x;
      if (relPos.x + right > imageWidth)
        newPos.x += relPos.x + right - imageWidth;
    }
    if (stageHeight < imageHeight) {
      if (relPos.y - top < 0) newPos.y -= top - relPos.y;
      if (relPos.y + bottom > imageHeight)
        newPos.y += relPos.y + bottom - imageHeight;
    }

    stageRef.current.position(newPos);
  };

  const handleMousePointerMove = () => {
    if (!imageRef.current) return;

    const width = imageRef.current.width();
    const height = imageRef.current.height();
    if (imageWidth != width) setImageWidth(width);
    if (imageHeight != height) setImageHeight(height);
    const relPos = imageRef.current?.getRelativePointerPosition() ?? {
      x: 0,
      y: 0,
    };

    setPointerPosition({
      x: relPos.x,
      y: relPos.y,
    });
  };

  // const paintPatch = (patch: Patch) => {
  //   const layer = new Konva.Layer();
  //   const patchShape = new Konva.Shape({
  //     id: JSON.stringify(patch),
  //     sceneFunc: (context, shape) => {
  //       const width = shape.width();
  //       const height = shape.height();
  //       const boundingBox: Vector2d[] = [];
  //       context.beginPath();

  //       patch.boundingBox.forEach((coord, coordIdx) => {
  //         const points = getVector2dFromCoordinate(
  //           coord,
  //           imageHeight ?? 0,
  //           imageWidth ?? 0,
  //         );
  //         boundingBox.push({
  //           x: Math.abs(points.x),
  //           y: Math.abs(points.y),
  //         });
  //       });
  //       context.moveTo(boundingBox[0].x, boundingBox[0].y);

  //       for (let i = 0; i < boundingBox.length; i++) {
  //         context.lineTo(
  //           boundingBox[(i + 1) % 4].x,
  //           boundingBox[(i + 1) % 4].y,
  //         );
  //       }
  //       context.lineTo(width - 40, height - 90);
  //       context.closePath();

  //       // (!) Konva specific method, it is very important
  //       context.fillStrokeShape(shape);
  //       console.log("HELLO");
  //     },
  //     fill: patch.color,
  //     stroke: "black",
  //     strokeWidth: 4,
  //   });
  //   console.log(stageRef.current);
  //   layer.add(patchShape);
  //   stageRef.current?.add(layer).draw();
  //   layer.draw();
  //   stageRef.current?.batchDraw();
  // };

  // useEffect(() => {
  //   if (!overlayLayerRef.current) return;
  //   paintPatch(dummy[0]);
  // }, [dummy, overlayLayerRef]);

  useEffect(() => {
    // TODO: Try to replace this
    stageRef.current?.batchDraw();
  });

  return (
    <main>
      {/* <Canvas
        style={{
          width: "100vw",
          height: "100vh",
        }}
      >
        <CanvasComponent />
      </Canvas> */}
      <div
        className="absolute"
        style={{
          zIndex: 20,
        }}
      >
        <Overlay
          pointerPos={pointerPosition}
          imageHeight={imageHeight}
          imageWidth={imageWidth}
          scale={scalingFactor}
          setScale={(scale) => setScalingFactor(scale)}
        />
      </div>
      <div
        className="w-[100vw] absolute"
        style={{
          zIndex: 1,
          margin: 0,
        }}
      >
        <Stage
          ref={stageRef}
          width={window.innerWidth}
          height={window.innerHeight}
          onDragMove={handleDragMove}
          onMouseMove={handleMousePointerMove}
          draggable
        >
          <Layer>
            <Image
              // draggable
              ref={imageRef}
              image={image}
              scaleY={scalingFactor}
              scaleX={scalingFactor}
            />
            <Image
              // draggable
              image={testImage}
              width={imageWidth}
              height={imageHeight}
              opacity={0.5}
              scaleX={scalingFactor}
              scaleY={scalingFactor}
            />

            {dummy.map((patch: Patch, patchIdx: number) => (
              <Shape
                key={`Shape_${patchIdx}`}
                width={260}
                height={170}
                sceneFunc={function (context, shape) {
                  const width = shape.width();
                  const height = shape.height();
                  const boundingBox: Vector2d[] = [];
                  context.beginPath();

                  patch.boundingBox.forEach((coord, coordIdx) => {
                    const points = getVector2dFromCoordinate(
                      coord,
                      imageHeight ?? 0,
                      imageWidth ?? 0,
                    );
                    boundingBox.push({
                      x: Math.abs(points.x),
                      y: Math.abs(points.y),
                    });
                  });
                  context.moveTo(boundingBox[0].x, boundingBox[0].y);

                  for (let i = 0; i < boundingBox.length; i++) {
                    context.lineTo(
                      boundingBox[(i + 1) % 4].x,
                      boundingBox[(i + 1) % 4].y,
                    );
                  }
                  context.lineTo(width - 40, height - 90);
                  context.closePath();

                  // (!) Konva specific method, it is very important
                  context.fillStrokeShape(shape);
                }}
                fill={patch.color}
              />
            ))}
          </Layer>
          <Layer ref={overlayLayerRef}></Layer>
        </Stage>
      </div>
    </main>
  );
}

export default App;
