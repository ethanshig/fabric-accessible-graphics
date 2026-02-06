#!/usr/bin/env bun
/**
 * TactileConvert.ts - TypeScript wrapper for tactile-core CLI
 *
 * Converts images to tactile-ready PDFs for PIAF printing.
 * This tool wraps the `tactile` CLI from the tactile-core Python library.
 *
 * Usage:
 *   bun run src/tools/TactileConvert.ts IMAGE_PATH [OPTIONS]
 *
 * Examples:
 *   bun run src/tools/TactileConvert.ts floor-plan.jpg
 *   bun run src/tools/TactileConvert.ts sketch.png --preset sketch
 *   bun run src/tools/TactileConvert.ts plan.jpg --detect-text --braille-grade 2
 */

import { $ } from "bun";
import { existsSync } from "fs";
import { resolve, basename, dirname, join } from "path";

interface ConvertOptions {
  output?: string;
  preset?: string;
  threshold?: number;
  paperSize?: "letter" | "tabloid";
  detectText?: boolean;
  brailleGrade?: 1 | 2;
  autoReduceDensity?: boolean;
  enableTiling?: boolean;
  zoomRegion?: string;
  verbose?: boolean;
}

function parseArgs(args: string[]): { imagePath: string; options: ConvertOptions } {
  const options: ConvertOptions = {};
  let imagePath = "";

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (!arg.startsWith("-") && !imagePath) {
      imagePath = arg;
      continue;
    }

    switch (arg) {
      case "-o":
      case "--output":
        options.output = args[++i];
        break;
      case "--preset":
        options.preset = args[++i];
        break;
      case "-t":
      case "--threshold":
        options.threshold = parseInt(args[++i], 10);
        break;
      case "-p":
      case "--paper-size":
        options.paperSize = args[++i] as "letter" | "tabloid";
        break;
      case "--detect-text":
        options.detectText = true;
        break;
      case "--braille-grade":
        options.brailleGrade = parseInt(args[++i], 10) as 1 | 2;
        break;
      case "--auto-reduce-density":
        options.autoReduceDensity = true;
        break;
      case "--enable-tiling":
        options.enableTiling = true;
        break;
      case "--zoom-region":
        options.zoomRegion = args[++i];
        break;
      case "-v":
      case "--verbose":
        options.verbose = true;
        break;
      case "-h":
      case "--help":
        printHelp();
        process.exit(0);
    }
  }

  return { imagePath, options };
}

function printHelp(): void {
  console.log(`
TactileConvert - Convert images to tactile-ready PDFs

Usage:
  bun run TactileConvert.ts IMAGE_PATH [OPTIONS]

Options:
  -o, --output PATH          Output PDF path
  --preset NAME              Use preset (floor_plan, sketch, section, etc.)
  -t, --threshold INT        Black/white threshold 0-255 (default: 128)
  -p, --paper-size SIZE      Paper size: letter or tabloid
  --detect-text              Enable OCR text detection
  --braille-grade 1|2        Braille grade (2 = contracted)
  --auto-reduce-density      Auto-fix high density images
  --enable-tiling            Split oversized images
  --zoom-region X,Y,W,H      Crop to region (percentages)
  -v, --verbose              Show detailed progress
  -h, --help                 Show this help

Examples:
  bun run TactileConvert.ts floor-plan.jpg
  bun run TactileConvert.ts sketch.png --preset sketch --verbose
  bun run TactileConvert.ts plan.jpg --detect-text --braille-grade 2

Available Presets:
  floor_plan, section, elevation, site_plan, sketch,
  diagram, technical_drawing, photograph, presentation, detail_drawing
`);
}

function buildCommand(imagePath: string, options: ConvertOptions): string[] {
  const cmd: string[] = ["tactile", "image-to-piaf", imagePath];

  if (options.output) {
    cmd.push("--output", options.output);
  }
  if (options.preset) {
    cmd.push("--preset", options.preset);
  }
  if (options.threshold !== undefined) {
    cmd.push("--threshold", options.threshold.toString());
  }
  if (options.paperSize) {
    cmd.push("--paper-size", options.paperSize);
  }
  if (options.detectText) {
    cmd.push("--detect-text");
  }
  if (options.brailleGrade) {
    cmd.push("--braille-grade", options.brailleGrade.toString());
  }
  if (options.autoReduceDensity) {
    cmd.push("--auto-reduce-density");
  }
  if (options.enableTiling) {
    cmd.push("--enable-tiling");
  }
  if (options.zoomRegion) {
    cmd.push("--zoom-region", options.zoomRegion);
  }
  if (options.verbose) {
    cmd.push("--verbose");
  }

  return cmd;
}

async function convert(imagePath: string, options: ConvertOptions): Promise<void> {
  // Resolve and validate image path
  const resolvedPath = resolve(imagePath);

  if (!existsSync(resolvedPath)) {
    console.error(`Error: Image file not found: ${resolvedPath}`);
    process.exit(1);
  }

  const cmd = buildCommand(resolvedPath, options);

  if (options.verbose) {
    console.log(`Running: ${cmd.join(" ")}`);
    console.log("");
  }

  try {
    // Execute the tactile CLI
    const result = await $`${cmd}`.text();
    console.log(result);

    // Determine output path for summary
    const outputPath = options.output ||
      join(dirname(resolvedPath), `${basename(resolvedPath, "." + resolvedPath.split(".").pop())}_piaf.pdf`);

    if (existsSync(outputPath)) {
      console.log(`\nOutput: ${outputPath}`);
    }
  } catch (error: any) {
    console.error(`Conversion failed: ${error.message || error}`);

    // Provide helpful suggestions
    if (error.message?.includes("density")) {
      console.log("\nTip: Try adding --auto-reduce-density to fix high density");
    }
    if (error.message?.includes("tesseract")) {
      console.log("\nTip: Install Tesseract OCR or remove --detect-text");
    }

    process.exit(1);
  }
}

// Main execution
const args = process.argv.slice(2);

if (args.length === 0) {
  printHelp();
  process.exit(1);
}

const { imagePath, options } = parseArgs(args);

if (!imagePath) {
  console.error("Error: No image path provided");
  printHelp();
  process.exit(1);
}

await convert(imagePath, options);
