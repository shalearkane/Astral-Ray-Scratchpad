
export interface Coordinate {
  lat: number;
  lon: number;
}


export interface Patch {
  boundingBox: Coordinate[];
  color: string;
}