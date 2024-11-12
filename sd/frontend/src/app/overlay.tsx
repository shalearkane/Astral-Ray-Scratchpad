import { Vector2d } from "konva/lib/types";
import { useEffect, useState } from "react";
import { Coordinate } from "../types/coord";
import { getCoordinatesFromVector2d } from "../lib/utils";
import Slider from "react-input-slider";
import { INITIAL_SCALING_FACTOR } from "./app";

function Overlay({
  pointerPos,
  imageWidth,
  imageHeight,
  scale,
  setScale,
}: {
  pointerPos: Vector2d;
  scale: number;
  setScale: (scale: number) => void;
  imageWidth?: number;
  imageHeight?: number;
}) {
  const [hoveredCoordinate, setHoveredCoordinate] = useState<Coordinate>();

  useEffect(() => {
    if (!imageWidth || !imageHeight) return;
    setHoveredCoordinate(
      getCoordinatesFromVector2d(pointerPos, imageHeight, imageWidth),
    );
  }, [pointerPos, imageHeight, imageWidth]);
  return (
    <div>
      {/* {hoveredCoordinate &&
        hoveredCoordinate.lat <= 80 &&
        hoveredCoordinate.lat >= -80 &&
        hoveredCoordinate.lon <= 180 &&
        hoveredCoordinate.lon >= -180 && ( */}
      <div
        className="fixed text-white bottom-0 right-0 m-5 bg-black px-5 py-2"
        style={{
          bottom: "0px",
        }}
      >
        LAT: {hoveredCoordinate?.lat.toPrecision(4)} | LON:{" "}
        {hoveredCoordinate?.lon.toPrecision(4)}
      </div>
      {/* )} */}

      <div className="fixed top-[30%] m-5 bg-black gap-5 px-5 py-5 text-white rounded-md flex flex-col justify-center">
        <div
          className="cursor-pointer"
          onClick={() => setScale(Math.min(scale + 0.1, 1))}
        >
          +
        </div>
        <Slider
          y={scale}
          axis="y"
          yreverse
          ymin={0.5}
          ymax={1}
          ystep={0.01}
          onChange={({ y }) => {
            console.log(y);
            setScale(y);
          }}
        />
        <div
          className="cursor-pointer"
          onClick={() => setScale(Math.max(scale - 0.1, 0.5))}
        >
          -
        </div>
      </div>
    </div>
  );
}

export default Overlay;
