// makefun-news-20261124: copy the rendered front page to the output dir.
//
// The entry image is drawn ahead of time by render.py and shipped in this
// repository as entry.png. This program only validates it and copies it to
// $MAKEFUN_OUTPUT_DIR (default /output) as entry.png, so both grader runs
// write identical bytes. Node standard library only, no network.

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;
const MAX_SIDE = 1024;

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const bytes = readFileSync(sourcePath);

if (bytes.length < 8 || bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes, outside the 1 MiB cap`);
}
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}
// PNG IHDR: width at bytes 16-19, height at bytes 20-23, big-endian.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > MAX_SIDE || height > MAX_SIDE) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(sourcePath, join(outDir, "entry.png"));
console.log(`wrote ${join(outDir, "entry.png")} (${bytes.length} bytes, ${width}x${height})`);
