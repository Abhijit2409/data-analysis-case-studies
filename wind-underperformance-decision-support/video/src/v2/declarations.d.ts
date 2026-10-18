// Screen captures are imported directly so every v2 asset lives under src/v2/.
declare module '*.png' {
  const src: string;
  export default src;
}
