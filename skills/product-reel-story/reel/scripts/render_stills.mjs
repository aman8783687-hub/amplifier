import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const frames = process.argv.slice(2).map(Number);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "DiwaliSareeReel" });

for (const frame of frames) {
  await renderStill({
    composition,
    serveUrl,
    output: `out/stills/f${String(frame).padStart(4, "0")}.png`,
    frame,
    scale: 1,
  });
  console.log("rendered", frame);
}
